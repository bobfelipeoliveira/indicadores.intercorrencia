"""
SGOI — Sistema de Gestão Operacional da Intercorrência
Solar Cuidados — Versão 1.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import re
from datetime import datetime
from repository.data_repo import get_stats_overview, get_tickets, get_monitoramentos
from utils.charts import kpi_html, section_header

st.set_page_config(page_title="SGOI — Solar Cuidados", page_icon="☀️", layout="wide", initial_sidebar_state="expanded")

from database.db import init_db
init_db()

# CSS ATUALIZADO
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #77255c; }
    .solar-logo { color: white; text-align: center; padding: 1rem; }
    .solar-logo-text { font-size: 1.4rem; font-weight: 800; color: #ffffff; }
    .solar-logo-sub { font-size: 0.75rem; color: #f9a031; font-weight: bold; }
    div.stButton > button { border: none !important; border-radius: 6px !important; font-weight: 600 !important; text-align: left !important; }
    div.stButton > button[data-testid="baseButton-primary"] { background-color: #f9a031 !important; color: #222 !important; }
    div.stButton > button[data-testid="baseButton-secondary"] { background-color: transparent !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ─── LÓGICA DE PROCESSAMENTO DE TROCAS ────────────────────────────────────
def processar_troca(texto):
    # Regex simples para buscar: Nome - Data
    # Ex: Sabrina - 28/06
    padrao = r"([a-zA-ZÀ-ÿ\s]+)\s*-\s*(\d{2}/\d{2})"
    matches = re.findall(padrao, texto)
    return matches # Lista de tuplas (Nome, Data)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div class="solar-logo">☀️ <div class="solar-logo-text">Solar Cuidados</div></div>""", unsafe_allow_html=True)
    
    if 'pagina' not in st.session_state: st.session_state['pagina'] = 'inicio'

    menu = [
        ("🏠 Início", "inicio"), ("🔄 Trocas de Ponto", "trocas_ponto"),
        (None, None), ("📊 Dashboard", "dashboard_exec"), ("👥 Pacientes", "pacientes"),
        ("📞 Ligações", "ligacoes"), ("📄 Relatórios", "relatorios")
    ]

    for label, key in menu:
        if key is None:
            st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.1);margin:10px 0'>", unsafe_allow_html=True)
            continue
        if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if st.session_state.get('pagina') == key else "secondary"):
            st.session_state['pagina'] = key
            st.rerun()

# ─── ROTEAMENTO ────────────────────────────────────────────────────────────
pagina = st.session_state.get('pagina', 'inicio')

if pagina == 'inicio':
    st.title("Início")
    stats = get_stats_overview()
    c1, c2, c3, c4 = st.columns(4)
    for col, data in zip([c1,c2,c3,c4], [("Pacientes",stats.get('total_pacientes',0),"👥"), ("Tickets",stats.get('total_tickets',0),"🎫"), ("Abertos",stats.get('tickets_abertos',0),"🔓"), ("Ligações",stats.get('total_ligacoes',0),"📞")]):
        with col: st.markdown(kpi_html(data[0], data[1], "", "primary", data[2]), unsafe_allow_html=True)

elif pagina == 'trocas_ponto':
    st.header("🔄 Formalização de Troca")
    st.info("Cole o formato: Nome - Data (Ex: Sabrina - 28/06)")
    
    input_troca = st.text_area("Cole a formalização aqui:")
    if st.button("Executar Troca"):
        resultado = processar_troca(input_troca)
        if resultado:
            st.success(f"Troca processada para: {resultado}")
            # AQUI VOCÊ ADICIONA A CHAMADA PARA O SEU BANCO DE DADOS
            # Ex: update_escala_banco(resultado)
        else:
            st.error("Formato inválido. Use: Nome - Data")

elif pagina == 'dashboard_exec': from pages.dashboard_exec import render; render()
# ... (restante das outras páginas)
