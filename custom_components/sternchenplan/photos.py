"""Fotonachweis: Hochladen aus der Karte, Anzeigen für Eltern, automatisches Löschen.

Fotos liegen nur lokal im HA-Konfigurationsordner (nicht unter /local, also
nicht öffentlich). Abrufen geht nur angemeldet oder über einen kurz gültigen,
signierten Link, den nur Eltern bekommen.
"""

from __future__ import annotations

import logging
import secrets
import time
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PHOTO_DELETE_AFTER_REVIEW,
    CONF_PHOTO_RETENTION,
    DEFAULT_PHOTO_DELETE_AFTER_REVIEW,
    DEFAULT_PHOTO_RETENTION,
    DOMAIN,
    PHOTO_DIR,
    PHOTO_MAX_BYTES,
    PHOTO_URL,
)
from .core import FamilyError, PermissionDenied

if TYPE_CHECKING:
    from . import SternchenplanConfigEntry

_LOGGER = logging.getLogger(__name__)

_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}


def photo_dir(hass: HomeAssistant) -> Path:
    return Path(hass.config.path(PHOTO_DIR))


def signed_url(hass: HomeAssistant, filename: str) -> str:
    return async_sign_path(hass, f"{PHOTO_URL}/{filename}", timedelta(hours=1))


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def cleanup(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> bool:
    """Fotos nach der Löschfrist entfernen. Läuft im Executor."""
    days = int(entry.options.get(CONF_PHOTO_RETENTION, DEFAULT_PHOTO_RETENTION))
    folder = photo_dir(hass)
    if not folder.is_dir():
        return False
    limit = time.time() - days * 86400
    removed = False
    for file in folder.iterdir():
        if file.is_file() and file.stat().st_mtime < limit:
            file.unlink(missing_ok=True)
            removed = True
    return removed


def delete_after_review(entry: SternchenplanConfigEntry) -> bool:
    return bool(
        entry.options.get(CONF_PHOTO_DELETE_AFTER_REVIEW, DEFAULT_PHOTO_DELETE_AFTER_REVIEW)
    )


def _unlink(path: Path) -> None:
    path.unlink(missing_ok=True)


async def async_discard(hass: HomeAssistant, filename: str | None) -> None:
    """Ein Foto sofort von der Platte löschen."""
    if filename and "/" not in filename and "\\" not in filename and not filename.startswith("."):
        await hass.async_add_executor_job(_unlink, photo_dir(hass) / filename)


def forget_missing(hass: HomeAssistant, entry: SternchenplanConfigEntry) -> bool:
    folder = photo_dir(hass)
    family = entry.runtime_data.family
    changed = False
    for chore in family.chores.values():
        if chore.photo and not (folder / chore.photo).is_file():
            chore.photo = None
            changed = True
    # Nach der Löschfrist verschwinden die Fotos auch aus der Galerie
    gone = [e["file"] for e in family.photo_log if not (folder / e["file"]).is_file()]
    return family.forget_photos(gone) or changed


class PhotoUploadView(HomeAssistantView):
    """POST multipart: chore_id, mode (claim|take_over), optional member, file."""

    url = PHOTO_URL
    name = f"api:{DOMAIN}:photo_upload"
    requires_auth = True

    async def post(self, request: web.Request) -> web.Response:
        from .services import actor_for_user, take_over  # noqa: PLC0415

        hass: HomeAssistant = request.app["hass"]
        entries = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            return self.json_message("Sternchenplan ist nicht eingerichtet.", 404)
        data = entries[0].runtime_data
        user = request["hass_user"]
        actor = actor_for_user(data, user.id, user.is_admin)

        if request.content_length and request.content_length > PHOTO_MAX_BYTES + 64 * 1024:
            return self.json_message("Das Foto ist zu groß.", 413)
        form = await request.post()
        upload = form.get("file")
        chore_id = str(form.get("chore_id", ""))
        mode = str(form.get("mode", "claim"))
        if upload is None or not hasattr(upload, "file"):
            return self.json_message("Kein Foto dabei.", 400)
        suffix = _TYPES.get(upload.content_type or "")
        if suffix is None:
            return self.json_message("Nur Fotos (JPG, PNG, WebP, HEIC).", 415)
        content = upload.file.read(PHOTO_MAX_BYTES + 1)
        if len(content) > PHOTO_MAX_BYTES:
            return self.json_message("Das Foto ist zu groß.", 413)

        member_id = str(form.get("member") or "") or (actor.member.id if actor.member else "")
        if not member_id:
            return self.json_message("Bitte angeben, wer die Aufgabe erledigt hat.", 400)

        filename = f"{secrets.token_hex(12)}{suffix}"
        try:
            if mode == "take_over":
                take_over(data, actor, chore_id, member_id, photo=filename)
            else:
                data.family.claim(actor, chore_id, member_id, dt_util.utcnow(), photo=filename)
        except FamilyError as err:
            # Nichts geändert. Das Foto wird nicht gespeichert.
            return self.json_message(str(err), 403 if isinstance(err, PermissionDenied) else 400)

        await hass.async_add_executor_job(_write, photo_dir(hass) / filename, content)
        await data.async_save()
        return self.json({"ok": True})


class PhotoView(HomeAssistantView):
    """Foto abrufen. Nur angemeldet oder per signiertem Link."""

    url = PHOTO_URL + "/{filename}"
    name = f"api:{DOMAIN}:photo"
    requires_auth = True

    async def get(self, request: web.Request, filename: str) -> web.StreamResponse:
        hass: HomeAssistant = request.app["hass"]
        if "/" in filename or "\\" in filename or filename.startswith("."):
            return web.Response(status=404)
        path = photo_dir(hass) / filename
        if not await hass.async_add_executor_job(path.is_file):
            return web.Response(status=404)
        return web.FileResponse(path, headers={"Cache-Control": "private, max-age=3600"})
