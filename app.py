"""
SwissHolidayOptimizer — Streamlit Frontend
Swiss Design: Helvetica, generous whitespace, red accent.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from io import BytesIO
import calendar

from holidays_ch import (
    CANTONS, VALID_YEAR_RANGE, get_holidays,
    calculate_bridge_days, validate_inputs,
)

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SwissHolidayOptimizer 🇨🇭",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS — Swiss Design aesthetic
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Typography — Swiss Grotesk ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}

/* ── Global — pure white canvas ── */
.stApp {
    background: #FFFFFF;
}

/* ── Remove Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Hero header — flat Swiss red bar ── */
.hero {
    background: #FF0000;
    padding: 2.8rem 3rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    position: relative;
}
.hero h1 {
    color: #FFFFFF;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.03em;
}
.hero p {
    color: rgba(255,255,255,0.85);
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
}
.hero .swiss-cross {
    position: absolute;
    top: 50%;
    right: 2.5rem;
    transform: translateY(-50%);
    width: 48px;
    height: 48px;
    opacity: 0.2;
}

/* ── Section titles (red, with dotted underline) ── */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FF0000;
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.8rem;
    border-bottom: 2px dotted #FF0000;
    letter-spacing: -0.01em;
    text-transform: uppercase;
}

/* ── Dotted separator ── */
.dotted-sep {
    border: none;
    border-top: 2px dotted #FF0000;
    margin: 2rem 0;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.stat-chip {
    background: #F2F2F2;
    border-radius: 20px;
    padding: 1rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    flex: 1;
    min-width: 160px;
    border: none;
}
.stat-chip .stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #FF0000;
    line-height: 1;
}
.stat-chip .stat-label {
    font-size: 0.82rem;
    color: #666;
    font-weight: 500;
    line-height: 1.3;
}

/* ── Recommendation cards ── */
.rec-card {
    background: #F2F2F2;
    border-left: 4px solid #FF0000;
    border-radius: 0 20px 20px 0;
    padding: 1.3rem 1.6rem;
    margin-bottom: 0.8rem;
    transition: transform 0.15s ease;
}
.rec-card:hover {
    transform: translateX(4px);
}
.rec-card .rec-title {
    font-weight: 700;
    color: #FF0000;
    font-size: 1rem;
    margin-bottom: 0.3rem;
}
.rec-card .rec-text {
    color: #333;
    font-size: 0.95rem;
    line-height: 1.5;
}
.rec-card .rec-days {
    display: inline-block;
    background: #FF0000;
    color: #FFF;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Calendar grid ── */
.cal-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.cal-month {
    background: #F2F2F2;
    border-radius: 20px;
    padding: 1.2rem;
}
.cal-month-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: #000;
    text-align: center;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}
.cal-header {
    text-align: center;
    font-size: 0.65rem;
    font-weight: 700;
    color: #999;
    padding: 0.3rem 0;
    text-transform: uppercase;
}
.cal-day {
    text-align: center;
    padding: 0.35rem 0.1rem;
    border-radius: 50%;
    font-size: 0.82rem;
    font-weight: 500;
    color: #333;
    transition: transform 0.12s ease;
    position: relative;
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}
.cal-day.empty { visibility: hidden; }
.cal-day.weekend {
    color: #AAA;
}
.cal-day.holiday {
    background: #FF0000;
    color: #FFFFFF;
    font-weight: 700;
}
.cal-day.bridge {
    background: #000000;
    color: #FFFFFF;
    font-weight: 700;
}
.cal-day.today {
    outline: 2px solid #FF0000;
    outline-offset: -1px;
}
.cal-day.holiday:hover,
.cal-day.bridge:hover {
    transform: scale(1.3);
    z-index: 10;
    cursor: pointer;
}

/* ── Tooltip ── */
.cal-day[title] {
    position: relative;
}
.cal-day[title]:hover::after {
    content: attr(title);
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: #000;
    color: #FFF;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    white-space: nowrap;
    pointer-events: none;
    z-index: 100;
    animation: fadeIn 0.15s ease;
}
.cal-day[title]:hover::before {
    content: '';
    position: absolute;
    bottom: calc(100% + 2px);
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #000;
    pointer-events: none;
    z-index: 100;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateX(-50%) translateY(4px); }
    to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* ── Legend ── */
.legend {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    padding: 0.8rem 1.2rem;
    background: #F2F2F2;
    border-radius: 999px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.82rem;
    color: #555;
    font-weight: 500;
}
.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}
.legend-dot.holiday-dot { background: #FF0000; }
.legend-dot.bridge-dot  { background: #000000; }
.legend-dot.weekend-dot { background: #DDD; }
.legend-dot.today-dot   { background: #FFF; border: 2px solid #FF0000; }

/* ── Holiday table ── */
.holiday-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.holiday-table thead {
    background: #FF0000;
}
.holiday-table th {
    color: #FFFFFF;
    padding: 1rem 1.2rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.holiday-table td {
    padding: 0.85rem 1.2rem;
    color: #222;
    font-size: 0.95rem;
    border-bottom: 1px dotted #DDD;
}
.holiday-table tr:last-child td {
    border-bottom: none;
}
.holiday-table tbody tr {
    background: #FFFFFF;
    transition: background 0.12s ease;
}
.holiday-table tbody tr:hover {
    background: #FFF5F5;
}
.holiday-table tbody tr:nth-child(even) {
    background: #F9F9F9;
}
.holiday-table tbody tr:nth-child(even):hover {
    background: #FFF5F5;
}

/* ── Weekday badges (pill shape) ── */
.wd-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}
.wd-badge.weekend { background: #F2F2F2; color: #888; }
.wd-badge.workday { background: #E8F5E9; color: #2E7D32; }

/* ── Download/Primary button — pill shape ── */
.stDownloadButton button {
    background: #FF0000 !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.75rem 2.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    transition: transform 0.15s ease, opacity 0.15s ease !important;
    letter-spacing: 0.02em !important;
}
.stDownloadButton button:hover {
    transform: translateY(-2px) !important;
    opacity: 0.9 !important;
}

.stButton > button[kind="primary"], .stButton > button {
    background: #FF0000 !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 700 !important;
    transition: transform 0.15s ease, opacity 0.15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    opacity: 0.9 !important;
}

/* ── Streamlit selectbox / number input override ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    border-radius: 999px !important;
    border: 2px solid #E0E0E0 !important;
    padding-left: 1rem !important;
}
.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus {
    border-color: #FF0000 !important;
    box-shadow: 0 0 0 1px #FF0000 !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #999;
    font-size: 1.05rem;
    background: #F2F2F2;
    border-radius: 20px;
}
.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 2rem;
    color: #999;
    font-size: 0.8rem;
    margin-top: 2rem;
    border-top: 2px dotted #FF0000;
}

/* ── Safari / iOS global fixes ── */
html {
    -webkit-text-size-adjust: 100%;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
body {
    -webkit-overflow-scrolling: touch;
}

/* Prevent Safari zoom on input focus (must be >= 16px) */
input, select, textarea {
    font-size: 16px !important;
}

/* Safe-area padding for iPhone notch / home indicator */
.stApp {
    padding-left: env(safe-area-inset-left) !important;
    padding-right: env(safe-area-inset-right) !important;
    padding-bottom: env(safe-area-inset-bottom) !important;
}

/* Remove Safari default input styling */
input, select, button, textarea {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
}

/* ── Tablet breakpoint (≤ 768px) ── */
@media (max-width: 768px) {
    /* Streamlit columns → stack vertically */
    [data-testid="column"] {
        width: 100% !important;
        flex: 0 0 100% !important;
        max-width: 100% !important;
    }

    .hero {
        padding: 1.5rem 1.2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
    }
    .hero h1 { font-size: 1.6rem; }
    .hero p { font-size: 0.95rem; }
    .hero .swiss-cross { display: none; }

    .stats-bar {
        gap: 0.5rem;
        display: grid;
        grid-template-columns: 1fr 1fr;
    }
    .stat-chip {
        min-width: 0;
        padding: 0.8rem 1rem;
        border-radius: 14px;
    }
    .stat-chip .stat-number { font-size: 1.5rem; }
    .stat-chip .stat-label { font-size: 0.72rem; }

    .cal-container {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 0.6rem;
    }
    .cal-month {
        padding: 0.8rem 0.5rem;
        border-radius: 14px;
    }
    .cal-month-title { font-size: 0.82rem; }
    .cal-day {
        font-size: 0.72rem;
    }
    .cal-header { font-size: 0.58rem; }

    .rec-card {
        padding: 1rem 1.2rem;
        border-radius: 0 14px 14px 0;
    }
    .rec-card .rec-title { font-size: 0.9rem; }
    .rec-card .rec-text { font-size: 0.85rem; }

    .legend {
        gap: 0.8rem;
        padding: 0.6rem 1rem;
        border-radius: 14px;
    }
    .legend-item { font-size: 0.75rem; }
    .section-title { font-size: 1rem; }

    /* Download button full-width */
    .stDownloadButton button {
        padding: 0.7rem 1.5rem !important;
        font-size: 0.9rem !important;
    }

    /* Button touch-friendly size */
    .stButton > button {
        min-height: 44px !important;
        padding: 0.55rem 1.5rem !important;
    }
}

/* ── Phone breakpoint (≤ 480px) ── */
@media (max-width: 480px) {
    .hero {
        padding: 1.2rem 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .hero h1 { font-size: 1.3rem; }
    .hero p { font-size: 0.85rem; }

    .stats-bar {
        grid-template-columns: 1fr 1fr;
        gap: 0.4rem;
    }
    .stat-chip {
        padding: 0.65rem 0.8rem;
        border-radius: 12px;
        gap: 0.5rem;
    }
    .stat-chip .stat-number { font-size: 1.2rem; }
    .stat-chip .stat-label { font-size: 0.65rem; }

    /* Calendar → 2 columns on phone for readability */
    .cal-container {
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
    }
    .cal-month {
        padding: 0.6rem 0.4rem;
        border-radius: 12px;
    }
    .cal-month-title { font-size: 0.75rem; }
    .cal-day { font-size: 0.65rem; }
    .cal-header { font-size: 0.5rem; }
    .cal-grid { gap: 2px; }

    .rec-card {
        padding: 0.85rem 1rem;
        margin-bottom: 0.6rem;
        border-radius: 0 12px 12px 0;
    }
    .rec-card .rec-title { font-size: 0.85rem; }
    .rec-card .rec-text { font-size: 0.8rem; line-height: 1.4; }
    .rec-card .rec-days {
        font-size: 0.68rem;
        padding: 0.15rem 0.5rem;
    }

    .legend {
        gap: 0.5rem;
        padding: 0.5rem 0.7rem;
        border-radius: 12px;
    }
    .legend-item { font-size: 0.68rem; }
    .legend-dot { width: 10px; height: 10px; }

    .section-title {
        font-size: 0.9rem;
        margin: 1.8rem 0 0.8rem 0;
        padding-bottom: 0.6rem;
    }

    .empty-state {
        padding: 2rem 1rem;
        font-size: 0.9rem;
        border-radius: 12px;
    }

    .app-footer {
        font-size: 0.7rem;
        padding: 1.2rem 0.5rem;
    }

    /* Full-width download button on phone */
    .stDownloadButton button {
        width: 100% !important;
        padding: 0.65rem 1rem !important;
        font-size: 0.85rem !important;
    }
    .stButton > button {
        width: 100% !important;
        min-height: 48px !important;
    }

    /* Streamlit number input +/- buttons — touch-friendly */
    .stNumberInput button {
        min-width: 36px !important;
        min-height: 36px !important;
    }
}

/* ── Touch device: disable hover transforms ── */
@media (hover: none) and (pointer: coarse) {
    .cal-day.holiday:hover,
    .cal-day.bridge:hover {
        transform: none;
    }
    .rec-card:hover {
        transform: none;
    }
    .stButton > button:hover {
        transform: none !important;
    }
    .stDownloadButton button:hover {
        transform: none !important;
    }
    /* Tooltip: show on tap via focus instead */
    .cal-day[title]:hover::after,
    .cal-day[title]:hover::before {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Helper: generate iCal
# ─────────────────────────────────────────────────────────────

def _strip_emojis(text: str) -> str:
    """Remove emoji characters that break some calendar apps."""
    import re
    return re.sub(
        r'[\U0001F300-\U0001FAD6\U0001FA70-\U0001FAFF\U00002702-\U000027B0'
        r'\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF\U0000200D]+',
        '', text
    ).strip()


def _ical_escape(text: str) -> str:
    """Escape special characters for iCalendar text fields."""
    text = _strip_emojis(text)
    text = text.replace('\\', '\\\\')
    text = text.replace(';', '\\;')
    text = text.replace(',', '\\,')
    text = text.replace('\n', '\\n')
    return text


def generate_ical(recommendations: list[dict], canton: str, year: int) -> str:
    """Generate a valid RFC 5545 iCalendar string manually."""
    from datetime import datetime
    import uuid

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SwissHolidayOptimizer//CH//",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Brueckentage {CANTONS[canton]} {year}",
    ]

    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    for rec in recommendations:
        uid = f"{uuid.uuid4()}@swissholidayoptimizer.ch"
        dtstart = rec["bridge_date"].strftime("%Y%m%d")
        from datetime import timedelta
        dtend = (rec["bridge_date"] + timedelta(days=1)).strftime("%Y%m%d")
        summary = _ical_escape(rec["holiday_name"])
        desc = _ical_escape(rec["recommendation"])

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:Brueckentag - {summary}",
            f"DESCRIPTION:{desc}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


# ─────────────────────────────────────────────────────────────
# Helper: render calendar month as HTML
# ─────────────────────────────────────────────────────────────

MONTH_NAMES_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

def render_calendar_html(
    year: int,
    holiday_dates: set,
    bridge_dates: set,
    holiday_names: dict = None,
    bridge_names: dict = None,
) -> str:
    """Render a 12-month calendar grid as HTML.

    holiday_names / bridge_names: dict mapping date -> display name
    (used for tooltip on hover).
    """
    today = date.today()
    holiday_names = holiday_names or {}
    bridge_names = bridge_names or {}
    html_parts = ['<div class="cal-container">']

    for month in range(1, 13):
        html_parts.append(f'<div class="cal-month">')
        html_parts.append(f'<div class="cal-month-title">{MONTH_NAMES_DE[month]}</div>')
        html_parts.append('<div class="cal-grid">')

        # Day headers
        for dh in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
            html_parts.append(f'<div class="cal-header">{dh}</div>')

        # Calendar days
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            for day_num in week:
                if day_num == 0:
                    html_parts.append('<div class="cal-day empty"></div>')
                    continue

                d = date(year, month, day_num)
                classes = ["cal-day"]
                tooltip = ""

                if d in holiday_dates:
                    classes.append("holiday")
                    tooltip = holiday_names.get(d, "")
                elif d in bridge_dates:
                    classes.append("bridge")
                    tooltip = bridge_names.get(d, "")
                elif d.weekday() >= 5:
                    classes.append("weekend")

                if d == today:
                    classes.append("today")

                title_attr = f' title="{tooltip}"' if tooltip else ''
                html_parts.append(
                    f'<div class="{" ".join(classes)}"{title_attr}>{day_num}</div>'
                )

        html_parts.append('</div></div>')

    html_parts.append('</div>')
    return "\n".join(html_parts)


# ─────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────

def main():
    # ── Hero ──
    st.markdown("""
    <div class="hero">
        <h1>SwissHolidayOptimizer</h1>
        <p>Maximiere deine freien Tage — finde die besten Brückentage für deinen Kanton.</p>
        <svg class="swiss-cross" viewBox="0 0 32 32" fill="white">
            <rect x="13" y="6" width="6" height="20"/>
            <rect x="6" y="13" width="20" height="6"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # ── Controls ──
    canton_options = {f"{code} — {name}": code for code, name in sorted(CANTONS.items())}

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        canton_display = st.selectbox(
            "Ort",
            options=list(canton_options.keys()),
            index=list(canton_options.keys()).index("ZH — Zürich"),
        )
        canton = canton_options[canton_display]

    with col2:
        current_year = date.today().year
        year = st.number_input(
            "Jahr",
            min_value=VALID_YEAR_RANGE[0],
            max_value=VALID_YEAR_RANGE[1],
            value=current_year,
            step=1,
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        calculate = st.button("Berechnen", use_container_width=True)

    # ── Calculate (auto-trigger or on button) ──
    if calculate or "last_canton" not in st.session_state:
        st.session_state["last_canton"] = canton
        st.session_state["last_year"] = year

    canton = st.session_state.get("last_canton", canton)
    year = st.session_state.get("last_year", year)

    error = validate_inputs(canton, int(year))
    if error:
        st.error(error)
        return

    holidays = get_holidays(canton, int(year))
    recommendations = calculate_bridge_days(canton, int(year))

    holiday_dates = {h["date"] for h in holidays}
    bridge_dates = {r["bridge_date"] for r in recommendations}

    # Name maps for calendar tooltips
    holiday_names = {h["date"]: h["name"] for h in holidays}
    bridge_names = {r["bridge_date"]: f'Brückentag ({r["holiday_name"]})' for r in recommendations}

    # ── Stats Bar ──
    workday_holidays = sum(1 for h in holidays if h["date"].weekday() < 5)
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-chip">
            <div class="stat-number">{len(holidays)}</div>
            <div class="stat-label">Feiertage<br>{CANTONS[canton]}</div>
        </div>
        <div class="stat-chip">
            <div class="stat-number">{workday_holidays}</div>
            <div class="stat-label">davon an<br>Werktagen</div>
        </div>
        <div class="stat-chip">
            <div class="stat-number">{len(recommendations)}</div>
            <div class="stat-label">Brückentag-<br>Möglichkeiten</div>
        </div>
        <div class="stat-chip">
            <div class="stat-number">{sum(r['free_days'] for r in recommendations)}</div>
            <div class="stat-label">potenzielle<br>freie Tage total</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Calendar View ──
    st.markdown('<div class="section-title">Jahreskalender</div>', unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div class="legend">
        <div class="legend-item"><div class="legend-dot holiday-dot"></div> Feiertag</div>
        <div class="legend-item"><div class="legend-dot bridge-dot"></div> Brückentag</div>
        <div class="legend-item"><div class="legend-dot weekend-dot"></div> Wochenende</div>
        <div class="legend-item"><div class="legend-dot today-dot"></div> Heute</div>
    </div>
    """, unsafe_allow_html=True)

    cal_html = render_calendar_html(int(year), holiday_dates, bridge_dates, holiday_names, bridge_names)
    st.markdown(cal_html, unsafe_allow_html=True)

    # ── Bridge Day Recommendations ──
    st.markdown('<div class="section-title">Brückentag-Empfehlungen</div>', unsafe_allow_html=True)

    if recommendations:
        for rec in recommendations:
            st.markdown(f"""
            <div class="rec-card">
                <div class="rec-title">
                    {rec['holiday_name']}
                    <span class="rec-days">{rec['free_days']} Tage frei</span>
                </div>
                <div class="rec-text">{rec['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── iCal Export ──
        st.markdown('<div class="section-title">Kalender-Export</div>', unsafe_allow_html=True)

        ical_data = generate_ical(recommendations, canton, int(year))
        ical_bytes = ical_data.encode("utf-8")
        st.download_button(
            label="In Kalender exportieren (.ics)",
            data=ical_bytes,
            file_name=f"brueckentage_{canton}_{int(year)}.ics",
            mime="text/calendar",
            use_container_width=True,
            key="ical_download",
        )
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🤷</div>
            Keine Brückentag-Möglichkeiten in diesem Jahr gefunden.<br>
            Die Feiertage fallen ungünstig auf Wochenenden oder Wochenmitte.
        </div>
        """, unsafe_allow_html=True)

    # ── Holiday Table ──
    st.markdown('<div class="section-title">Alle Feiertage</div>', unsafe_allow_html=True)

    weekend_class = lambda wd: "weekend" if wd in ("Samstag", "Sonntag") else "workday"

    table_rows = []
    for h in holidays:
        d = h["date"]
        badge_class = weekend_class(h["weekday"])
        table_rows.append(
            f'<tr><td><strong>{h["name"]}</strong></td>'
            f'<td>{d.strftime("%d.%m.%Y")}</td>'
            f'<td><span class="wd-badge {badge_class}">{h["weekday"]}</span></td></tr>'
        )

    table_html = (
        '<html><head>'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<style>'
        '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");'
        'body{margin:0;padding:0;font-family:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif;background:transparent;-webkit-text-size-adjust:100%;}'
        '.holiday-table{width:100%;border-collapse:separate;border-spacing:0;border-radius:20px;overflow:hidden;}'
        '.holiday-table thead{background:#FF0000;}'
        '.holiday-table th{color:#FFF;padding:1rem 1.2rem;text-align:left;font-weight:600;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.06em;}'
        '.holiday-table td{padding:0.85rem 1.2rem;color:#222;font-size:0.95rem;border-bottom:1px dotted #DDD;}'
        '.holiday-table tr:last-child td{border-bottom:none;}'
        '.holiday-table tbody tr{background:#FFF;transition:background 0.12s ease;}'
        '.holiday-table tbody tr:hover{background:#FFF5F5;}'
        '.holiday-table tbody tr:nth-child(even){background:#F9F9F9;}'
        '.holiday-table tbody tr:nth-child(even):hover{background:#FFF5F5;}'
        '.wd-badge{display:inline-block;padding:0.2rem 0.7rem;border-radius:999px;font-size:0.8rem;font-weight:600;}'
        '.wd-badge.weekend{background:#F2F2F2;color:#888;}'
        '.wd-badge.workday{background:#E8F5E9;color:#2E7D32;}'
        '@media(max-width:480px){'
        '.holiday-table th{padding:0.6rem 0.5rem;font-size:0.7rem;}'
        '.holiday-table td{padding:0.55rem 0.5rem;font-size:0.8rem;}'
        '.holiday-table{border-radius:12px;}'
        '.wd-badge{font-size:0.68rem;padding:0.15rem 0.5rem;}'
        '}'
        '</style></head><body>'
        '<table class="holiday-table">'
        '<thead><tr><th>Feiertag</th><th>Datum</th><th>Wochentag</th></tr></thead>'
        '<tbody>' + ''.join(table_rows) + '</tbody>'
        '</table></body></html>'
    )

    import streamlit.components.v1 as components
    row_count = len(holidays)
    table_height = 58 + row_count * 48 + 20  # header + rows + padding
    components.html(table_html, height=table_height, scrolling=False)

    # ── Footer ──
    st.markdown("""
    <div class="app-footer">
        SwissHolidayOptimizer — Keine Daten werden gespeichert · Berechnung erfolgt lokal ·
        Alle Angaben ohne Gewähr
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
else:
    main()
