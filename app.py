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
/* ── Import Helvetica-like Google font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}

.stApp {
    background: linear-gradient(165deg, #FAFAFA 0%, #F0F0F0 100%);
}

/* ── Remove Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #D50000 0%, #FF1744 40%, #FF5252 100%);
    padding: 2.5rem 3rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(213, 0, 0, 0.25);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero h1 {
    color: #FFFFFF;
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.03em;
}
.hero p {
    color: rgba(255,255,255,0.88);
    font-size: 1.15rem;
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.01em;
}

/* ── Control panel ── */
.control-panel {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
}

/* ── Section titles ── */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1A1A1A;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    letter-spacing: -0.01em;
}

/* ── Holiday table ── */
.holiday-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}
.holiday-table thead {
    background: linear-gradient(135deg, #D50000, #FF1744);
}
.holiday-table th {
    color: #FFFFFF;
    padding: 1rem 1.2rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.holiday-table td {
    padding: 0.85rem 1.2rem;
    color: #2C2C2C;
    font-size: 0.95rem;
    border-bottom: 1px solid #F0F0F0;
}
.holiday-table tr:last-child td {
    border-bottom: none;
}
.holiday-table tbody tr {
    background: #FFFFFF;
    transition: background 0.15s ease;
}
.holiday-table tbody tr:hover {
    background: #FFF5F5;
}
.holiday-table tbody tr:nth-child(even) {
    background: #FAFAFA;
}
.holiday-table tbody tr:nth-child(even):hover {
    background: #FFF5F5;
}

/* ── Weekday badges ── */
.wd-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
}
.wd-badge.weekend { background: #F3E5F5; color: #7B1FA2; }
.wd-badge.workday { background: #E3F2FD; color: #1565C0; }

/* ── Recommendation cards ── */
.rec-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF8F8 100%);
    border-left: 4px solid #D50000;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.rec-card:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(213,0,0,0.12);
}
.rec-card .rec-title {
    font-weight: 700;
    color: #D50000;
    font-size: 1rem;
    margin-bottom: 0.3rem;
}
.rec-card .rec-text {
    color: #444;
    font-size: 0.95rem;
    line-height: 1.5;
}
.rec-card .rec-days {
    display: inline-block;
    background: #D50000;
    color: #FFF;
    padding: 0.15rem 0.55rem;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Calendar grid ── */
.cal-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.cal-month {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
}
.cal-month-title {
    font-weight: 700;
    font-size: 1rem;
    color: #1A1A1A;
    text-align: center;
    margin-bottom: 0.8rem;
    letter-spacing: -0.01em;
}
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}
.cal-header {
    text-align: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: #999;
    padding: 0.3rem 0;
    text-transform: uppercase;
}
.cal-day {
    text-align: center;
    padding: 0.35rem 0.1rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    color: #333;
    transition: transform 0.1s ease;
    position: relative;
}
.cal-day.empty { visibility: hidden; }
.cal-day.weekend {
    color: #999;
    background: #F5F5F5;
}
.cal-day.holiday {
    background: linear-gradient(135deg, #D50000, #FF1744);
    color: #FFFFFF;
    font-weight: 700;
    box-shadow: 0 2px 6px rgba(213,0,0,0.3);
}
.cal-day.bridge {
    background: linear-gradient(135deg, #FF6D00, #FF9100);
    color: #FFFFFF;
    font-weight: 700;
    box-shadow: 0 2px 6px rgba(255,109,0,0.3);
}
.cal-day.today {
    outline: 2px solid #D50000;
    outline-offset: -1px;
}
.cal-day.holiday:hover,
.cal-day.bridge:hover {
    transform: scale(1.25);
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
    background: #1A1A1A;
    color: #FFF;
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
    pointer-events: none;
    box-shadow: 0 3px 12px rgba(0,0,0,0.2);
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
    border-top-color: #1A1A1A;
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
    padding: 1rem 1.5rem;
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: #555;
    font-weight: 500;
}
.legend-dot {
    width: 14px;
    height: 14px;
    border-radius: 5px;
}
.legend-dot.holiday-dot { background: linear-gradient(135deg, #D50000, #FF1744); }
.legend-dot.bridge-dot  { background: linear-gradient(135deg, #FF6D00, #FF9100); }
.legend-dot.weekend-dot { background: #F5F5F5; border: 1px solid #DDD; }
.legend-dot.today-dot   { background: #FFFFFF; border: 2px solid #D50000; }

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.stat-chip {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 0.9rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    display: flex;
    align-items: center;
    gap: 0.7rem;
    flex: 1;
    min-width: 160px;
    border: 1px solid rgba(0,0,0,0.04);
}
.stat-chip .stat-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #D50000;
    line-height: 1;
}
.stat-chip .stat-label {
    font-size: 0.82rem;
    color: #777;
    font-weight: 500;
    line-height: 1.3;
}

/* ── Download button override ── */
.stDownloadButton button {
    background: linear-gradient(135deg, #D50000, #FF1744) !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: 0 4px 16px rgba(213,0,0,0.25) !important;
}
.stDownloadButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(213,0,0,0.35) !important;
}

/* ── Primary button override ── */
.stButton > button[kind="primary"], .stButton > button {
    background: linear-gradient(135deg, #D50000, #FF1744) !important;
    color: #FFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: 0 4px 16px rgba(213,0,0,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(213,0,0,0.35) !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #999;
    font-size: 1.1rem;
}
.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 2rem;
    color: #AAA;
    font-size: 0.82rem;
    margin-top: 2rem;
    border-top: 1px solid #EEE;
}

/* ── Mobile Responsive ── */
@media (max-width: 768px) {
    .hero {
        padding: 1.5rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        font-size: 1.6rem;
    }
    .hero p {
        font-size: 0.95rem;
    }

    .stats-bar {
        gap: 0.6rem;
    }
    .stat-chip {
        min-width: 0;
        flex: 1 1 45%;
        padding: 0.7rem 0.9rem;
    }
    .stat-chip .stat-number {
        font-size: 1.4rem;
    }
    .stat-chip .stat-label {
        font-size: 0.75rem;
    }

    .cal-container {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 0.7rem;
    }
    .cal-month {
        padding: 0.8rem 0.5rem;
        border-radius: 10px;
    }
    .cal-month-title {
        font-size: 0.88rem;
    }
    .cal-day {
        padding: 0.25rem 0;
        font-size: 0.72rem;
        border-radius: 6px;
    }
    .cal-header {
        font-size: 0.6rem;
    }

    .rec-card {
        padding: 1rem 1.1rem;
    }
    .rec-card .rec-title {
        font-size: 0.9rem;
    }
    .rec-card .rec-text {
        font-size: 0.85rem;
    }

    .legend {
        gap: 0.8rem;
        padding: 0.8rem 1rem;
    }
    .legend-item {
        font-size: 0.78rem;
    }

    .section-title {
        font-size: 1.1rem;
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
        <h1>🇨🇭 SwissHolidayOptimizer</h1>
        <p>Maximiere deine freien Tage — finde die besten Brückentage für deinen Kanton.</p>
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
        calculate = st.button("🔍 Optimierung berechnen", use_container_width=True)

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
    st.markdown('<div class="section-title">📅 Jahreskalender</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="section-title">💡 Brückentag-Empfehlungen</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="section-title">📤 Kalender-Export</div>', unsafe_allow_html=True)

        ical_data = generate_ical(recommendations, canton, int(year))
        ical_bytes = ical_data.encode("utf-8")
        st.download_button(
            label="📅 In Kalender exportieren (.ics)",
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
    st.markdown('<div class="section-title">📋 Alle Feiertage</div>', unsafe_allow_html=True)

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
        '<html><head><style>'
        '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");'
        'body{margin:0;padding:0;font-family:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif;background:transparent;}'
        '.holiday-table{width:100%;border-collapse:separate;border-spacing:0;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.05);}'
        '.holiday-table thead{background:linear-gradient(135deg,#D50000,#FF1744);}'
        '.holiday-table th{color:#FFF;padding:1rem 1.2rem;text-align:left;font-weight:600;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.06em;}'
        '.holiday-table td{padding:0.85rem 1.2rem;color:#2C2C2C;font-size:0.95rem;border-bottom:1px solid #F0F0F0;}'
        '.holiday-table tr:last-child td{border-bottom:none;}'
        '.holiday-table tbody tr{background:#FFF;transition:background 0.15s ease;}'
        '.holiday-table tbody tr:hover{background:#FFF5F5;}'
        '.holiday-table tbody tr:nth-child(even){background:#FAFAFA;}'
        '.holiday-table tbody tr:nth-child(even):hover{background:#FFF5F5;}'
        '.wd-badge{display:inline-block;padding:0.2rem 0.6rem;border-radius:6px;font-size:0.82rem;font-weight:600;}'
        '.wd-badge.weekend{background:#F3E5F5;color:#7B1FA2;}'
        '.wd-badge.workday{background:#E3F2FD;color:#1565C0;}'
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
