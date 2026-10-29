"""Kostenlos oder Pro.

Kostenlos: Aufgaben, Punkte, Belohnungen, Push-Erinnerungen.
Pro: Internetsperre, Fotonachweis, Aufgaben übernehmen, Lautsprecher-Ansagen,
Abwesenheit mit Vertretung.

Nach der Installation läuft Pro 30 Tage zum Ausprobieren. Danach braucht es
einen Lizenzschlüssel. Der Schlüssel wird einmal online bei Polar aktiviert
und danach nur gelegentlich nachgeprüft. Ohne Internet bleibt Pro an. Pro
endet nur, wenn Polar den Schlüssel ausdrücklich ablehnt (z. B. erstattet).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    POLAR_API,
    POLAR_ORGANIZATION_ID,
    STORAGE_VERSION,
    TRIAL_DAYS,
    VALIDATE_EVERY,
)

_LOGGER = logging.getLogger(__name__)

# Bewusst ohne entry_id: Neu einrichten startet keine neue Testphase und
# verliert den Schlüssel nicht.
STORAGE_KEY = f"{DOMAIN}.license"


class LicenseError(Exception):
    """Aktivieren hat nicht geklappt. Der Text kommt direkt in die Oberfläche."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class License:
    trial_start: datetime
    key: str | None = None
    activation_id: str | None = None
    valid: bool = False
    last_check: datetime | None = None

    def is_pro(self, now: datetime) -> bool:
        return self.valid or self.trial_days_left(now) > 0

    def trial_days_left(self, now: datetime) -> int:
        left = self.trial_start + timedelta(days=TRIAL_DAYS) - now
        if left <= timedelta(0):
            return 0
        return left.days + (1 if left % timedelta(days=1) else 0)

    def display_key(self) -> str | None:
        """Nur das Ende zeigen, der Schlüssel gehört nicht in Screenshots."""
        if not self.key:
            return None
        return f"…{self.key[-6:]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_start": self.trial_start.isoformat(),
            "key": self.key,
            "activation_id": self.activation_id,
            "valid": self.valid,
            "last_check": self.last_check.isoformat() if self.last_check else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> License:
        last = data.get("last_check")
        return cls(
            trial_start=datetime.fromisoformat(data["trial_start"]),
            key=data.get("key"),
            activation_id=data.get("activation_id"),
            valid=bool(data.get("valid")),
            last_check=datetime.fromisoformat(last) if last else None,
        )


class LicenseManager:
    """Lädt, speichert und prüft die Lizenz."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.license = License(trial_start=dt_util.utcnow())

    async def async_load(self) -> None:
        stored = await self.store.async_load()
        if stored:
            self.license = License.from_dict(stored)
        else:
            # Erste Installation: Testphase beginnt jetzt.
            await self.async_save()

    async def async_save(self) -> None:
        await self.store.async_save(self.license.to_dict())

    def is_pro(self, now: datetime | None = None) -> bool:
        return self.license.is_pro(now or dt_util.utcnow())

    def status(self, now: datetime | None = None) -> dict[str, Any]:
        now = now or dt_util.utcnow()
        lic = self.license
        return {
            "pro": lic.is_pro(now),
            "licensed": lic.valid,
            "trial_days_left": 0 if lic.valid else lic.trial_days_left(now),
            "key": lic.display_key(),
        }

    async def _post(self, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        session = async_get_clientsession(self.hass)
        async with asyncio.timeout(20):
            async with session.post(f"{POLAR_API}{path}", json=payload) as resp:
                try:
                    body = await resp.json(content_type=None)
                except ValueError:
                    body = {}
                return resp.status, body if isinstance(body, dict) else {}

    async def async_activate(self, key: str) -> None:
        """Schlüssel einmal online aktivieren. Wirft LicenseError mit Grund."""
        key = key.strip()
        if not key:
            raise LicenseError("key_missing")
        if not POLAR_ORGANIZATION_ID:
            raise LicenseError("shop_not_ready")
        payload = {
            "key": key,
            "organization_id": POLAR_ORGANIZATION_ID,
            "label": f"Home Assistant {self.hass.config.location_name}"[:100],
        }
        try:
            status, body = await self._post(
                "/v1/customer-portal/license-keys/activate", payload
            )
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.warning("Lizenz aktivieren: keine Verbindung (%s)", err)
            raise LicenseError("cannot_connect") from err
        if status == 404:
            raise LicenseError("key_unknown")
        if status == 403:
            raise LicenseError("too_many_activations")
        if status != 200:
            _LOGGER.warning("Lizenz aktivieren: Antwort %s %s", status, body)
            raise LicenseError("cannot_connect")
        if (body.get("license_key") or {}).get("status") != "granted":
            raise LicenseError("key_revoked")
        self.license.key = key
        self.license.activation_id = body.get("id")
        self.license.valid = True
        self.license.last_check = dt_util.utcnow()
        await self.async_save()

    async def async_deactivate(self) -> None:
        """Schlüssel hier freigeben, z. B. vor dem Umzug auf ein neues Gerät.

        Klappt das online nicht, wird der Schlüssel trotzdem hier entfernt.
        """
        lic = self.license
        if lic.key and lic.activation_id and POLAR_ORGANIZATION_ID:
            try:
                await self._post(
                    "/v1/customer-portal/license-keys/deactivate",
                    {
                        "key": lic.key,
                        "organization_id": POLAR_ORGANIZATION_ID,
                        "activation_id": lic.activation_id,
                    },
                )
            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.warning("Lizenz freigeben: keine Verbindung (%s)", err)
        lic.key = lic.activation_id = lic.last_check = None
        lic.valid = False
        await self.async_save()

    async def async_validate_if_due(self, now: datetime | None = None) -> bool:
        """Ab und zu nachprüfen. Gibt True zurück, wenn Pro dadurch endet.

        Keine Verbindung oder Polar gestört: nichts ändern, später wieder.
        """
        now = now or dt_util.utcnow()
        lic = self.license
        if not lic.valid or not lic.key or not POLAR_ORGANIZATION_ID:
            return False
        if lic.last_check and now - lic.last_check < VALIDATE_EVERY:
            return False
        payload = {"key": lic.key, "organization_id": POLAR_ORGANIZATION_ID}
        if lic.activation_id:
            payload["activation_id"] = lic.activation_id
        try:
            status, body = await self._post(
                "/v1/customer-portal/license-keys/validate", payload
            )
        except (aiohttp.ClientError, TimeoutError):
            return False
        if status == 200 and body.get("status") == "granted":
            lic.last_check = now
            await self.async_save()
            return False
        if status == 404 or (status == 200 and body.get("status") in ("revoked", "disabled")):
            _LOGGER.warning("Sternchenplan Pro: Lizenzschlüssel ist nicht mehr gültig")
            lic.valid = False
            lic.last_check = now
            await self.async_save()
            return True
        return False
