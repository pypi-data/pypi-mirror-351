"""Slot choices for the slots app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentType(models.TextChoices):
    """Appointment type choices."""

    WALK_IN = "walk-in", _("Walk-in")
    ROUTINE = "routine", _("Routine")
    CHECKUP = "checkup", _("Check-up")
    FOLLOWUP = "followup", _("Follow-up")
    EMERGENCY = "emergency", _("Emergency")


class SlotStatus(models.TextChoices):
    """Slot status choices."""

    FREE = "free", _("Free")
    BUSY = "busy", _("Busy")
    BUSY_UNAVAILABLE = "busy_unavailable", _("Busy Unavailable")
    BUSY_TENTATIVE = "busy_tentative", _("Busy Tentative")
    ENTER_IN_ERROR = "enter_in_error", _("Enter in Error")
