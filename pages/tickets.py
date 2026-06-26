import streamlit as st
import pandas as pd
from datetime import date, datetime
from repository.data_repo import get_tickets, save_ticket, get_pacientes
from utils.charts import section_header, kpi_html
import io

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()

def render_ticket_table(df, key_prefix):
    if df.empty:
        st.info("Nenhum ticket encontrado com os filtros aplicados.")
        return

    # Stats rápidas
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Total",str(len(df)),"Tickets","primary","🎫"), unsafe_allow_html=True)
    with c2:
        ab = (df['status'] == 'Aberto').sum()
        st.markdown(kpi_html("Abertos",str(ab),"","warning","🔓"), unsafe_allow_html=True)
    with c3:
        fe = (df['status'] == 'Fechado').sum()
        st.markdown(kpi_html("Fechados",str(fe),"","success","✅"), unsafe_allow_html=True)
    with c4:
        avg_h = df['horas_consumidas'].mean() if 'horas_consumidas' in df.columns else 0
        avg_h = 0 if pd.isna(avg_h) else avg_h
        st.markdown(kpi_html("Tempo Médio",f"{avg_h:.1f}h","Horas consumidas","accent","⏱️"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Export
    colx1, colx2 = st.columns([8,2])
    with colx2:
        st.download_button("📥 Exportar Excel", to_excel(df), "tickets.xlsx",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          key=f"{key_prefix}_export")

    # Tabela
    cols_show = ['numero','paciente_nome','operadora','classificacao','motivo',
                 'data_abertura','data_encerramento','horas_consumidas','status','status_prazo','responsavel']
    cols_show = [c for c in cols_show if c in df.columns]
    display_df = df[cols_show].copy()
    display_df.columns = ['Número','Paciente','Operadora','Tipo','Motivo',
                          'Abertura','Encerramento','Horas','Status','Status Prazo','Responsável'][:len(cols_show)]

    def color_status(val):
        if val == 'Aberto':
            return 'color: #E67E22; font-weight: bold'
        elif val == 'Fechado':
            return 'color: #27AE60; font-weight: bold'
        return ''

    styled = display_df.style
    if 'Status' in display_df.columns:
        styled = styled.applymap(color_status, subset=['Status'])

    st.dataframe(styled, use_container_width=True, height=420)

def render():
    st.markdown("""
    <div class="page-title">🎫 Tickets</div>
    <div class="page-subtitle">Gestão completa de tickets operacionais</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏥 Criados pela Intercorrência", "📩 Recebidos de Outras Áreas", "➕ Novo Ticket"])

    # ---- TAB 1: Intercorrência ----
    with tab1:
        st.markdown(section_header("🏥","Tickets Criados pela Intercorrência"), unsafe_allow_html=True)

        with st.expander("🔍 Filtros", expanded=True):
            f1,f2,f3,f4 = st.columns(4)
            with f1:
                busca = st.text_input("🔎 Buscar", placeholder="Paciente, número, descrição...", key="t1_busca")
            with f2:
                status = st.selectbox("Status", ["Todos","Aberto","Fechado"], key="t1_status")
            with f3:
                mes = st.selectbox("Mês", ["Todos","2026-05","2026-06"], key="t1_mes")
            with f4:
                area = st.text_input("Área", key="t1_area")

        filters = {'criado_por': 'Intercorrência'}
        if busca: filters['busca'] = busca
        if status != "Todos": filters['status'] = status
        if mes != "Todos": filters['mes'] = mes

        df = get_tickets(filters)
        render_ticket_table(df, "t1")

    # ---- TAB 2: Outras Áreas ----
    with tab2:
        st.markdown(section_header("📩","Tickets Recebidos de Outras Áreas"), unsafe_allow_html=True)

        with st.expander("🔍 Filtros", expanded=True):
            f1b,f2b,f3b = st.columns(3)
            with f1b:
                busca2 = st.text_input("🔎 Buscar", placeholder="Paciente, número...", key="t2_busca")
            with f2b:
                status2 = st.selectbox("Status", ["Todos","Aberto","Fechado"], key="t2_status")
            with f3b:
                mes2 = st.selectbox("Mês", ["Todos","2026-05","2026-06"], key="t2_mes")

        # For now shows all tickets not created by Intercorrencia
        # In production, add 'area_destino' field
        filters2 = {}
        if busca2: filters2['busca'] = busca2
        if status2 != "Todos": filters2['status'] = status2
        if mes2 != "Todos": filters2['mes'] = mes2

        df2 = get_tickets(filters2)
        # Filter for tickets received from other areas (placeholder logic)
        df2_ext = df2[df2.get('area', pd.Series(dtype=str)).str.contains('CRC|EXTERNO', na=False, case=False)] if 'area' in df2.columns else pd.DataFrame()
        if df2_ext.empty:
            st.info("📋 Nenhum ticket de outras áreas registrado. Utilize o formulário para cadastrar tickets recebidos.")
        else:
            render_ticket_table(df2_ext, "t2")

    # ---- TAB 3: Novo Ticket ----
    with tab3:
        st.markdown(section_header("➕","Novo Ticket"), unsafe_allow_html=True)

        with st.form("form_ticket"):
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                numero = st.text_input("Número do Ticket *", placeholder="Ex: 125001")
            with r1c2:
                pacientes = get_pacientes()
                pac_opts = [""] + list(pacientes['nome'].values) if not pacientes.empty else [""]
                paciente_nome = st.selectbox("Paciente *", pac_opts)
            with r1c3:
                operadora = st.selectbox("Operadora", ["","AMIL","BRADESCO SAÚDE","UNIMED BRASIL","SULAMERICA","OUTROS"])

            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            with r2c1:
                area = st.selectbox("Área", ["CI-INTERCORRENCIA","CRC","ENFERMAGEM","FISIOTERAPIA","OUTROS"])
            with r2c2:
                origem = st.selectbox("Origem", ["RECEPTIVO","ATIVO","EMAIL","WHATSAPP","OUTROS"])
            with r2c3:
                tipo = st.selectbox("Tipo", ["Solicitação","Informação","Manifestação","Reclamação","Ocorrência"])
            with r2c4:
                classificacao = st.selectbox("Classificação", ["SOLICITAÇÃO","INFORMAÇÃO","MANIFESTAÇÃO","OUTRAS ATIVIDADES"])

            r3c1, r3c2 = st.columns(2)
            with r3c1:
                motivo = st.text_input("Motivo", placeholder="Ex: RECARGA, TROCA EQUIPAMENTO...")
            with r3c2:
                responsavel = st.text_input("Responsável", placeholder="Nome do responsável")

            descricao = st.text_area("Descrição *", height=120, placeholder="Descreva detalhadamente a demanda...")

            r4c1, r4c2, r4c3 = st.columns(3)
            with r4c1:
                prioridade = st.selectbox("Prioridade", ["Normal","Alta","Crítica","Baixa"])
            with r4c2:
                data_abertura = st.date_input("Data de Abertura", value=date.today())
            with r4c3:
                criado_por = st.selectbox("Criado por", ["Intercorrência","Outra Área"])

            observacoes = st.text_area("Observações", height=80)

            submitted = st.form_submit_button("💾 Salvar Ticket", use_container_width=True)

            if submitted:
                if not numero or not descricao:
                    st.error("❌ Preencha os campos obrigatórios: Número e Descrição.")
                else:
                    try:
                        save_ticket({
                            'numero': numero, 'paciente_nome': paciente_nome,
                            'area': area, 'origem': origem, 'tipo': tipo,
                            'classificacao': classificacao, 'descricao': descricao,
                            'motivo': motivo, 'status': 'Aberto', 'prioridade': prioridade,
                            'prazo': '', 'data_abertura': str(data_abertura),
                            'responsavel': responsavel, 'observacoes': observacoes,
                            'criado_por': criado_por, 'operadora': operadora
                        })
                        st.success(f"✅ Ticket **{numero}** salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")
