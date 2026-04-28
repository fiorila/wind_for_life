"""Tests for export infrastructure layer.

Tests the data exporters (CSV/JSON rendering).
These are pure data transformation tests with NO HTTP concerns.
HTTP/API endpoint tests belong in test_views.py (presentation layer).
Mapper tests are in test_mappers.py (application layer tests).
"""

import csv
import io

from wind_for_life.apps.anemometers.exports import ReadingExporter

# -------------------
# EXPORTER TESTS
# -------------------


def test_reading_exporter_to_json():
    """Test ReadingExporter returns JSON-ready data unchanged."""
    data = [{"id": "123", "speed": 10.5}]
    exported_data = ReadingExporter.to_json(data)

    assert exported_data == data


def test_reading_exporter_to_csv():
    """Test ReadingExporter renders CSV content."""
    data = [
        {"id": "123", "speed": 10.5, "anemometer_id": "abc"},
        {"id": "456", "speed": 8.2, "anemometer_id": "def"},
    ]
    csv_content = ReadingExporter.to_csv(data)

    rows = list(csv.DictReader(io.StringIO(csv_content)))

    assert len(rows) == 2  # noqa: PLR2004
    assert rows[0]["id"] == "123"
    assert rows[0]["speed"] == "10.5"
    assert rows[1]["id"] == "456"


def test_reading_exporter_to_csv_empty():
    """Test CSV export handles empty data gracefully."""
    csv_content = ReadingExporter.to_csv([])

    assert csv_content == ""
