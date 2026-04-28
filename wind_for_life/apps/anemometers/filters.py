from django_filters import rest_framework as filters

from wind_for_life.apps.anemometers.models import Reading


class ReadingFilterSet(filters.FilterSet):
    date_from = filters.DateTimeFilter(
        field_name="recorded_at",
        lookup_expr="gte",
        label="Filter readings recorded on or after this date (ISO format)",
    )
    date_to = filters.DateTimeFilter(
        field_name="recorded_at",
        lookup_expr="lte",
        label="Filter readings recorded on or before this date (ISO format)",
    )

    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["anemometer", "date_from", "date_to"]
