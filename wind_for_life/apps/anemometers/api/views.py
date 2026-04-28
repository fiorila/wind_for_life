from datetime import timedelta

from django.db.models import Avg
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.utils.timezone import now
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from wind_for_life.apps.anemometers.api.serializers import (
    RecentReadingsAnemometerSerializer,
)
from wind_for_life.apps.anemometers.exports import ReadingExporter
from wind_for_life.apps.anemometers.filters import ReadingFilterSet
from wind_for_life.apps.anemometers.models import Anemometer, Reading
from wind_for_life.apps.anemometers.serializers import (
    AnemometerDetailSerializer,
    AnemometerMinimalSerializer,
    ReadingDetailSerializer,
    ReadingExportSerializer,
    ReadingMinimalSerializer,
    ReadReadingMinimalSerializer,
    WriteReadingMinimalSerializer,
)
from wind_for_life.apps.base.mixins import ReadWriteSerializerMixin


class AnemometerViewSet(viewsets.ModelViewSet):
    """Anemometers API"""

    serializer_class = AnemometerMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Anemometer.objects.all()

    def retrieve(self, request, pk=None):
        """Detail anemometer shows readings values as well"""
        try:
            anemometer = Anemometer.objects.prefetch_related("readings").get(
                pk=pk,
            )
        except Anemometer.DoesNotExist as exc:
            raise NotFound from exc

        serializer = AnemometerDetailSerializer(anemometer)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
    )
    def recent_readings(self, request):
        """
        Anemometers with average daily & weekly speed as well as their 5 most
        recent readings.
        """
        _now = now()
        day_ago = _now - timedelta(days=1)
        week_ago = _now - timedelta(days=7)

        anemometers = Anemometer.objects.prefetch_related("readings").annotate(
            average_daily_speed=Avg(
                "readings__speed",
                filter=Q(readings__recorded_at__gte=day_ago),
            ),
            average_weekly_speed=Avg(
                "readings__speed",
                filter=Q(readings__recorded_at__gte=week_ago),
            ),
        )

        page = self.paginate_queryset(anemometers)
        if page is not None:
            serializer = RecentReadingsAnemometerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RecentReadingsAnemometerSerializer(anemometers, many=True)
        return Response(serializer.data)


class ReadingViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """Readings API"""

    queryset = Reading.objects.all()
    read_serializer_class = ReadReadingMinimalSerializer
    write_serializer_class = WriteReadingMinimalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ReadingFilterSet

    def get_queryset(self) -> QuerySet:
        return Reading.objects.select_related("anemometer")

    @action(detail=False, methods=["GET"])
    def export(self, request):
        """Export readings in JSON or CSV format with filtering support.

        Supports filtering by:
        - format: 'json' or 'csv' (default: 'json')
        - date_from: Start date/time (ISO format, inclusive)
        - date_to: End date/time (ISO format, inclusive)
        """
        export_format = request.query_params.get("export_format", "json").lower()

        if export_format not in ["json", "csv"]:
            msg = "Unsupported export format. Use 'json' or 'csv'."
            raise ValidationError({"format": msg})

        readings = self.filter_queryset(self.get_queryset())
        serializer = ReadingExportSerializer(readings, many=True)

        if export_format == "json":
            data = ReadingExporter.to_json(serializer.data)
            response = Response(data)
            response["Content-Disposition"] = 'attachment; filename="readings.json"'
            return response

        csv_content = ReadingExporter.to_csv(serializer.data)
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="readings.csv"'
        return response

    def retrieve(self, request, pk=None):
        """Detailed reading shows anemometer value as well"""
        try:
            reading = Reading.objects.select_related("anemometer").get(
                pk=pk,
            )
        except Reading.DoesNotExist as exc:
            raise NotFound from exc

        serializer = ReadingDetailSerializer(reading)
        return Response(serializer.data)


class AnemometerReadingViewSet(viewsets.ModelViewSet):
    """Readings nested into anemometers

    Allows to get anemometer specific readings operations.
    Optimized for getting anemometer data coupled with reading's.
    """

    serializer_class = ReadingMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Reading.objects.select_related("anemometer").filter(
            anemometer=self.kwargs["anemometer_pk"],
        )

    def retrieve(self, request, anemometer_pk, pk=None):
        """Detailed reading shows anemometer value as well"""
        try:
            reading = Reading.objects.select_related("anemometer").get(
                pk=pk,
            )
        except Reading.DoesNotExist as exc:
            raise NotFound from exc

        serializer = ReadingDetailSerializer(reading)
        return Response(serializer.data)
