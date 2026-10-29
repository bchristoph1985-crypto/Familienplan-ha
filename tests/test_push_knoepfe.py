"""Freigeben und Ablehnen direkt aus der Push-Nachricht."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import async_mock_service

from homeassistant.core import Context, HomeAssistant

from custom_components.sternchenplan.core import SYSTEM, ChoreState

from .test_reminders import auto_enable_custom_integrations, entry  # noqa: F401


def _knopf(hass: HomeAssistant, action: str, user_id: str | None) -> None:
    hass.bus.async_fire(
        "mobile_app_notification_action", {"action": action}, context=Context(user_id=user_id)
    )


async def test_freigabe_aus_der_push(
    hass: HomeAssistant, entry, hass_admin_user, hass_read_only_user  # noqa: F811
) -> None:
    papa = async_mock_service(hass, "notify", "mobile_app_papa")
    family = entry.runtime_data.family
    next(m for m in family.members.values() if m.name == "Papa").notify_service = "mobile_app_papa"
    lucas = next(m for m in family.members.values() if m.name == "Lucas")
    chore = family.create_chore(SYSTEM, "Bad putzen", [lucas.id], points=5, requires_approval=True)
    await entry.runtime_data.async_save()

    await hass.services.async_call(
        "sternchenplan", "claim_chore", {"chore_id": chore.id}, blocking=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    await hass.async_block_till_done()
    ask = papa[-1].data
    assert ask["message"] == "Lucas hat „Bad putzen“ erledigt. Freigeben?"
    actions = [a["action"] for a in ask["data"]["actions"]]
    assert actions == [f"STERNCHENPLAN:APPROVE:{chore.id}", f"STERNCHENPLAN:REJECT:{chore.id}"]

    # Das Kind drückt auf einem Eltern-Handy-Knopf: nichts passiert
    _knopf(hass, actions[0], hass_read_only_user.id)
    await hass.async_block_till_done()
    assert chore.state is ChoreState.CLAIMED

    _knopf(hass, actions[0], hass_admin_user.id)
    await hass.async_block_till_done()
    assert chore.state is not ChoreState.CLAIMED
    assert lucas.points == 5
    assert papa[-1].data == {"message": "clear_notification", "data": {"tag": f"sternchenplan-{chore.id}"}}

    # Zweiter Druck (anderes Elternteil war schneller): kein Fehler, keine Doppelpunkte
    _knopf(hass, actions[0], hass_admin_user.id)
    await hass.async_block_till_done()
    assert lucas.points == 5


async def test_einloesen_aus_der_push(
    hass: HomeAssistant, entry, hass_admin_user, hass_read_only_user  # noqa: F811
) -> None:
    papa = async_mock_service(hass, "notify", "mobile_app_papa")
    family = entry.runtime_data.family
    next(m for m in family.members.values() if m.name == "Papa").notify_service = "mobile_app_papa"
    lucas = next(m for m in family.members.values() if m.name == "Lucas")
    lucas.points = 20
    reward = family.create_reward(SYSTEM, "Eis", 15)
    await entry.runtime_data.async_save()
    await hass.services.async_call(
        "sternchenplan", "redeem_reward", {"reward_id": reward.id}, blocking=True,
        context=Context(user_id=hass_read_only_user.id),
    )
    await hass.async_block_till_done()
    redemption = family.pending_redemptions()[0]
    assert papa[-1].data["data"]["actions"][1]["action"] == f"STERNCHENPLAN:REFUSE:{redemption.id}"
    _knopf(hass, f"STERNCHENPLAN:REFUSE:{redemption.id}", hass_admin_user.id)
    await hass.async_block_till_done()
    assert family.pending_redemptions() == []
    assert lucas.points == 20  # abgelehnt: Sterne zurück
    # Fremde Knöpfe anderer Integrationen werden ignoriert
    _knopf(hass, "ALARM_OFF", hass_admin_user.id)
    await hass.async_block_till_done()
