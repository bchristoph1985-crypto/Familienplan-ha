"""Wegmopsen: Wann Geschwister fremde Aufgaben übernehmen dürfen und mit welchem Faktor."""

from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING

from homeassistant.util import dt as dt_util

from .const import (
    CONF_TAKEOVER_DOUBLE,
    CONF_TAKEOVER_FROM,
    CONF_TAKEOVER_MAX,
    DEFAULT_TAKEOVER_DOUBLE,
    DEFAULT_TAKEOVER_FROM,
    DEFAULT_TAKEOVER_MAX,
)

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry


def _time(value: str) -> time | None:
    value = (value or "").strip()
    return time.fromisoformat(value) if value else None


def takeover_terms(entry: SternchenplanConfigEntry, now: datetime) -> tuple[bool, int, int, datetime]:
    """(erlaubt, Faktor, max. pro Tag, Tagesbeginn in UTC)."""
    options = entry.options
    local = dt_util.as_local(now)
    day_start = dt_util.as_utc(local.replace(hour=0, minute=0, second=0, microsecond=0))
    start = _time(options.get(CONF_TAKEOVER_FROM, DEFAULT_TAKEOVER_FROM))
    double = _time(options.get(CONF_TAKEOVER_DOUBLE, DEFAULT_TAKEOVER_DOUBLE))
    allowed = start is not None and local.time() >= start
    multiplier = 2 if double is not None and local.time() >= double else 1
    return allowed, multiplier, int(options.get(CONF_TAKEOVER_MAX, DEFAULT_TAKEOVER_MAX)), day_start
