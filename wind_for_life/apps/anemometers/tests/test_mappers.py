"""Tests for domain mappers.

Tests the transformation logic from domain models to export representations.
Following DDD, these are application layer tests separate from infrastructure.
"""

import pytest

from wind_for_life.apps.anemometers.mappers import (
    AnemometerExportMapper,
    ReadingExportMapper,
)
from wind_for_life.apps.anemometers.tests.factories import (
    AnemometerFactory,
    ReadingFactory,
)

# ---------------------------------
# ANEMOMETER EXPORT MAPPER TESTS
# ---------------------------------


@pytest.mark.django_db
def test_anemometer_export_mapper_basic_fields():
    """Test AnemometerExportMapper transforms basic fields correctly."""
    anemometer = AnemometerFactory(name="Test Anemometer")
    result = AnemometerExportMapper.to_dict(anemometer)

    assert result["anemometer_id"] == str(anemometer.id)
    assert result["anemometer_name"] == "Test Anemometer"


@pytest.mark.django_db
def test_anemometer_export_mapper_returns_dict():
    """Test AnemometerExportMapper returns a dictionary."""
    anemometer = AnemometerFactory()
    result = AnemometerExportMapper.to_dict(anemometer)

    assert isinstance(result, dict)
    assert "anemometer_id" in result
    assert "anemometer_name" in result


@pytest.mark.django_db
def test_anemometer_export_mapper_id_is_string():
    """Test AnemometerExportMapper converts UUID to string."""
    anemometer = AnemometerFactory()
    result = AnemometerExportMapper.to_dict(anemometer)

    assert isinstance(result["anemometer_id"], str)


# ------------------------------
# READING EXPORT MAPPER TESTS
# ------------------------------


@pytest.mark.django_db
def test_reading_export_mapper_all_fields():
    """Test ReadingExportMapper transforms all fields correctly."""
    anemometer = AnemometerFactory(name="Test Anemometer")
    reading = ReadingFactory(speed=15.5, anemometer=anemometer)

    result = ReadingExportMapper.to_dict(reading)

    # Check all required fields are present and have correct values
    assert result["id"] == str(reading.id)
    assert result["speed"] == 15.5  # noqa: PLR2004
    assert "recorded_at" in result
    assert result["anemometer_id"] == str(reading.anemometer.id)
    assert result["anemometer_name"] == "Test Anemometer"


@pytest.mark.django_db
def test_reading_export_mapper_includes_anemometer_details():
    """Test ReadingExportMapper includes anemometer data via composition."""
    anemometer = AnemometerFactory(name="Wind Station Alpha")
    reading = ReadingFactory(anemometer=anemometer)
    result = ReadingExportMapper.to_dict(reading)

    assert result["anemometer_id"] == str(anemometer.id)
    assert result["anemometer_name"] == "Wind Station Alpha"


@pytest.mark.django_db
def test_reading_export_mapper_recorded_at_is_iso_format():
    """Test ReadingExportMapper formats timestamp as ISO string."""
    reading = ReadingFactory()
    result = ReadingExportMapper.to_dict(reading)

    assert isinstance(result["recorded_at"], str)
    assert "T" in result["recorded_at"]  # ISO format includes T separator


@pytest.mark.django_db
def test_reading_export_mapper_returns_dict():
    """Test ReadingExportMapper returns a dictionary."""
    reading = ReadingFactory()
    result = ReadingExportMapper.to_dict(reading)

    assert isinstance(result, dict)


@pytest.mark.django_db
def test_reading_export_mapper_id_types():
    """Test ReadingExportMapper converts UUIDs to strings."""
    reading = ReadingFactory()
    result = ReadingExportMapper.to_dict(reading)

    assert isinstance(result["id"], str)
    assert isinstance(result["anemometer_id"], str)
