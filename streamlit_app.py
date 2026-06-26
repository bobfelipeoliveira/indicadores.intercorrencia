"""
SGOI — Sistema de Gestão Operacional da Intercorrência
Solar Cuidados — Versão 1.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from datetime import datetime
from repository.data_repo import get_stats_overview, get_tickets, get_monitoramentos
from utils.charts import kpi_html, section_header

st.set_page_config(
    page_title="SGOI — Solar Cuidados",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import init_db
init_db()

# CSS COMPLETO
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #77255c; }
    .solar-logo { color: white; text-align: center; padding: 1rem; }
    .solar-logo-text { font-size: 1.4rem; font-weight: 800; color: #ffffff; }
    .solar-logo-sub { font-size: 0.75rem; color: #f9a031; font-weight: bold; }
    div.stButton > button { border: none !important; border-radius: 6px !important; font-weight: 600 !important; text-align: left !important; }
    div.stButton > button[data-testid="baseButton-primary"] { background-color: #f9a031 !important; color: #222 !important; }
    div.stButton > button[data-testid="baseButton-secondary"] { background-color: transparent !important; color: #ffffff !important; }
    div.stButton > button:hover { background-color: rgba(255,255,255,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="solar-logo">
        <div style="font-size:2rem;">☀️</div>
        <div class="solar-logo-text">Solar Cuidados</div>
        <div class="solar-logo-sub">Gestão Operacional — Intercorrência</div>
    </div>
    """, unsafe_allow_html=True)

    busca_global = st.text_input("🔎", placeholder="Pesquisa global...", key="busca_global", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    if 'pagina' not in st.session_state: st.session_state['pagina'] = 'inicio'

    menu = [
        ("🏠 Início", "inicio"), ("📊 Dashboard Executivo", "dashboard_exec"),
        ("👔 Dashboard Diretoria", "dashboard_diretoria"), ("📅 Indicadores Mensais", "indicadores_mensais"),
        ("📆 Indicadores Anuais", "indicadores_anuais"), (None, None),
        ("👥 Pacientes", "pacientes"), ("🎫 Tickets", "tickets"), ("🔁 Call Back", "call_back"),
        ("📞 Ligações", "ligacoes"), ("👁️ Monitoramentos", "monitoramentos"), ("⚠️ Pendências", "pendencias"),
        ("🎯 SLA", "sla"), (None, None), ("📅 Timeline Paciente", "timeline"),
        ("🔍 Central de Causas", "central_causas"), ("🌡️ Mapa de Calor", "mapa_calor"),
        (None, None), ("📄 Relatórios", "relatorios"), ("📤 Importação", "importacao"), ("⚙️ Configurações", "configuracoes"),
    ]

    for label, key in menu:
        if key is None:
            st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.1);margin:10px 0'>", unsafe_allow_html=True)
            continue
        if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if st.session_state.get('pagina') == key else "secondary"):
            st.session_state['pagina'] = key
            st.rerun()

# ─── ROTEAMENTO E PÁGINA INICIAL ──────────────────────────────────────────
pagina = st.session_state.get('pagina', 'inicio')

if pagina == 'inicio':
    st.title("Início")
    stats = get_stats_overview()
    
    # KPIs - Adicionando "Transferidas"
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_data = [
        ("Pacientes", stats.get('total_pacientes', 0), "👥"),
        ("Tickets", stats.get('total_tickets', 0), "🎫"),
        ("Abertos", stats.get('tickets_abertos', 0), "🔓"),
        ("Ligações", stats.get('total_ligacoes', 0), "📞"),
        ("Transferidas", stats.get('ligacoes_transferidas', 0), "➡️")
    ]
    
    for col, data in zip([c1, c2, c3, c4, c5], kpi_data):
        with col: 
            st.markdown(kpi_html(data[0], data[1], "", "primary", data[2]), unsafe_allow_html=True)

elif pagina == 'dashboard_exec': from pages.dashboard_exec import render; render()
elif pagina == 'dashboard_diretoria': from pages.dashboard_diretoria import render; render()
elif pagina == 'indicadores_mensais': from pages.indicadores_mensais import render; render()
elif pagina == 'indicadores_anuais': from pages.other_pages import page_indicadores_anuais; page_indicadores_anuais()
elif pagina == 'pacientes': from pages.other_pages import page_pacientes; page_pacientes()
elif pagina == 'tickets': from pages.tickets import render; render()
elif pagina == 'call_back': from pages.other_pages import page_call_back; page_call_back()
elif pagina == 'ligacoes': from pages.other_pages import page_ligacoes; page_ligacoes()
elif pagina == 'monitoramentos': from pages.other_pages import page_monitoramentos; page_monitoramentos()
elif pagina == 'pendencias': from pages.other_pages import page_pendencias; page_pendencias()
elif pagina == 'sla': from pages.other_pages import page_sla; page_sla()
elif pagina == 'timeline': from pages.other_pages import page_timeline; page_timeline()
elif pagina == 'central_causas': from pages.other_pages import page_central_causas; page_central_causas()
elif pagina == 'mapa_calor': from pages.other_pages import page_mapa_calor; page_mapa_calor()
elif pagina == 'relatorios': from pages.other_pages import page_relatorios; page_relatorios()
elif pagina == 'importacao': from pages.other_pages import page_importacao; page_importacao()
elif pagina == 'configuracoes': from pages.other_pages import page_configuracoes; page_configuracoes()
