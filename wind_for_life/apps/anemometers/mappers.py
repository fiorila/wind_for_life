"""Mappers for transforming domain models to export representations.

Following DDD principles, mappers handle the translation between
domain objects and external representations without polluting the domain model.
"""

from wind_for_life.apps.anemometers.models import Anemometer, Reading


class AnemometerExportMapper:
    """Maps Anemometer domain objects to export dictionaries."""

    @staticmethod
    def to_dict(anemometer: Anemometer) -> dict[str, str]:
        """Transform an Anemometer to its export representation.

        Args:
            anemometer: Domain object to transform.

        Returns:
            Dictionary with anemometer data for exports.
        """
        return {
            "anemometer_id": str(anemometer.id),
            "anemometer_name": anemometer.name,
        }


class ReadingExportMapper:
    """Maps Reading domain objects to export dictionaries."""

    @staticmethod
    def to_dict(reading: Reading) -> dict[str, str | float]:
        """Transform a Reading to its export representation.

        Args:
            reading: Domain object to transform.

        Returns:
            Dictionary with reading data including anemometer details.
        """
        return {
            "id": str(reading.id),
            "speed": reading.speed,
            "recorded_at": reading.recorded_at.isoformat(),
            **AnemometerExportMapper.to_dict(reading.anemometer),
        }
