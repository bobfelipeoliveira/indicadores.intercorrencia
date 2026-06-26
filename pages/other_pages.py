"""
Pages module — all secondary pages.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from repository.data_repo import (
    get_pacientes, get_ligacoes, get_monitoramentos, get_pendencias,
    get_call_back, get_tickets, save_paciente, save_monitoramento,
    save_pendencia, get_tickets_por_motivo, get_tickets_por_categoria,
    get_timeline_paciente, get_indicadores_diarios, search_global
)
from utils.charts import (
    bar_chart, line_chart, pie_chart, heatmap_chart,
    kpi_html, section_header, SOLAR_COLORS
)
import io


# ================================================================
#  PACIENTES
# ================================================================
def page_pacientes():
    st.markdown('<div class="page-title">👥 Pacientes</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Listagem & Busca","➕ Novo Paciente"])

    with tab1:
        busca = st.text_input("🔎 Buscar paciente", placeholder="Digite o nome...")
        df = get_pacientes(busca)
        st.markdown(f"**{len(df)} paciente(s) encontrado(s)**")
        if not df.empty:
            for _, row in df.iterrows():
                with st.expander(f"👤 {row['nome']}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Operadora:** {row.get('operadora','—')}")
                    with c2:
                        st.write(f"**Telefone:** {row.get('telefone','—')}")
                    with c3:
                        st.write(f"**Status:** {row.get('status','Ativo')}")

                    # Tickets deste paciente
                    tks = get_tickets({'paciente': row['nome']})
                    if not tks.empty:
                        st.write(f"**Tickets:** {len(tks)}")
                        st.dataframe(tks[['numero','classificacao','motivo','data_abertura','status']].head(5),
                                     use_container_width=True)
        else:
            st.info("Nenhum paciente encontrado.")

    with tab2:
        with st.form("form_paciente"):
            nome = st.text_input("Nome Completo *")
            c1, c2 = st.columns(2)
            with c1:
                operadora = st.selectbox("Operadora", ["","AMIL","BRADESCO SAÚDE","UNIMED BRASIL","SULAMERICA","OUTROS"])
                telefone = st.text_input("Telefone")
            with c2:
                status = st.selectbox("Status", ["Ativo","Inativo"])
                obs = st.text_area("Observações", height=80)
            if st.form_submit_button("💾 Salvar Paciente", use_container_width=True):
                if not nome:
                    st.error("Nome é obrigatório.")
                else:
                    save_paciente({'nome': nome, 'operadora': operadora, 'telefone': telefone,
                                   'data_cadastro': str(date.today()), 'status': status, 'observacoes': obs})
                    st.success(f"✅ Paciente **{nome}** cadastrado!")
                    st.rerun()


# ================================================================
#  LIGAÇÕES
# ================================================================
def page_ligacoes():
    st.markdown('<div class="page-title">📞 Ligações</div>', unsafe_allow_html=True)

    mes = st.selectbox("Mês", ["2026-06","2026-05"], key="lig_mes")
    df = get_ligacoes(mes)

    if df.empty:
        st.info("Sem dados de ligações. Importe o arquivo Excel.")
        return

    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
    df = df.dropna(subset=['data_hora'])
    df['hora'] = df['data_hora'].dt.hour
    df['dia'] = df['data_hora'].dt.date
    df['dia_semana'] = df['data_hora'].dt.day_name()

    total = len(df)
    atendidas = total - int(df['abandonada'].sum())
    abandonadas = int(df['abandonada'].sum())
    sla = round(atendidas/total*100,1) if total > 0 else 0

    c1,c2,c3,c4 = st.columns(4)
    kpis = [
        (c1,"Total",f"{total:,}","primary","📞"),
        (c2,"Atendidas",f"{atendidas:,}","success","✅"),
        (c3,"Abandonadas",f"{abandonadas:,}","danger","📵"),
        (c4,"SLA",f"{sla}%","accent","🎯"),
    ]
    for col, label, val, color, icon in kpis:
        with col:
            st.markdown(kpi_html(label, val, "", color, icon), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Por hora
    st.markdown(section_header("⏰","Ligações por Hora do Dia"), unsafe_allow_html=True)
    hora_grp = df.groupby('hora').agg(total=('id','count'), abandonadas=('abandonada','sum')).reset_index()
    hora_grp['atendidas'] = hora_grp['total'] - hora_grp['abandonadas']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Atendidas', x=hora_grp['hora'], y=hora_grp['atendidas'], marker_color=SOLAR_COLORS['success']))
    fig.add_trace(go.Bar(name='Abandonadas', x=hora_grp['hora'], y=hora_grp['abandonadas'], marker_color=SOLAR_COLORS['danger']))
    fig.update_layout(barmode='stack', height=300, paper_bgcolor='white', plot_bgcolor='white',
                      font=dict(family='Inter'), margin=dict(l=10,r=10,t=20,b=10),
                      xaxis=dict(dtick=1, showgrid=False), yaxis=dict(gridcolor='#EBF5FB'))
    st.plotly_chart(fig, use_container_width=True)

    # Por dia
    st.markdown(section_header("📅","Volume por Dia"), unsafe_allow_html=True)
    dia_grp = df.groupby('dia').agg(total=('id','count')).reset_index()
    dia_grp['dia'] = dia_grp['dia'].astype(str)
    fig2 = bar_chart(dia_grp, 'dia', 'total', height=280)
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # Ranking grupos
    st.markdown(section_header("🏆","Ranking por Grupo"), unsafe_allow_html=True)
    grp = df.groupby('grupo_inicial').size().reset_index(name='total').sort_values('total', ascending=False).head(10)
    fig3 = bar_chart(grp, 'grupo_inicial', 'total', color=SOLAR_COLORS['secondary'], height=280)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(section_header("📋","Detalhamento das Ligações"), unsafe_allow_html=True)
    cols = ['call_id','data_hora','telefone_externo','agente_inicial','agente_final','grupo_inicial','duracao','abandonada']
    cols = [c for c in cols if c in df.columns]
    st.dataframe(df[cols].head(200), use_container_width=True, height=350)


# ================================================================
#  MONITORAMENTOS
# ================================================================
def page_monitoramentos():
    st.markdown('<div class="page-title">👁️ Monitoramentos</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Ativos","➕ Novo Monitoramento"])

    with tab1:
        status_f = st.selectbox("Status", ["","Ativo","Finalizado","Aguardando"], key="mon_status")
        df = get_monitoramentos(status_f)
        if df.empty:
            st.info("Nenhum monitoramento encontrado.")
        else:
            st.markdown(f"**{len(df)} registro(s)**")
            for _, row in df.iterrows():
                prioridade_cor = "#E74C3C" if row.get('status') == 'Crítico' else "#1A5276"
                with st.expander(f"👁️ {row.get('paciente_nome','—')} — {row.get('situacao','—')}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Conduta:** {row.get('conduta','—')}")
                        st.write(f"**Pendência:** {row.get('pendencia','—')}")
                    with c2:
                        st.write(f"**Status:** {row.get('status','—')}")
                        st.write(f"**Próxima Ação:** {row.get('proxima_acao','—')} em {row.get('data_proxima_acao','—')}")
                    if row.get('observacoes'):
                        st.info(f"📝 {row['observacoes']}")

    with tab2:
        with st.form("form_mon"):
            pac_opts = [""] + list(get_pacientes()['nome'].values)
            c1, c2 = st.columns(2)
            with c1:
                pac = st.selectbox("Paciente *", pac_opts)
                situacao = st.text_area("Situação Clínica *", height=80)
            with c2:
                conduta = st.text_area("Conduta", height=80)
                pendencia = st.text_input("Pendência")
            c3, c4, c5 = st.columns(3)
            with c3:
                status = st.selectbox("Status", ["Ativo","Aguardando","Crítico","Finalizado"])
            with c4:
                prox = st.text_input("Próxima Ação")
            with c5:
                data_prox = st.date_input("Data Próxima Ação", value=date.today())
            responsavel = st.text_input("Responsável")
            obs = st.text_area("Observações", height=60)

            if st.form_submit_button("💾 Registrar Monitoramento", use_container_width=True):
                if not pac or not situacao:
                    st.error("Paciente e Situação são obrigatórios.")
                else:
                    save_monitoramento({
                        'paciente_nome': pac, 'situacao': situacao, 'pendencia': pendencia,
                        'conduta': conduta, 'status': status, 'proxima_acao': prox,
                        'data_proxima_acao': str(data_prox), 'observacoes': obs,
                        'data_registro': str(date.today()), 'responsavel': responsavel
                    })
                    st.success("✅ Monitoramento registrado!")
                    st.rerun()


# ================================================================
#  PENDÊNCIAS
# ================================================================
def page_pendencias():
    st.markdown('<div class="page-title">⚠️ Pendências</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Painel de Pendências","➕ Nova Pendência"])

    with tab1:
        status_f = st.selectbox("Status", ["","Aberta","Resolvida","Em Andamento"])
        df = get_pendencias(status_f)
        if df.empty:
            st.info("Nenhuma pendência encontrada.")
        else:
            # Color by priority
            def badge(p):
                if p == 'Crítica': return '🔴'
                if p == 'Alta': return '🟠'
                if p == 'Normal': return '🟡'
                return '🟢'

            st.markdown(f"**{len(df)} pendência(s)**")
            st.dataframe(df[['paciente_nome','origem','tipo','prioridade','prazo','status','responsavel','proxima_acao']],
                         use_container_width=True, height=450)

    with tab2:
        with st.form("form_pend"):
            c1, c2 = st.columns(2)
            with c1:
                pac = st.text_input("Paciente")
                tipo = st.text_input("Tipo")
                prazo = st.date_input("Prazo", value=date.today())
            with c2:
                origem = st.selectbox("Origem", ["Intercorrência","CRC","Médico","Família","Outros"])
                prioridade = st.selectbox("Prioridade", ["Normal","Alta","Crítica","Baixa"])
                responsavel = st.text_input("Responsável")
            obs = st.text_area("Observações", height=60)
            prox = st.text_input("Próxima Ação")

            if st.form_submit_button("💾 Registrar Pendência", use_container_width=True):
                save_pendencia({
                    'paciente_nome': pac, 'origem': origem, 'tipo': tipo, 'prioridade': prioridade,
                    'prazo': str(prazo), 'status': 'Aberta', 'responsavel': responsavel,
                    'observacoes': obs, 'proxima_acao': prox, 'data_registro': str(date.today())
                })
                st.success("✅ Pendência registrada!")
                st.rerun()


# ================================================================
#  CALL BACK
# ================================================================
def page_call_back():
    st.markdown('<div class="page-title">🔁 Call Back</div>', unsafe_allow_html=True)

    df = get_call_back()
    abertos = df[df['status'] == 'Aberto'] if not df.empty else pd.DataFrame()

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Total CB",str(len(df)),"","primary","🔁"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Abertos",str(len(abertos)),"","danger","🔓"), unsafe_allow_html=True)
    with c3:
        if not abertos.empty and 'dias_aberto' in abertos.columns:
            med = abertos['dias_aberto'].mean()
            st.markdown(kpi_html("Média Dias",f"{med:.1f}","Dias em aberto","warning","⏱️"), unsafe_allow_html=True)
        else:
            st.markdown(kpi_html("Média Dias","—","","warning","⏱️"), unsafe_allow_html=True)
    with c4:
        if not abertos.empty and 'dias_aberto' in abertos.columns:
            maxi = abertos['dias_aberto'].max()
            st.markdown(kpi_html("Máx. Dias",str(int(maxi)) if pd.notna(maxi) else "—","","danger","📅"), unsafe_allow_html=True)
        else:
            st.markdown(kpi_html("Máx. Dias","—","","danger","📅"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Import Call Back data from tickets with "CALL BACK" in motivo
    tk_df = get_tickets({'busca': 'CALL BACK'})
    if not tk_df.empty:
        st.markdown(section_header("🎫","Tickets Call Back — Extraído dos Tickets"), unsafe_allow_html=True)
        cols = ['numero','paciente_nome','operadora','motivo','data_abertura','data_encerramento','horas_consumidas','status']
        cols = [c for c in cols if c in tk_df.columns]
        st.dataframe(tk_df[cols], use_container_width=True, height=380)

        if 'horas_consumidas' in tk_df.columns:
            abertos_tk = tk_df[tk_df['status'] == 'Aberto']
            fechados_tk = tk_df[tk_df['status'] == 'Fechado']
            st.markdown(section_header("📊","Análise Call Back"), unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if not abertos_tk.empty:
                    fig = pie_chart(
                        pd.DataFrame({'status':['Aberto','Fechado'],'total':[len(abertos_tk),len(fechados_tk)]}),
                        'status','total','Status dos Call Backs',320)
                    st.plotly_chart(fig, use_container_width=True)
            with cc2:
                if 'horas_consumidas' in tk_df.columns:
                    h_df = tk_df[tk_df['horas_consumidas'] > 0]
                    if not h_df.empty:
                        fig2 = bar_chart(h_df.head(15), 'paciente_nome', 'horas_consumidas',
                                         'Horas por Paciente (CB)', height=320)
                        fig2.update_layout(xaxis_tickangle=-40)
                        st.plotly_chart(fig2, use_container_width=True)
    else:
        if df.empty:
            st.info("Nenhum dado de Call Back. Registre manualmente ou importe os dados.")


# ================================================================
#  SLA
# ================================================================
def page_sla():
    st.markdown('<div class="page-title">🎯 Central de SLA</div>', unsafe_allow_html=True)

    df = get_tickets()
    if df.empty:
        st.info("Sem dados de tickets para análise de SLA.")
        return

    df_com_prazo = df[df['status_prazo'].notna() & (df['status_prazo'] != '') & (df['status_prazo'] != 'nan')]

    if not df_com_prazo.empty:
        dentro = (df_com_prazo['status_prazo'].str.contains('DENTRO', case=False, na=False)).sum()
        vencido = (df_com_prazo['status_prazo'].str.contains('VENCIDO|FORA', case=False, na=False)).sum()
        outros = len(df_com_prazo) - dentro - vencido

        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(kpi_html("✅ Dentro do Prazo",str(dentro),"","success","✅"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_html("❌ Vencido",str(vencido),"","danger","❌"), unsafe_allow_html=True)
        with c3:
            total_sla = dentro + vencido + outros
            pct = round(dentro/total_sla*100,1) if total_sla > 0 else 0
            st.markdown(kpi_html("📊 Conformidade SLA",f"{pct}%","","accent","🎯"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico
        fig = pie_chart(
            pd.DataFrame({'Status':['Dentro do Prazo','Vencido','Outros'],'Total':[dentro,vencido,outros]}),
            'Status','Total','Distribuição SLA',350)
        col1, col2 = st.columns([1,2])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown(section_header("📋","Tickets com SLA"), unsafe_allow_html=True)
            cols = ['numero','paciente_nome','data_abertura','data_encerramento','horas_consumidas','status_prazo','status']
            cols = [c for c in cols if c in df_com_prazo.columns]

            def color_sla(row):
                sp = str(row.get('status_prazo','')).upper()
                if 'DENTRO' in sp:
                    return ['background-color: #EAFAF1'] * len(row)
                elif 'VENCIDO' in sp or 'FORA' in sp:
                    return ['background-color: #FDEDEC'] * len(row)
                return [''] * len(row)

            disp = df_com_prazo[cols].head(100)
            st.dataframe(disp.style.apply(color_sla, axis=1), use_container_width=True, height=360)
    else:
        st.info("Sem dados de SLA disponíveis. Os tickets precisam ter campo 'Status Prazo' preenchido.")

        # Show all tickets table anyway
        cols = ['numero','paciente_nome','data_abertura','data_encerramento','horas_consumidas','status']
        cols = [c for c in cols if c in df.columns]
        st.dataframe(df[cols].head(100), use_container_width=True)


# ================================================================
#  TIMELINE DO PACIENTE
# ================================================================
def page_timeline():
    st.markdown('<div class="page-title">📅 Timeline do Paciente</div>', unsafe_allow_html=True)

    pac_df = get_pacientes()
    if pac_df.empty:
        st.info("Nenhum paciente cadastrado.")
        return

    pac_sel = st.selectbox("Selecione o paciente", [""] + list(pac_df['nome'].values))

    if not pac_sel:
        st.info("Selecione um paciente para visualizar a timeline.")
        return

    data = get_timeline_paciente(pac_sel)
    tickets = data['tickets']
    monitoramentos = data['monitoramentos']

    # Summary cards
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(kpi_html("Tickets",str(len(tickets)),"Total do paciente","primary","🎫"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Monitoramentos",str(len(monitoramentos)),"","accent","👁️"), unsafe_allow_html=True)
    with c3:
        if not tickets.empty and 'horas_consumidas' in tickets.columns:
            total_h = tickets['horas_consumidas'].sum()
            st.markdown(kpi_html("Horas Totais",f"{total_h:.0f}h","Consumidas","warning","⏱️"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(section_header("📅",f"Timeline — {pac_sel}","Histórico completo"), unsafe_allow_html=True)

    # Build timeline events
    events = []
    if not tickets.empty:
        for _, row in tickets.iterrows():
            events.append({
                'data': str(row.get('data_abertura',''))[:10],
                'tipo': '🎫 Ticket',
                'desc': f"#{row.get('numero','?')} — {row.get('classificacao','')} — {row.get('motivo','')[:60]}",
                'status': row.get('status','')
            })
    if not monitoramentos.empty:
        for _, row in monitoramentos.iterrows():
            events.append({
                'data': str(row.get('data_registro',''))[:10],
                'tipo': '👁️ Monitoramento',
                'desc': f"{row.get('situacao','')[:80]}",
                'status': row.get('status','')
            })

    if events:
        ev_df = pd.DataFrame(events).sort_values('data', ascending=False)
        for _, ev in ev_df.iterrows():
            color = "#1A5276" if "Ticket" in ev['tipo'] else "#27AE60"
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-bottom:0.75rem;align-items:flex-start;">
                <div style="min-width:100px;font-size:0.78rem;color:#566573;padding-top:4px;">{ev['data']}</div>
                <div style="width:4px;background:{color};border-radius:2px;min-height:40px;"></div>
                <div style="background:white;border-radius:8px;padding:0.6rem 1rem;box-shadow:0 1px 6px rgba(0,0,0,0.08);flex:1;">
                    <div style="font-size:0.78rem;font-weight:700;color:{color};">{ev['tipo']}</div>
                    <div style="font-size:0.85rem;color:#2C3E50;margin-top:2px;">{ev['desc']}</div>
                    <span style="font-size:0.72rem;background:#EBF5FB;color:#1A5276;padding:2px 8px;border-radius:10px;">{ev['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum evento encontrado para este paciente.")


# ================================================================
#  CENTRAL DE CAUSAS
# ================================================================
def page_central_causas():
    st.markdown('<div class="page-title">🔍 Central de Causas</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Análise de Motivos","📂 Categorias"])

    with tab1:
        motivos = get_tickets_por_motivo()
        if motivos.empty:
            st.info("Sem dados.")
            return

        # Pareto
        motivos['acumulado'] = motivos['total'].cumsum()
        motivos['perc_acum'] = motivos['acumulado'] / motivos['total'].sum() * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ocorrências', x=motivos['motivo'], y=motivos['total'],
                              marker_color=SOLAR_COLORS['primary']))
        fig.add_trace(go.Scatter(name='% Acumulado', x=motivos['motivo'], y=motivos['perc_acum'],
                                  mode='lines+markers', yaxis='y2',
                                  line=dict(color=SOLAR_COLORS['accent'], width=2.5),
                                  marker=dict(size=8)))
        fig.update_layout(
            title='Diagrama de Pareto — Top Motivos',
            yaxis2=dict(overlaying='y', side='right', range=[0,110], title='% Acumulado'),
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family='Inter'), height=420,
            margin=dict(l=10,r=10,t=40,b=10),
            xaxis=dict(showgrid=False, tickangle=-40),
            yaxis=dict(gridcolor='#EBF5FB'),
            legend=dict(orientation='h', y=1.05),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabela
        motivos_disp = motivos.copy()
        motivos_disp.columns = ['Motivo','Total','Acumulado','% Acumulado']
        motivos_disp['% Acumulado'] = motivos_disp['% Acumulado'].round(1).astype(str) + '%'
        st.dataframe(motivos_disp, use_container_width=True)

    with tab2:
        cats = get_tickets_por_categoria()
        if not cats.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig2 = pie_chart(cats, 'categoria', 'total', 'Tickets por Categoria', 380)
                st.plotly_chart(fig2, use_container_width=True)
            with c2:
                fig3 = bar_chart(cats, 'categoria', 'total',
                                 color=SOLAR_COLORS['secondary'], height=380)
                fig3.update_layout(xaxis_tickangle=-40)
                st.plotly_chart(fig3, use_container_width=True)


# ================================================================
#  MAPA DE CALOR
# ================================================================
def page_mapa_calor():
    st.markdown('<div class="page-title">🌡️ Mapa de Calor</div>', unsafe_allow_html=True)

    mes = st.selectbox("Mês", ["2026-06","2026-05"])
    lig_df = get_ligacoes(mes)

    if lig_df.empty:
        st.info("Sem dados de ligações para o mês selecionado.")
        return

    lig_df['data_hora'] = pd.to_datetime(lig_df['data_hora'], errors='coerce')
    lig_df = lig_df.dropna(subset=['data_hora'])
    lig_df['hora'] = lig_df['data_hora'].dt.hour
    lig_df['dia_semana'] = lig_df['data_hora'].dt.day_name()

    dias_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dias_pt = ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo']

    pivot = lig_df.pivot_table(index='dia_semana', columns='hora', values='id', aggfunc='count', fill_value=0)
    pivot = pivot.reindex(dias_order).fillna(0)

    fig = heatmap_chart(pivot.values.tolist(), list(range(24)), dias_pt,
                        'Ligações por Hora × Dia da Semana', height=380)
    st.plotly_chart(fig, use_container_width=True)

    # Tickets heatmap
    tk_df = get_tickets({'mes': mes})
    if not tk_df.empty and 'data_abertura' in tk_df.columns:
        tk_df['data_abertura'] = pd.to_datetime(tk_df['data_abertura'], errors='coerce')
        tk_df = tk_df.dropna(subset=['data_abertura'])
        tk_df['dia_semana'] = tk_df['data_abertura'].dt.day_name()
        tk_df['dia_mes'] = tk_df['data_abertura'].dt.day

        pivot2 = tk_df.pivot_table(index='dia_semana', columns='dia_mes', values='id', aggfunc='count', fill_value=0)
        pivot2 = pivot2.reindex([d for d in dias_order if d in pivot2.index]).fillna(0)

        if not pivot2.empty:
            dias_pt2 = [dias_pt[dias_order.index(d)] for d in pivot2.index]
            fig2 = heatmap_chart(pivot2.values.tolist(),
                                 list(pivot2.columns), dias_pt2,
                                 'Tickets por Dia do Mês × Dia da Semana', height=320)
            st.plotly_chart(fig2, use_container_width=True)


# ================================================================
#  INDICADORES ANUAIS
# ================================================================
def page_indicadores_anuais():
    st.markdown('<div class="page-title">📆 Indicadores Anuais</div>', unsafe_allow_html=True)

    from repository.data_repo import get_consolidado
    df_mai = get_consolidado('2026-05')
    df_jun = get_consolidado('2026-06')

    meses = []
    if not df_mai.empty:
        meses.append({'Mês':'Maio/2026', **df_mai.iloc[0].to_dict()})
    if not df_jun.empty:
        meses.append({'Mês':'Junho/2026', **df_jun.iloc[0].to_dict()})

    if not meses:
        st.info("Sem dados anuais consolidados. Importe os dados mensais.")
        # Show indicadores diários aggregated
        df_all = get_indicadores_diarios('')
        if not df_all.empty:
            st.markdown(section_header("📊","Resumo por Mês"), unsafe_allow_html=True)
            df_all['mes_fmt'] = df_all['mes'].map({'2026-05':'Maio/2026','2026-06':'Junho/2026'})
            grp = df_all.groupby('mes_fmt').agg(
                lig_crc=('ligacoes_entrantes_crc','sum'),
                lig_emerg=('ligacoes_transferidas_emerg','sum'),
            ).reset_index()
            if not grp.empty:
                fig = bar_chart(grp, 'mes_fmt', 'lig_crc', 'Ligações CRC por Mês', height=300)
                st.plotly_chart(fig, use_container_width=True)
        return

    df_anual = pd.DataFrame(meses)
    st.markdown(section_header("📊","Comparativo Mensal"), unsafe_allow_html=True)

    cols_num = ['ligacoes_entrantes_grupo','ligacoes_atendidas_grupo','tickets_abertos_callback','tickets_fechados_callback']
    for col in cols_num:
        if col in df_anual.columns:
            fig = bar_chart(df_anual, 'Mês', col, col.replace('_',' ').title(), height=280)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(section_header("📋","Tabela Comparativa"), unsafe_allow_html=True)
    disp = df_anual[['Mês'] + [c for c in cols_num if c in df_anual.columns]].copy()
    disp.columns = [c.replace('_',' ').title() for c in disp.columns]
    st.dataframe(disp, use_container_width=True)


# ================================================================
#  RELATÓRIOS
# ================================================================
def page_relatorios():
    st.markdown('<div class="page-title">📄 Relatórios</div>', unsafe_allow_html=True)

    tipo = st.selectbox("Tipo de Relatório",
                        ["Tickets","Ligações","Monitoramentos","Pendências","Call Back","SLA","Top Causas"])
    mes = st.selectbox("Mês de Referência", ["2026-06","2026-05","Todos"])
    mes_f = '' if mes == 'Todos' else mes

    if st.button("🔄 Gerar Relatório", use_container_width=True):
        with st.spinner("Gerando relatório..."):
            if tipo == "Tickets":
                df = get_tickets({'mes': mes_f} if mes_f else {})
            elif tipo == "Ligações":
                df = get_ligacoes(mes_f)
            elif tipo == "Monitoramentos":
                df = get_monitoramentos()
            elif tipo == "Pendências":
                df = get_pendencias()
            elif tipo == "Call Back":
                df = get_tickets({'busca':'CALL BACK'})
            elif tipo == "SLA":
                df = get_tickets({'mes': mes_f} if mes_f else {})
            elif tipo == "Top Causas":
                df = get_tickets_por_motivo()
            else:
                df = pd.DataFrame()

            if df.empty:
                st.warning("Nenhum dado encontrado para este relatório.")
            else:
                st.success(f"✅ Relatório gerado: **{len(df)} registros**")
                st.dataframe(df, use_container_width=True, height=400)

                # Export
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name=tipo)
                st.download_button(
                    f"📥 Baixar {tipo}.xlsx", buf.getvalue(),
                    f"relatorio_{tipo.lower().replace(' ','_')}_{mes_f}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                buf_csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    f"📥 Baixar {tipo}.csv", buf_csv,
                    f"relatorio_{tipo.lower()}_{mes_f}.csv",
                    "text/csv"
                )


# ================================================================
#  IMPORTAÇÃO
# ================================================================
def page_importacao():
    st.markdown('<div class="page-title">📤 Importação de Dados</div>', unsafe_allow_html=True)

    st.markdown(section_header("📂","Importar Arquivo","Excel, CSV ou ODS"), unsafe_allow_html=True)

    arquivo = st.file_uploader(
        "Selecione o arquivo",
        type=['xlsx','xls','csv','ods'],
        help="Formatos suportados: Excel (.xlsx/.xls), CSV, ODS"
    )

    if arquivo:
        st.success(f"✅ Arquivo carregado: **{arquivo.name}** ({arquivo.size/1024:.1f} KB)")

        if st.button("🚀 Importar Dados", use_container_width=True):
            with st.spinner("Importando dados... aguarde."):
                try:
                    import tempfile, os
                    suffix = os.path.splitext(arquivo.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(arquivo.read())
                        tmp_path = tmp.name

                    from services.import_service import import_excel
                    results = import_excel(tmp_path)
                    os.unlink(tmp_path)

                    st.success("✅ Importação concluída!")
                    for key, count in results.items():
                        st.write(f"- **{key}**: {count} registros importados")

                    from database.db import get_connection
                    conn = get_connection()
                    from datetime import datetime
                    conn.execute(
                        "INSERT INTO importacoes (arquivo, tipo, data_importacao, registros_importados) VALUES (?,?,?,?)",
                        (arquivo.name, suffix, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         sum(results.values()))
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro na importação: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # Histórico
    st.markdown(section_header("📋","Histórico de Importações"), unsafe_allow_html=True)
    from database.db import get_connection
    import pandas as pd
    conn = get_connection()
    hist = pd.read_sql_query("SELECT * FROM importacoes ORDER BY data_importacao DESC LIMIT 20", conn)
    conn.close()
    if hist.empty:
        st.info("Nenhuma importação realizada ainda.")
    else:
        st.dataframe(hist, use_container_width=True)


# ================================================================
#  PESQUISA GLOBAL
# ================================================================
def page_pesquisa(termo):
    if not termo:
        return
    st.markdown(f'<div class="page-title">🔎 Resultados para "{termo}"</div>', unsafe_allow_html=True)
    results = search_global(termo)
    for key, df in results.items():
        if not df.empty:
            st.markdown(f"**{key.title()} ({len(df)} resultado(s))**")
            st.dataframe(df, use_container_width=True)


# ================================================================
#  CONFIGURAÇÕES
# ================================================================
def page_configuracoes():
    st.markdown('<div class="page-title">⚙️ Configurações</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🎨 Aparência","🗄️ Banco de Dados"])

    with tab1:
        st.subheader("Identidade Visual")
        st.write("**Paleta Solar Cuidados:**")
        cols = st.columns(6)
        cores = [("#1A5276","Azul Principal"),("#2E86C1","Azul Sec."),
                 ("#F39C12","Âmbar"),("#27AE60","Verde"),("#E74C3C","Vermelho"),("#566573","Cinza")]
        for col, (cor, nome) in zip(cols, cores):
            with col:
                st.markdown(f'<div style="background:{cor};border-radius:8px;height:50px;"></div><div style="text-align:center;font-size:0.75rem;margin-top:4px;">{nome}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.info("ℹ️ Para adicionar o logotipo oficial, coloque o arquivo `logo.png` na pasta `assets/` do projeto.")

    with tab2:
        st.subheader("Status do Banco de Dados")
        from database.db import get_connection, DB_PATH
        conn = get_connection()
        tables = ['pacientes','tickets','ligacoes','call_back','monitoramentos','pendencias','indicadores_diarios','consolidado_mensal']
        for tbl in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                st.write(f"✅ **{tbl}**: {count:,} registros")
            except:
                st.write(f"⚠️ **{tbl}**: tabela não encontrada")
        conn.close()
        st.caption(f"📁 Banco de dados: `{DB_PATH}`")

        if st.button("🔄 Re-inicializar Banco de Dados", type="secondary"):
            from database.db import init_db
            init_db()
            st.success("Banco re-inicializado!")
