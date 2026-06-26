SOLAR_CSS = """
<style>
/* ===== SOLAR CUIDADOS — IDENTIDADE VISUAL ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --solar-primary: #1A5276;
    --solar-secondary: #2E86C1;
    --solar-accent: #F39C12;
    --solar-success: #27AE60;
    --solar-warning: #F39C12;
    --solar-danger: #E74C3C;
    --solar-light: #EBF5FB;
    --solar-dark: #1A2733;
    --solar-gray: #566573;
    --solar-bg: #F4F6F7;
    --solar-card: #FFFFFF;
    --solar-border: #D5DBDB;
    --solar-text: #2C3E50;
    --radius: 12px;
    --shadow: 0 2px 12px rgba(26,82,118,0.10);
    --shadow-hover: 0 6px 24px rgba(26,82,118,0.18);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A5276 0%, #154360 60%, #0E2F44 100%) !important;
    border-right: none !important;
}

section[data-testid="stSidebar"] * {
    color: #EBF5FB !important;
}

section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.5rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.12) !important;
}

/* MAIN AREA */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1400px;
}

/* METRIC CARDS */
.kpi-card {
    background: white;
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    border-left: 4px solid var(--solar-primary);
    transition: all 0.25s ease;
    margin-bottom: 1rem;
}

.kpi-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.kpi-card.accent { border-left-color: var(--solar-accent); }
.kpi-card.success { border-left-color: var(--solar-success); }
.kpi-card.danger { border-left-color: var(--solar-danger); }
.kpi-card.warning { border-left-color: var(--solar-warning); }

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--solar-gray);
    margin-bottom: 0.4rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--solar-primary);
    line-height: 1;
}

.kpi-sub {
    font-size: 0.78rem;
    color: var(--solar-gray);
    margin-top: 0.3rem;
}

/* SECTION HEADER */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid var(--solar-light);
}

.section-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--solar-dark);
}

/* LOGO AREA */
.solar-logo {
    text-align: center;
    padding: 1.5rem 1rem 1rem 1rem;
}

.solar-logo-text {
    font-size: 1.3rem;
    font-weight: 800;
    color: #ffffff !important;
    letter-spacing: 0.05em;
}

.solar-logo-sub {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.65) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 2px;
}

.solar-divider {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.15);
    margin: 1rem 0;
}

/* ALERT CARDS */
.alert-critical {
    background: #FDEDEC;
    border: 1px solid #E74C3C;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    color: #922B21;
    font-size: 0.85rem;
    font-weight: 500;
}

.alert-warning {
    background: #FEF9E7;
    border: 1px solid #F39C12;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    color: #9A7D0A;
    font-size: 0.85rem;
    font-weight: 500;
}

.alert-info {
    background: #EBF5FB;
    border: 1px solid #2E86C1;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    color: #1A5276;
    font-size: 0.85rem;
    font-weight: 500;
}

/* SLA BADGES */
.sla-ok { background:#EAFAF1; color:#1E8449; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.sla-warn { background:#FEF9E7; color:#B7950B; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.sla-late { background:#FDEDEC; color:#922B21; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* PAGE TITLE */
.page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--solar-primary);
    margin-bottom: 0.25rem;
}

.page-subtitle {
    font-size: 0.875rem;
    color: var(--solar-gray);
    margin-bottom: 1.5rem;
}

/* STREAMLIT OVERRIDES */
div[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: var(--shadow);
    border-left: 4px solid #1A5276;
}

.stButton > button {
    background: linear-gradient(135deg, #1A5276, #2E86C1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(26,82,118,0.3) !important;
}

.stSelectbox > div, .stMultiSelect > div {
    border-radius: 8px !important;
}

.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* TAB STYLING */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--solar-light);
    border-radius: 10px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}

.stTabs [aria-selected="true"] {
    background: var(--solar-primary) !important;
    color: white !important;
}
</style>
"""
