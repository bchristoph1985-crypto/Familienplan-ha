"""Geldbeträge in der Währung, die in Home Assistant eingestellt ist."""

from __future__ import annotations

_SYMBOLS = {"EUR": "€", "GBP": "£", "USD": "$", "AUD": "A$", "CAD": "C$", "NZD": "NZ$"}


def format_money(cents: int, currency: str | None, lang: str, whole: bool = False) -> str:
    """"6,50 €", "£6.50", "6.50 CHF". Mit whole=True ohne Nachkommastellen ("1 €", "£1")."""
    currency = currency or "EUR"
    symbol = _SYMBOLS.get(currency, currency)
    number = f"{cents // 100}" if whole else f"{cents / 100:.2f}"
    if lang == "de":
        return f"{number.replace('.', ',')} {symbol}"
    return f"{symbol}{number}" if currency in _SYMBOLS else f"{number} {symbol}"
