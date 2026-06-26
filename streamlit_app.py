import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SGOI — Solar Cuidados", layout="wide")

# ─── CONFIGURAÇÃO DO QUADRO ──────────────────────────────────────────
def carregar_escala_limpa():
    # Caminho do seu arquivo (ajuste conforme necessário)
    arquivo = "Colaboradores ativos Intercorrência (1).xlsx - Escala mensal julho.csv"
    if not os.path.exists(arquivo):
        return pd.DataFrame()
    
    # header=2 pula as linhas de Férias/Afastamento e vai direto para os títulos
    df = pd.read_csv(arquivo, header=2)
    
    # Selecionar apenas colunas essenciais para o quadro de RH
    colunas_interesse = ['Nome do Funcionário', 'Função', 'Turno'] + [str(i) for i in range(1, 32)]
    df = df[colunas_interesse].dropna(subset=['Nome do Funcionário'])
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☀️ Solar Cuidados")
    pagina = st.radio("Navegação", ["Início", "Quadro de Ponto", "Trocas"])

# ─── PÁGINA: QUADRO DE PONTO ──────────────────────────────────────────
if pagina == "Quadro de Ponto":
    st.header("📋 Quadro de Ponto — RH")
    
    df = carregar_escala_limpa()
    
    if not df.empty:
        # Editando o quadro
        edited_df = st.data_editor(
            df, 
            use_container_width=True,
            column_config={
                "Nome do Funcionário": st.column_config.TextColumn("Colaborador", disabled=True),
                "Função": st.column_config.TextColumn("Função"),
                "Turno": st.column_config.SelectboxColumn("Turno", options=["Diurno", "Noturno"])
            }
        )
        
        # Legenda automática
        st.markdown("""
        **Legenda de Controle:**
        * `x` = Trabalhando | `F` = Folga | `T` = Troca | `A` = Ausência
        """)
    else:
        st.error("Não foi possível carregar a planilha. Verifique se o nome do arquivo está correto.")

elif pagina == "Início":
    st.title("Bem-vindo, Gestor")
    st.write("Use o menu lateral para acessar o Quadro de Ponto.")
