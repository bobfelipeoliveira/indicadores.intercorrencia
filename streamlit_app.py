"""
SGOI — Sistema de Gestão Operacional da Intercorrência
Solar Cuidados — Versão 1.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="SGOI — Solar Cuidados",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import init_db
init_db()

# Definição de estilo aplicada diretamente para garantir a paleta
st.markdown("""
<style>
    :root {
        --primary-color: #77255c;
        --secondary-color: #f9a031;
    }
    [data-testid="stSidebar"] {
        background-color: #77255c;
        color: white;
    }
    .solar-logo { color: white; text-align: center; padding: 1rem; }
    .solar-logo-text { font-size: 1.5rem; font-weight: bold; }
    .solar-logo-sub { font-size: 0.8rem; opacity: 0.8; }
    .solar-divider { border-top: 1px solid rgba(255,255,255,0.2); }
    
    div.stButton > button {
        border: none !important;
        border-radius: 8px !important;
    }
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #f9a031 !important;
        color: white !important;
        font-weight: bold;
    }
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        color: white !important;
    }
    .alert-warning { background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px; border-left: 5px solid #f9a031; }
    .alert-critical { background-color: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border-left: 5px solid #77255c; }
    .alert-info { background-color: #fdfdfd; color: #333; padding: 1rem; border-radius: 8px; border-left: 5px solid #77255c; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="solar-logo">
        <div style="font-size:2.2rem;margin-bottom:4px;">☀️</div>
        <div class="solar-logo-text">Solar Cuidados</div>
        <div class="solar-logo-sub">Gestão Operacional — Intercorrência</div>
    </div>
    <hr class="solar-divider">
    """, unsafe_allow_html=True)

    busca_global = st.text_input("🔎", placeholder="Pesquisa global...", key="busca_global", label_visibility="collapsed")
    if busca_global:
        st.session_state['pagina'] = 'pesquisa'
        st.session_state['busca_termo'] = busca_global

    st.markdown('<hr class="solar-divider">', unsafe_allow_html=True)

    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'inicio'

    menu = [
        ("🏠 Início", "inicio"),
        ("📊 Dashboard Executivo", "dashboard_exec"),
        ("👔 Dashboard Diretoria", "dashboard_diretoria"),
        ("📅 Indicadores Mensais", "indicadores_mensais"),
        ("📆 Indicadores Anuais", "indicadores_anuais"),
        (None, None),
        ("👥 Pacientes", "pacientes"),
        ("🎫 Tickets", "tickets"),
        ("🔁 Call Back", "call_back"),
        ("📞 Ligações", "ligacoes"),
        ("👁️ Monitoramentos", "monitoramentos"),
        ("⚠️ Pendências", "pendencias"),
        ("🎯 SLA", "sla"),
        (None, None),
        ("📅 Timeline Paciente", "timeline"),
        ("🔍 Central de Causas", "central_causas"),
        ("🌡️ Mapa de Calor", "mapa_calor"),
        (None, None),
        ("📄 Relatórios", "relatorios"),
        ("📤 Importação", "importacao"),
        ("⚙️ Configurações", "configuracoes"),
    ]

    pagina_atual = st.session_state.get('pagina', 'inicio')
    for label, key in menu:
        if key is None:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            continue
        tipo = "primary" if pagina_atual == key else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=tipo):
            st.session_state['pagina'] = key
            if 'busca_termo' in st.session_state:
                del st.session_state['busca_termo']
            st.rerun()

    st.markdown('<hr class="solar-divider">', unsafe_allow_html=True)
    now = datetime.now()
    st.markdown(f"""
    <div style="text-align:center;font-size:0.68rem;color:rgba(255,255,255,0.6);padding:0.5rem;">
        {now.strftime('%d/%m/%Y %H:%M')}<br>Solar Cuidados © 2026
    </div>""", unsafe_allow_html=True)

# ─── ROTEAMENTO ────────────────────────────────────────────────────────────
pagina = st.session_state.get('pagina', 'inicio')

if pagina == 'inicio':
    from repository.data_repo import get_stats_overview, get_tickets, get_monitoramentos
    from utils.charts import kpi_html, section_header

    now = datetime.now()
    hora = now.hour
    saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"

    st.markdown(f"""
    <div style="background-color:#77255c; border-radius:16px; padding:2rem; color:white; margin-bottom:1.5rem; border-bottom: 5px solid #f9a031;">
        <div style="font-size:1rem; opacity:0.8;">{saudacao}! 👋</div>
        <div style="font-size:2rem; font-weight:800;">Solar Cuidados — Intercorrência</div>
        <div style="font-size:0.85rem; opacity:0.7; margin-top:0.4rem;">
            {now.strftime('%A, %d de %B de %Y — %H:%M')}
        </div>
    </div>""", unsafe_allow_html=True)

    stats = get_stats_overview()
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,(label,val,color,icon) in zip([c1,c2,c3,c4,c5,c6],[
        ("Pacientes",f"{stats['total_pacientes']:,}","primary","👥"),
        ("Total Tickets",f"{stats['total_tickets']:,}","primary","🎫"),
        ("Abertos",f"{stats['tickets_abertos']:,}","warning","🔓"),
        ("Ligações",f"{stats['total_ligacoes']:,}","accent","📞"),
        ("Pendências",f"{stats['pendencias_abertas']:,}","danger","⚠️"),
        ("Call Back",f"{stats['call_back_abertos']:,}","danger","🔁"),
    ]):
        with col:
            st.markdown(kpi_html(label,val,"",color,icon), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_header("⚡","Ações Rápidas"), unsafe_allow_html=True)
    ac1,ac2,ac3,ac4,ac5,ac6 = st.columns(6)
    for col, lbl, pg in [(ac1,"🎫 Novo Ticket","tickets"),(ac2,"👁️ Monitoramento","monitoramentos"),(ac3,"👥 Novo Paciente","pacientes"),(ac4,"🔁 Call Back","call_back"),(ac5,"📤 Importar","importacao"),(ac6,"📄 Relatório","relatorios")]:
        with col:
            if st.button(lbl, use_container_width=True):
                st.session_state['pagina'] = pg
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(section_header("🎫","Últimos Tickets"), unsafe_allow_html=True)
        ult = get_tickets()
        if not ult.empty:
            st.dataframe(ult[['numero','paciente_nome','classificacao','status','data_abertura']].head(8), use_container_width=True)
        else:
            st.info("Nenhum ticket encontrado.")
    with col_b:
        st.markdown(section_header("👁️","Monitoramentos Ativos"), unsafe_allow_html=True)
        mons = get_monitoramentos('Ativo')
        if not mons.empty:
            st.dataframe(mons[['paciente_nome','situacao','status','data_registro']].head(8), use_container_width=True)
        else:
            st.info("Nenhum monitoramento ativo.")

    st.markdown(section_header("🚨","Alertas"), unsafe_allow_html=True)
    al1, al2 = st.columns(2)
    with al1:
        if stats.get('tickets_abertos'): st.markdown(f'<div class="alert-warning">⚠️ {stats["tickets_abertos"]} tickets em aberto.</div>', unsafe_allow_html=True)
        if stats.get('ligacoes_abandonadas'): st.markdown(f'<div class="alert-critical">🚨 {stats["ligacoes_abandonadas"]} ligações abandonadas.</div>', unsafe_allow_html=True)
    with al2:
        if stats.get('call_back_abertos'): st.markdown(f'<div class="alert-critical">🔁 {stats["call_back_abertos"]} Call Backs pendentes.</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-info">✅ SGOI operacional — Solar Cuidados</div>', unsafe_allow_html=True)

# Roteamento dos demais módulos
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
elif pagina == 'pesquisa': page_pesquisa(st.session_state.get('busca_termo', ''))
elif pagina == 'configuracoes': from pages.other_pages import page_configuracoes; page_configuracoes()
