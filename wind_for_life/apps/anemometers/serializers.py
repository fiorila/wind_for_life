from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from wind_for_life.apps.anemometers.models import Anemometer, Reading


# Model specific
class AnemometerMinimalSerializer(serializers.ModelSerializer):
    """Excludes all foreign keys data"""

    class Meta:  # type: ignore  # noqa: PGH003
        model = Anemometer
        fields = ["id", "name", "longitude", "latitude"]
        read_only_fields = ["id"]


class ReadingMinimalSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Excludes all foreign keys data"""

    tags = TagListSerializerField(
        required=False,
        help_text="A comma separated list of tags.",
    )

    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["id", "speed", "recorded_at", "tags"]
        read_only_fields = ["id"]


class ReadReadingMinimalSerializer(ReadingMinimalSerializer):
    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["id", "speed", "recorded_at", "tags"]
        read_only_fields = ["id"]


class WriteReadingMinimalSerializer(ReadingMinimalSerializer):
    anemometer = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Anemometer.objects.all(),
    )

    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["id", "speed", "recorded_at", "tags", "anemometer"]
        read_only_fields = ["id"]


class AnemometerDetailSerializer(AnemometerMinimalSerializer):
    """Complete detail of Anemometer"""

    readings = ReadingMinimalSerializer(many=True, read_only=True)

    class Meta:  # type: ignore  # noqa: PGH003
        model = Anemometer
        fields = ["id", "name", "longitude", "latitude", "readings"]
        read_only_fields = ["id"]


class ReadingDetailSerializer(ReadingMinimalSerializer):
    """Complete detail of Reading"""

    anemometer = AnemometerMinimalSerializer(many=False, read_only=False)

    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["id", "speed", "recorded_at", "tags", "anemometer"]
        read_only_fields = ["id"]


class ReadingExportSerializer(serializers.Serializer):
    """Serializer for reading exports.

    Transforms Reading instances into export-ready dictionaries
    with flattened anemometer data.
    """

    def to_representation(self, instance):
        """Transform Reading to export dictionary."""
        return {
            "id": str(instance.id),
            "speed": instance.speed,
            "recorded_at": instance.recorded_at.isoformat(),
            "anemometer_id": str(instance.anemometer.id),
            "anemometer_name": instance.anemometer.name,
        }
