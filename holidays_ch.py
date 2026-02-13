"""
holidays_ch.py — Schweizer Feiertagsdaten & Brückentag-Logik

Enthält:
  • Feiertagsdaten für alle 26 Kantone (feste + bewegliche)
  • Easter-Berechnung (anonymer Gregorianischer Algorithmus)
  • Brückentag-Optimierung
"""

from datetime import date, timedelta
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Gültige Kantone
# ─────────────────────────────────────────────────────────────

CANTONS: dict[str, str] = {
    "AG": "Aargau",
    "AI": "Appenzell Innerrhoden",
    "AR": "Appenzell Ausserrhoden",
    "BE": "Bern",
    "BL": "Basel-Landschaft",
    "BS": "Basel-Stadt",
    "FR": "Freiburg",
    "GE": "Genf",
    "GL": "Glarus",
    "GR": "Graubünden",
    "JU": "Jura",
    "LU": "Luzern",
    "NE": "Neuenburg",
    "NW": "Nidwalden",
    "OW": "Obwalden",
    "SG": "St. Gallen",
    "SH": "Schaffhausen",
    "SO": "Solothurn",
    "SZ": "Schwyz",
    "TG": "Thurgau",
    "TI": "Tessin",
    "UR": "Uri",
    "VD": "Waadt",
    "VS": "Wallis",
    "ZG": "Zug",
    "ZH": "Zürich",
}

VALID_YEAR_RANGE = (2020, 2035)

# ─────────────────────────────────────────────────────────────
# Easter calculation  (Anonymous Gregorian algorithm)
# ─────────────────────────────────────────────────────────────

def get_easter(year: int) -> date:
    """Compute Easter Sunday for a given year."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


# ─────────────────────────────────────────────────────────────
# Bettag (Eidgenössischer Dank-, Buss- und Bettag)
#   → 3. Sonntag im September
# ─────────────────────────────────────────────────────────────

def _bettag(year: int) -> date:
    """3rd Sunday of September."""
    sep1 = date(year, 9, 1)
    # days until first Sunday
    offset = (6 - sep1.weekday()) % 7
    first_sunday = sep1 + timedelta(days=offset)
    return first_sunday + timedelta(weeks=2)


def _bettag_monday(year: int) -> date:
    """Monday after Bettag."""
    return _bettag(year) + timedelta(days=1)


# ─────────────────────────────────────────────────────────────
# Genfer Jeûne genevois — Thursday after the first Sunday of
# September
# ─────────────────────────────────────────────────────────────

def _jeune_genevois(year: int) -> date:
    sep1 = date(year, 9, 1)
    offset = (6 - sep1.weekday()) % 7
    first_sunday = sep1 + timedelta(days=offset)
    return first_sunday + timedelta(days=4)  # Thursday


# ─────────────────────────────────────────────────────────────
# Holiday definitions per canton
#
# Each canton maps to a list of (name, date_or_factory) tuples.
# date_or_factory is either:
#   - a (month, day) tuple for fixed holidays
#   - a callable(year) -> date for movable holidays
# ─────────────────────────────────────────────────────────────

def _easter_offset(days: int):
    """Return a factory that adds `days` to Easter Sunday."""
    def factory(year: int) -> date:
        return get_easter(year) + timedelta(days=days)
    return factory


# Shared holidays
_NEUJAHR          = ("Neujahr",                    (1, 1))
_BERCHTOLDSTAG    = ("Berchtoldstag",              (1, 2))
_HEILIGE_DREI     = ("Heilige Drei Könige",        (1, 6))
_JOSEFSTAG        = ("Josefstag",                  (3, 19))
_KARFREITAG       = ("Karfreitag",                 _easter_offset(-2))
_OSTERSONNTAG     = ("Ostersonntag",               _easter_offset(0))
_OSTERMONTAG      = ("Ostermontag",                _easter_offset(1))
_TAG_DER_ARBEIT   = ("Tag der Arbeit",             (5, 1))
_AUFFAHRT         = ("Auffahrt (Christi Himmelfahrt)", _easter_offset(39))
_PFINGSTSONNTAG   = ("Pfingstsonntag",             _easter_offset(49))
_PFINGSTMONTAG    = ("Pfingstmontag",              _easter_offset(50))
_FRONLEICHNAM     = ("Fronleichnam",               _easter_offset(60))
_BUNDESFEIER      = ("Bundesfeiertag",             (8, 1))
_MARIA_HIMMELFAHRT = ("Mariä Himmelfahrt",         (8, 15))
_ALLERHEILIGEN    = ("Allerheiligen",              (11, 1))
_MARIA_EMPFAENGNIS = ("Mariä Empfängnis",          (12, 8))
_WEIHNACHTEN      = ("Weihnachten",               (12, 25))
_STEPHANSTAG      = ("Stephanstag",               (12, 26))
_BETTAG_MO        = ("Bettagsmontag",             _bettag_monday)
_NAEFELSER_FAHRT  = ("Näfelser Fahrt",             lambda year: _naefelser_fahrt(year))

def _naefelser_fahrt(year: int) -> date:
    """First Thursday of April."""
    apr1 = date(year, 4, 1)
    offset = (3 - apr1.weekday()) % 7  # 3 = Thursday
    return apr1 + timedelta(days=offset)


# ─── Canton holiday definitions ────────────────────────────

CANTON_HOLIDAYS: dict[str, list[tuple]] = {
    "ZH": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _BETTAG_MO, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "BE": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _BETTAG_MO, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "LU": [
        _NEUJAHR, _BERCHTOLDSTAG, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "UR": [
        _NEUJAHR, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "SZ": [
        _NEUJAHR, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "OW": [
        _NEUJAHR, _BERCHTOLDSTAG, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        ("Bruder Klaus", (9, 25)),
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "NW": [
        _NEUJAHR, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "GL": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _NAEFELSER_FAHRT,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _ALLERHEILIGEN,
        _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "ZG": [
        _NEUJAHR, _BERCHTOLDSTAG, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "FR": [
        _NEUJAHR, _BERCHTOLDSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT,
        _ALLERHEILIGEN, _MARIA_EMPFAENGNIS,
        _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "SO": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _FRONLEICHNAM, _BUNDESFEIER, _MARIA_HIMMELFAHRT,
        _ALLERHEILIGEN, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "BS": [
        _NEUJAHR, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "BL": [
        _NEUJAHR, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "SH": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _BETTAG_MO, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "AR": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _BETTAG_MO, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "AI": [
        _NEUJAHR, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "SG": [
        _NEUJAHR, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _ALLERHEILIGEN,
        _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "GR": [
        _NEUJAHR, _BERCHTOLDSTAG, _HEILIGE_DREI, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "AG": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _FRONLEICHNAM, _BUNDESFEIER, _MARIA_HIMMELFAHRT,
        _ALLERHEILIGEN, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "TG": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER, _BETTAG_MO, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "TI": [
        _NEUJAHR, _HEILIGE_DREI,
        _JOSEFSTAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _FRONLEICHNAM,
        ("San Pietro e Paolo", (6, 29)),
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "VD": [
        _NEUJAHR, _BERCHTOLDSTAG, _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER,
        _BETTAG_MO,
        _WEIHNACHTEN,
    ],
    "VS": [
        _NEUJAHR, _JOSEFSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG, _FRONLEICHNAM,
        _BUNDESFEIER, _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _MARIA_EMPFAENGNIS, _WEIHNACHTEN, _STEPHANSTAG,
    ],
    "NE": [
        _NEUJAHR, _BERCHTOLDSTAG,
        ("Instauration de la République", (3, 1)),
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _FRONLEICHNAM, _BUNDESFEIER,
        _BETTAG_MO, _WEIHNACHTEN,
    ],
    "GE": [
        _NEUJAHR,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _BUNDESFEIER,
        ("Jeûne genevois", _jeune_genevois),
        ("Restauration de la République", (12, 31)),
        _WEIHNACHTEN,
    ],
    "JU": [
        _NEUJAHR, _BERCHTOLDSTAG,
        _KARFREITAG, _OSTERSONNTAG, _OSTERMONTAG,
        _TAG_DER_ARBEIT, _AUFFAHRT, _PFINGSTSONNTAG, _PFINGSTMONTAG,
        _FRONLEICHNAM, _BUNDESFEIER,
        ("Plébiscite jurassien", (6, 23)),
        _MARIA_HIMMELFAHRT, _ALLERHEILIGEN,
        _WEIHNACHTEN,
    ],
}


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def validate_inputs(canton: str, year: int) -> Optional[str]:
    """Return an error message if inputs are invalid, else None."""
    if canton not in CANTONS:
        return f"Ungültiger Kanton: '{canton}'. Bitte eines der folgenden Kürzel verwenden: {', '.join(sorted(CANTONS))}."
    if year < VALID_YEAR_RANGE[0] or year > VALID_YEAR_RANGE[1]:
        return f"Jahr muss zwischen {VALID_YEAR_RANGE[0]} und {VALID_YEAR_RANGE[1]} liegen."
    return None


def get_holidays(canton: str, year: int) -> list[dict]:
    """
    Return a list of dicts: [{name, date, weekday}, ...]
    sorted by date.
    """
    error = validate_inputs(canton, year)
    if error:
        raise ValueError(error)

    WEEKDAYS_DE = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag",
        "Freitag", "Samstag", "Sonntag",
    ]

    holidays = []
    for name, spec in CANTON_HOLIDAYS[canton]:
        if callable(spec):
            d = spec(year)
        else:
            month, day = spec
            d = date(year, month, day)

        holidays.append({
            "name": name,
            "date": d,
            "weekday": WEEKDAYS_DE[d.weekday()],
        })

    holidays.sort(key=lambda h: h["date"])
    return holidays


def calculate_bridge_days(canton: str, year: int) -> list[dict]:
    """
    Find holidays on Tuesday or Thursday and suggest the adjacent
    Monday or Friday as a bridge day.

    Returns a list of dicts:
    {
      "holiday_name": str,
      "holiday_date": date,
      "bridge_date":  date,
      "bridge_weekday": str,
      "free_days":    int,          # total consecutive free days
      "recommendation": str,       # human-readable German text
    }
    """
    holidays = get_holidays(canton, year)
    holiday_dates = {h["date"] for h in holidays}

    WEEKDAYS_DE = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag",
        "Freitag", "Samstag", "Sonntag",
    ]

    recommendations = []
    seen_bridge_dates = set()

    for h in holidays:
        d = h["date"]
        wd = d.weekday()  # 0=Mon … 6=Sun

        if wd == 1:  # Dienstag → take Monday off → Sat-Sun-Mon-Tue = 4 days
            bridge = d - timedelta(days=1)
            if bridge not in seen_bridge_dates and bridge not in holiday_dates:
                seen_bridge_dates.add(bridge)
                recommendations.append({
                    "holiday_name": h["name"],
                    "holiday_date": d,
                    "bridge_date": bridge,
                    "bridge_weekday": WEEKDAYS_DE[bridge.weekday()],
                    "free_days": 4,
                    "recommendation": (
                        f"Nimm den Montag, {bridge.strftime('%d.%m.%Y')} frei — "
                        f"zusammen mit «{h['name']}» (Di {d.strftime('%d.%m.')}) "
                        f"ergibt das ein 4-Tage-Wochenende! 🎉"
                    ),
                })

        elif wd == 3:  # Donnerstag → take Friday off → Thu-Fri-Sat-Sun = 4 days
            bridge = d + timedelta(days=1)
            if bridge not in seen_bridge_dates and bridge not in holiday_dates:
                seen_bridge_dates.add(bridge)
                recommendations.append({
                    "holiday_name": h["name"],
                    "holiday_date": d,
                    "bridge_date": bridge,
                    "bridge_weekday": WEEKDAYS_DE[bridge.weekday()],
                    "free_days": 4,
                    "recommendation": (
                        f"Nimm den Freitag, {bridge.strftime('%d.%m.%Y')} frei — "
                        f"zusammen mit «{h['name']}» (Do {d.strftime('%d.%m.')}) "
                        f"ergibt das ein 4-Tage-Wochenende! 🎉"
                    ),
                })

        elif wd == 2:  # Mittwoch → could take Mon+Tue or Thu+Fri = 5 days
            bridge_before = d - timedelta(days=1)  # Dienstag
            bridge_before2 = d - timedelta(days=2)  # Montag
            if (bridge_before not in holiday_dates and bridge_before2 not in holiday_dates
                    and bridge_before not in seen_bridge_dates):
                seen_bridge_dates.add(bridge_before)
                seen_bridge_dates.add(bridge_before2)
                recommendations.append({
                    "holiday_name": h["name"],
                    "holiday_date": d,
                    "bridge_date": bridge_before2,
                    "bridge_weekday": "Montag + Dienstag",
                    "free_days": 5,
                    "recommendation": (
                        f"Nimm Montag & Dienstag ({bridge_before2.strftime('%d.%m.')} & "
                        f"{bridge_before.strftime('%d.%m.')}) frei — zusammen mit "
                        f"«{h['name']}» (Mi {d.strftime('%d.%m.')}) ergibt das 5 freie Tage! 🏖️"
                    ),
                })

    recommendations.sort(key=lambda r: r["bridge_date"])
    return recommendations
