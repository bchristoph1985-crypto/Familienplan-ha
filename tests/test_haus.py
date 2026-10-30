"""Das Haus prüft selbst."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import async_mock_service

from homeassistant.core import HomeAssistant

from custom_components.sternchenplan.const import DOMAIN
from custom_components.sternchenplan.core import SYSTEM, ChoreState, Recurrence

from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401


async def test_sensor_hakt_ab_und_meldet(hass: HomeAssistant, entry) -> None:  # noqa: F811
    lucas_calls = async_mock_service(hass, "notify", "lucas_handy")
    fam = entry.runtime_data.family
    finn = next(m for m in fam.members.values() if m.name == "Finn")
    hass.states.async_set("vacuum.robbi", "cleaning")
    hass.states.async_set("switch.spuelmaschine", "on")

    await hass.services.async_call(
        DOMAIN, "create_chore",
        {"name": "Saugroboter leeren", "assignees": ["Finn"], "points": 2,
         "requires_approval": True, "done_entity": "vacuum.robbi", "done_state": "docked"},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN, "create_chore",
        {"name": "Spülmaschine ausräumen", "assignees": ["Finn"], "recurrence": "daily",
         "due": "2026-11-02T19:00:00+00:00",
         "start_entity": "switch.spuelmaschine", "start_state": "off"},
        blocking=True,
    )
    await hass.async_block_till_done()
    robbi = next(c for c in fam.chores.values() if c.name == "Saugroboter leeren")
    assert robbi.done_entity == "vacuum.robbi"

    hass.states.async_set("switch.spuelmaschine", "off")
    await hass.async_block_till_done()
    assert lucas_calls[-1].data["message"] == "Jetzt bist du dran: Spülmaschine ausräumen"

    hass.states.async_set("vacuum.robbi", "docked")
    await hass.async_block_till_done()
    # Das Haus braucht keine Freigabe
    assert robbi.state is ChoreState.DONE
    assert finn.points == 2
    assert any("Das Haus hat gesehen" in c.data["message"] for c in lucas_calls)

    # Kopplung entfernen: kein Mitzählen mehr
    await hass.services.async_call(
        DOMAIN, "update_chore", {"chore_id": robbi.id, "done_entity": ""}, blocking=True
    )
    assert robbi.done_entity == ""


async def test_mehrere_dran_ohne_gutschrift(hass: HomeAssistant, entry) -> None:  # noqa: F811
    fam = entry.runtime_data.family
    ids = [m.id for m in fam.members.values() if m.name in ("Finn", "Paul")]
    chore = fam.create_chore(SYSTEM, "Tür zu", ids, recurrence=Recurrence.NONE,
                             house={"done_entity": "binary_sensor.tuer", "done_state": "off"})
    await entry.runtime_data.async_save()
    hass.states.async_set("binary_sensor.tuer", "on")
    await hass.async_block_till_done()
    hass.states.async_set("binary_sensor.tuer", "off")
    await hass.async_block_till_done()
    assert chore.state is ChoreState.OPEN  # wer war es? unklar, also nichts gutschreiben


async def test_geraet_kommt_zurueck_ist_kein_ereignis(hass: HomeAssistant, entry) -> None:  # noqa: F811
    fam = entry.runtime_data.family
    finn = next(m for m in fam.members.values() if m.name == "Finn")
    fam.set_features(SYSTEM, [*fam.features, "demand"])
    hass.states.async_set("sensor.waschmaschine", "fertig")
    chore = fam.create_chore(SYSTEM, "Wäsche aufhängen", [finn.id], recurrence=Recurrence.ON_DEMAND,
                             house={"start_entity": "sensor.waschmaschine", "start_state": "fertig"})
    await entry.runtime_data.async_save()
    # WLAN-Aussetzer: kurz nicht erreichbar, dann wieder „fertig“ wie vorher
    hass.states.async_set("sensor.waschmaschine", "unavailable")
    await hass.async_block_till_done()
    hass.states.async_set("sensor.waschmaschine", "fertig")
    await hass.async_block_till_done()
    assert chore.state is ChoreState.DONE  # ruht weiter
    # Echte neue Wäsche
    hass.states.async_set("sensor.waschmaschine", "läuft")
    await hass.async_block_till_done()
    hass.states.async_set("sensor.waschmaschine", "fertig")
    await hass.async_block_till_done()
    assert chore.state is not ChoreState.DONE
