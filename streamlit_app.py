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

# CSS OTIMIZADO PARA CONTRASTE
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #77255c;
    }
    .solar-logo { color: white; text-align: center; padding: 1rem; }
    .solar-logo-text { font-size: 1.4rem; font-weight: 800; color: #ffffff; }
    .solar-logo-sub { font-size: 0.75rem; color: #f9a031; font-weight: bold; }
    
    /* Ajuste dos botões da sidebar para leitura clara */
    div.stButton > button {
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    /* Botão ativo (Laranja com texto escuro) */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #f9a031 !important;
        color: #333 !important;
    }
    /* Botão inativo (Roxo mais claro com texto branco) */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }
    div.stButton > button:hover { background-color: rgba(255,255,255,0.2) !important; }
    
    .stTextInput > div > div > input { background-color: rgba(255,255,255,0.9); }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="solar-logo">
        <div style="font-size:2rem;">☀️</div>
        <div class="solar-logo-text">Solar Cuidados</div>
        <div class="solar-logo-sub">Gestão Operacional</div>
    </div>
    """, unsafe_allow_html=True)

    busca_global = st.text_input("🔎", placeholder="Pesquisa global...", key="busca_global", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)

    if 'pagina' not in st.session_state: st.session_state['pagina'] = 'inicio'

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
    ]

    pagina_atual = st.session_state.get('pagina', 'inicio')
    for label, key in menu:
        if key is None:
            st.markdown("<hr style='border:0;border-top:1px solid rgba(255,255,255,0.1);margin:10px 0'>", unsafe_allow_html=True)
            continue
        tipo = "primary" if pagina_atual == key else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=tipo):
            st.session_state['pagina'] = key
            st.rerun()

# ─── ROTEAMENTO ────────────────────────────────────────────────────────────
pagina = st.session_state.get('pagina', 'inicio')

# (Mantém a lógica de carregamento de páginas igual ao seu original)
if pagina == 'inicio':
    st.title("Bem-vindo ao SGOI")
    st.write("Selecione uma opção no menu lateral.")
else:
    # Lógica de roteamento das demais páginas...
    pass
