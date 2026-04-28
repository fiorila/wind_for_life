"""Tests for API views (presentation layer).

Tests HTTP endpoints, request/response handling, authentication, etc.
These are integration tests that test the full HTTP request/response cycle.
"""

import csv
import io
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from wind_for_life.apps.anemometers.tests.factories import ReadingFactory
from wind_for_life.apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")  # noqa: S106


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


# -----------------------
# EXPORT ENDPOINT TESTS
# -----------------------


@pytest.mark.django_db
def test_export_readings_as_json(auth_client):
    """Test JSON export API endpoint."""
    reading = ReadingFactory()
    url = reverse("api:readings-export")
    response = auth_client.get(url, {"export_format": "json"})

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Disposition"] == 'attachment; filename="readings.json"'
    assert len(response.data) >= 1

    matching_reading = next(item for item in response.data if item["id"] == str(reading.pk))
    assert matching_reading["anemometer_id"] == str(reading.anemometer.pk)
    assert matching_reading["anemometer_name"] == reading.anemometer.name


@pytest.mark.django_db
def test_export_readings_as_csv(auth_client):
    """Test CSV export API endpoint."""
    reading = ReadingFactory()
    url = reverse("api:readings-export")
    response = auth_client.get(url, {"export_format": "csv"})

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Disposition"] == 'attachment; filename="readings.csv"'
    assert response["Content-Type"] == "text/csv"

    rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8"))))

    assert len(rows) >= 1
    assert any(row["id"] == str(reading.pk) for row in rows)


@pytest.mark.django_db
def test_export_readings_invalid_format(auth_client):
    """Test export endpoint rejects invalid format."""
    url = reverse("api:readings-export")
    response = auth_client.get(url, {"export_format": "xml"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "format" in response.data


@pytest.mark.django_db
def test_export_readings_default_format_is_json(auth_client):
    """Test export endpoint defaults to JSON when format not specified."""
    ReadingFactory()
    url = reverse("api:readings-export")
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Disposition"] == 'attachment; filename="readings.json"'


@pytest.mark.django_db
def test_export_requires_authentication(api_client):
    """Test export endpoint requires authentication."""
    url = reverse("api:readings-export")
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ----------------------------
# DATE FILTERING TESTS
# ----------------------------


@pytest.mark.django_db
def test_export_with_date_from_filter(auth_client):
    """Test export filters readings from a start date."""
    current_time = now()
    old_reading = ReadingFactory(recorded_at=current_time - timedelta(days=10))
    recent_reading = ReadingFactory(recorded_at=current_time - timedelta(days=1))
    
    url = reverse("api:readings-export")
    date_from = (current_time - timedelta(days=5)).isoformat()
    response = auth_client.get(url, {"export_format": "json", "date_from": date_from})
    
    assert response.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in response.data]
    assert str(recent_reading.pk) in ids
    assert str(old_reading.pk) not in ids


@pytest.mark.django_db
def test_export_with_date_to_filter(auth_client):
    """Test export filters readings up to an end date."""
    current_time = now()
    old_reading = ReadingFactory(recorded_at=current_time - timedelta(days=10))
    recent_reading = ReadingFactory(recorded_at=current_time - timedelta(days=1))
    
    url = reverse("api:readings-export")
    date_to = (current_time - timedelta(days=5)).isoformat()
    response = auth_client.get(url, {"export_format": "json", "date_to": date_to})
    
    assert response.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in response.data]
    assert str(old_reading.pk) in ids
    assert str(recent_reading.pk) not in ids


@pytest.mark.django_db
def test_export_with_date_range(auth_client):
    """Test export with both date_from and date_to filters."""
    current_time = now()
    too_old = ReadingFactory(recorded_at=current_time - timedelta(days=20))
    in_range = ReadingFactory(recorded_at=current_time - timedelta(days=10))
    too_recent = ReadingFactory(recorded_at=current_time - timedelta(days=1))
    
    url = reverse("api:readings-export")
    date_from = (current_time - timedelta(days=15)).isoformat()
    date_to = (current_time - timedelta(days=5)).isoformat()
    
    response = auth_client.get(url, {"export_format": "json", "date_from": date_from, "date_to": date_to})
    
    assert response.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in response.data]
    assert str(in_range.pk) in ids
    assert str(too_old.pk) not in ids
    assert str(too_recent.pk) not in ids


@pytest.mark.django_db
def test_export_csv_with_date_filter(auth_client):
    """Test CSV export respects date filtering."""
    current_time = now()
    old_reading = ReadingFactory(recorded_at=current_time - timedelta(days=10))
    recent_reading = ReadingFactory(recorded_at=current_time - timedelta(days=1))
    
    url = reverse("api:readings-export")
    date_from = (current_time - timedelta(days=5)).isoformat()
    response = auth_client.get(url, {"export_format": "csv", "date_from": date_from})
    
    assert response.status_code == status.HTTP_200_OK
    rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8"))))
    ids = [row["id"] for row in rows]
    
    assert str(recent_reading.pk) in ids
    assert str(old_reading.pk) not in ids
