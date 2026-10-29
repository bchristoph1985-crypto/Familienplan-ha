"""Kostenlos und Pro: Testphase, Lizenzschlüssel, was ohne Pro nicht geht."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

from homeassistant.core import Context, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.sternchenplan.const import DOMAIN, POLAR_API
from custom_components.sternchenplan.core import SYSTEM, FamilyError, Recurrence

from .test_consequences import (  # noqa: F401
    _state,
    _tick,
    auto_enable_custom_integrations,
    setup,
)

ORG = "11111111-2222-3333-4444-555555555555"
ACTIVATE = f"{POLAR_API}/v1/customer-portal/license-keys/activate"
VALIDATE = f"{POLAR_API}/v1/customer-portal/license-keys/validate"


@pytest.fixture
def org():
    with patch("custom_components.sternchenplan.licensing.POLAR_ORGANIZATION_ID", ORG):
        yield


async def _end_trial(hass, entry) -> None:
    entry.runtime_data.license.license.trial_start -= timedelta(days=31)
    await entry.runtime_data.async_tick()
    await hass.async_block_till_done()


async def test_testphase_30_tage(hass: HomeAssistant, setup) -> None:  # noqa: F811
    status = setup.runtime_data.license.status()
    assert status == {"pro": True, "licensed": False, "trial_days_left": 30, "key": None}

    # Neu einrichten startet keine neue Testphase
    setup.runtime_data.license.license.trial_start -= timedelta(days=10)
    await setup.runtime_data.license.async_save()
    await hass.config_entries.async_reload(setup.entry_id)
    await hass.async_block_till_done()
    assert setup.runtime_data.license.status()["trial_days_left"] == 20


async def test_ohne_pro_gesperrte_geraete_frei_und_funktionen_aus(
    hass: HomeAssistant, setup, freezer, hass_admin_user, hass_read_only_user  # noqa: F811
) -> None:
    await _tick(hass, freezer, "2026-11-02 20:01:00+00:00")
    assert _state(hass, "switch.ps5") == "off"

    await _end_trial(hass, setup)
    assert not setup.runtime_data.pro
    # Ohne Pro sperrt Sternchenplan nichts mehr und gibt Gesperrtes frei
    assert _state(hass, "switch.ps5") == "on"
    assert setup.runtime_data.family.locked == {}

    admin = Context(user_id=hass_admin_user.id)
    for service, data in (
        ("set_absence", {"member": "Lucas", "until": "2026-11-05 12:00:00"}),
        ("announce", {"message": "Hallo"}),
    ):
        with pytest.raises(ServiceValidationError, match="Pro"):
            await hass.services.async_call(DOMAIN, service, data, blocking=True, context=admin)


async def test_ohne_pro_kein_fotozwang(
    hass: HomeAssistant, setup, hass_read_only_user  # noqa: F811
) -> None:
    family = setup.runtime_data.family
    lucas = next(m for m in family.members.values() if m.name == "Lucas")
    chore = family.create_chore(
        SYSTEM, "Zimmer", [lucas.id], recurrence=Recurrence.NONE, requires_photo=True
    )
    kid = family.actor_for_user(hass_read_only_user.id, is_admin=False)
    with pytest.raises(FamilyError):
        family.claim(kid, chore.id, lucas.id, dt_util.utcnow())

    await _end_trial(hass, setup)
    family.claim(kid, chore.id, lucas.id, dt_util.utcnow())
    assert chore.requires_photo  # Einstellung bleibt für später erhalten


async def test_schluessel_aktivieren_und_entzug(
    hass: HomeAssistant, setup, aioclient_mock, org  # noqa: F811
) -> None:
    await _end_trial(hass, setup)
    manager = setup.runtime_data.license
    aioclient_mock.post(
        ACTIVATE, json={"id": "act-1", "license_key": {"status": "granted"}}
    )
    await manager.async_activate("  FAMILIE-ABC-123456  ")
    assert manager.status() == {
        "pro": True, "licensed": True, "trial_days_left": 0, "key": "…123456"
    }
    assert aioclient_mock.mock_calls[-1][2]["organization_id"] == ORG

    # Innerhalb einer Woche wird nicht nachgefragt
    assert not await manager.async_validate_if_due()
    assert aioclient_mock.call_count == 1

    # Ohne Internet bleibt Pro an
    later = dt_util.utcnow() + timedelta(days=8)
    aioclient_mock.post(VALIDATE, exc=TimeoutError())
    assert not await manager.async_validate_if_due(later)
    assert manager.is_pro(later)

    # Erstattet: Polar sagt revoked, dann endet Pro
    aioclient_mock.clear_requests()
    aioclient_mock.post(VALIDATE, json={"status": "revoked"})
    assert await manager.async_validate_if_due(later)
    assert not manager.is_pro(later)


@pytest.mark.parametrize(
    ("status", "reason"),
    [(404, "key_unknown"), (403, "too_many_activations"), (500, "cannot_connect")],
)
async def test_schluessel_fehler(
    hass: HomeAssistant, setup, aioclient_mock, org, status, reason  # noqa: F811
) -> None:
    aioclient_mock.post(ACTIVATE, status=status, json={})
    flow = await hass.config_entries.options.async_init(setup.entry_id)
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"next_step_id": "pro"}
    )
    assert "Testphase" in flow["description_placeholders"]["state"]
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"license_key": "FALSCH"}
    )
    assert flow["type"] is FlowResultType.FORM
    assert flow["errors"] == {"base": reason}
    assert not setup.runtime_data.license.license.valid


async def test_shop_noch_nicht_eingerichtet(hass: HomeAssistant, setup) -> None:  # noqa: F811
    with patch("custom_components.sternchenplan.licensing.POLAR_ORGANIZATION_ID", ""):
        await _shop_not_ready(hass, setup)


async def _shop_not_ready(hass, setup) -> None:  # noqa: F811
    flow = await hass.config_entries.options.async_init(setup.entry_id)
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"next_step_id": "pro"}
    )
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"license_key": "ABC"}
    )
    assert flow["errors"] == {"base": "shop_not_ready"}


async def test_schluessel_im_dialog_und_freigeben(
    hass: HomeAssistant, setup, aioclient_mock, org  # noqa: F811
) -> None:
    aioclient_mock.post(ACTIVATE, json={"id": "act-1", "license_key": {"status": "granted"}})
    aioclient_mock.post(
        f"{POLAR_API}/v1/customer-portal/license-keys/deactivate", status=204
    )
    flow = await hass.config_entries.options.async_init(setup.entry_id)
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"next_step_id": "pro"}
    )
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"license_key": "FAMILIE-ABC-123456"}
    )
    assert flow["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    manager = hass.config_entries.async_get_entry(setup.entry_id).runtime_data.license
    assert manager.license.valid

    flow = await hass.config_entries.options.async_init(setup.entry_id)
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"next_step_id": "pro"}
    )
    assert "freigeschaltet" in flow["description_placeholders"]["state"]
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"], {"license_remove": True}
    )
    assert flow["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    manager = hass.config_entries.async_get_entry(setup.entry_id).runtime_data.license
    assert not manager.license.valid and manager.license.key is None
