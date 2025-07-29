"""Encounter filter module."""

from django_filters import DateTimeFromToRangeFilter
from django_filters import rest_framework as filters

from .models import Encounter


class EncounterFilter(filters.FilterSet):
    """Encounter filter."""

    id = filters.CharFilter(field_name="id")
    start_date_time = DateTimeFromToRangeFilter(field_name="start_date_time")
    end_date_time = DateTimeFromToRangeFilter(field_name="end_date_time")
    patient = filters.CharFilter(field_name="patient__id")
    practitioner = filters.CharFilter(
        field_name="encounter_participant__practitioner__id"
    )

    class Meta:
        """Meta class."""

        model = Encounter
        fields = ["id", "start_date_time", "end_date_time", "patient", "practitioner"]
