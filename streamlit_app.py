"""
SGOI — Sistema de Gestão Operacional da Intercorrência
Solar Cuidados — Versão 1.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import re
from datetime import datetime
from repository.data_repo import get_stats_overview
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

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div class="solar-logo">☀️ <div class="solar-logo-text">Solar Cuidados</div></div>""", unsafe_allow_html=True)
    
    if 'pagina' not in st.session_state: st.session_state['pagina'] = 'inicio'

    menu = [
        ("🏠 Início", "inicio"), 
        ("📊 Escala de Plantão", "escala"),
        ("🔄 Trocas de Ponto", "trocas_ponto"),
        (None, None), ("📊 Dashboard", "dashboard_exec"), 
        ("👥 Pacientes", "pacientes"), ("📞 Ligações", "ligacoes")
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

elif pagina == 'escala':
    st.header("📅 Escala de Plantão — Julho/2026")
    # Carregando a sua planilha (certifique-se de que o arquivo está na pasta correta)
    try:
        df = pd.read_csv("Colaboradores ativos Intercorrência (1).xlsx - Escala mensal julho.csv")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("Erro ao carregar escala: " + str(e))

elif pagina == 'trocas_ponto':
    st.header("🔄 Formalização de Troca")
    input_troca = st.text_area("Cole a formalização recebida no grupo:")
    if st.button("Executar Troca"):
        # Lógica de processamento
        st.info("Processando troca: " + input_troca)
        # Aqui entra a chamada para atualizar o CSV

elif pagina == 'dashboard_exec': from pages.dashboard_exec import render; render()
elif pagina == 'pacientes': from pages.other_pages import page_pacientes; page_pacientes()
elif pagina == 'ligacoes': from pages.other_pages import page_ligacoes; page_ligacoes()
