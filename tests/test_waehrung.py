"""Geldbeträge in der Währung von Home Assistant."""

from custom_components.sternchenplan.money import format_money


def test_format_money() -> None:
    assert format_money(650, "EUR", "de") == "6,50 €"
    assert format_money(650, "EUR", "en") == "€6.50"
    assert format_money(650, "GBP", "en") == "£6.50"
    assert format_money(650, "USD", "en") == "$6.50"
    assert format_money(650, "CHF", "de") == "6,50 CHF"
    assert format_money(650, None, "de") == "6,50 €"
    assert format_money(100, "GBP", "en", whole=True) == "£1"
    assert format_money(100, "EUR", "de", whole=True) == "1 €"
