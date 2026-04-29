from django.db.models import Count
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
    tags_any = filters.CharFilter(
        method="filter_tags_any",
        label="Comma-separated tag list, any of these tags (OR)",
    )
    tags_exact = filters.CharFilter(
        method="filter_tags_exact",
        label="Comma-separated tag list, exactly of these tags (AND)",
    )

    def filter_tags_any(self, queryset, name, value):
        """Compares against an allowed list of tags (OR)"""
        tags = [tag.strip() for tag in value.split(",") if tag.strip()]
        return queryset.filter(tags__name__in=tags).distinct()

    def filter_tags_exact(self, queryset, name, value):
        """
        Compares against an exact list of tags (AND)
        """
        tags = [tag.strip() for tag in value.split(",") if tag.strip()]
        tag_count = len(tags)
        if tag_count == 0:
            return queryset.none()

        queryset = (
            queryset.annotate(num_tags=Count("tags", distinct=True))
            .filter(tags__name__in=tags)
            .filter(num_tags=tag_count)
            .distinct()
        )

        readings_with_exact_tags = [
            reading.pk
            for reading in queryset.prefetch_related("tags")
            if set(reading.tags.names()) == set(tags)
        ]

        return queryset.model.objects.filter(pk__in=readings_with_exact_tags)

    class Meta:  # type: ignore  # noqa: PGH003
        model = Reading
        fields = ["anemometer", "date_from", "date_to"]
