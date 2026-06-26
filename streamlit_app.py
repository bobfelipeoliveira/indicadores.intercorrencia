"""
SGOI — Sistema de Gestão Operacional da Intercorrência
Solar Cuidados — Versão 1.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime
from repository.data_repo import get_stats_overview
from utils.charts import kpi_html

st.set_page_config(page_title="SGOI — Solar Cuidados", page_icon="☀️", layout="wide")

# CSS ESTILIZADO PARA O QUADRO
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #77255c; }
    .stDataFrame { border: 2px solid #77255c !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:white;'>☀️ Solar Cuidados</h2>", unsafe_allow_html=True)
    if st.button("🏠 Início", use_container_width=True): st.session_state['pagina'] = 'inicio'
    if st.button("📊 Quadro de Ponto (RH)", use_container_width=True): st.session_state['pagina'] = 'ponto'
    if st.button("🔄 Formalizar Trocas", use_container_width=True): st.session_state['pagina'] = 'trocas'

# ─── ROTEAMENTO E QUADRO DE PONTO ──────────────────────────────────────────
pagina = st.session_state.get('pagina', 'inicio')

if pagina == 'ponto':
    st.header("📋 Controle de Ponto — RH")
    st.info("💡 Dica: Você pode editar as células diretamente abaixo. As alterações serão salvas automaticamente.")
    
    # Carregamento inteligente ignorando as linhas extras do Excel
    try:
        # Ajuste o nome do arquivo para o caminho real no seu servidor
        caminho_csv = "Colaboradores ativos Intercorrência (1).xlsx - Escala mensal julho.csv"
        df = pd.read_csv(caminho_csv, header=2) # header=2 pula as linhas de "Férias/Afastamento"
        
        # Exibe o editor de dados (A mágica do RH)
        edited_df = st.data_editor(
            df, 
            use_container_width=True, 
            height=600,
            column_config={
                "Nome do Funcionário": st.column_config.TextColumn("Colaborador", width="medium"),
            }
        )
        
        if st.button("💾 Salvar Alterações no Ponto"):
            edited_df.to_csv(caminho_csv, index=False)
            st.success("Escala atualizada com sucesso!")
            
    except Exception as e:
        st.error(f"Erro ao carregar escala: {e}")

elif pagina == 'inicio':
    st.title("Início")
    st.write("Selecione 'Quadro de Ponto (RH)' na barra lateral para gerenciar os plantões.")

elif pagina == 'trocas':
    st.header("🔄 Processador de Trocas")
    texto = st.text_area("Cole a mensagem do grupo:")
    if st.button("Executar Automático"):
        # Aqui entra a lógica de regex para atualizar o 'edited_df' automaticamente
        st.write("Processando...")
