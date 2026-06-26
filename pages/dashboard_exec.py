import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from repository.data_repo import (
    get_stats_overview, get_tickets_por_categoria, get_top_pacientes,
    get_tickets_por_operadora, get_tickets_por_motivo, get_indicadores_diarios,
    get_tickets, get_ligacoes
)
from utils.charts import (
    bar_chart, line_chart, pie_chart, heatmap_chart,
    kpi_html, section_header, SOLAR_COLORS
)

def render():
    st.markdown("""
    <div class="page-title">📊 Dashboard Executivo</div>
    <div class="page-subtitle">Visão operacional em tempo real — Solar Cuidados Intercorrência</div>
    """, unsafe_allow_html=True)

    # --- KPIs ---
    stats = get_stats_overview()
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        st.markdown(kpi_html("Pacientes","total_pacientes" and f"{stats['total_pacientes']:,}","Cadastrados","primary","👥"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Total Tickets",f"{stats['total_tickets']:,}","Todos os períodos","secondary","🎫"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Abertos",f"{stats['tickets_abertos']:,}","Tickets em aberto","warning","🔓"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Encerrados",f"{stats['tickets_fechados']:,}","Tickets fechados","success","✅"), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_html("Ligações",f"{stats['total_ligacoes']:,}","Total registradas","accent","📞"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_html("Monitoramentos",f"{stats['monitoramentos_ativos']:,}","Ativos","primary","👁️"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c7,c8,c9,c10 = st.columns(4)
    with c7:
        st.markdown(kpi_html("Ligações Abandonadas",f"{stats['ligacoes_abandonadas']:,}","","danger","📵"), unsafe_allow_html=True)
    with c8:
        total_lig = stats['total_ligacoes']
        sla = round((1 - stats['ligacoes_abandonadas'] / total_lig) * 100, 1) if total_lig > 0 else 0
        st.markdown(kpi_html("SLA Atendimento",f"{sla}%","Ligações atendidas","success","🎯"), unsafe_allow_html=True)
    with c9:
        st.markdown(kpi_html("Pendências",f"{stats['pendencias_abertas']:,}","Abertas","warning","⚠️"), unsafe_allow_html=True)
    with c10:
        st.markdown(kpi_html("Call Back",f"{stats['call_back_abertos']:,}","Em aberto","danger","🔁"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FILTROS ---
    with st.expander("🔍 Filtros do Dashboard", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            mes_sel = st.selectbox("Mês", ["Todos","2026-05","2026-06"], key="dash_mes")
        with fc2:
            area_opts = ["Todas","CI-INTERCORRENCIA"]
            area_sel = st.selectbox("Área", area_opts, key="dash_area")
        with fc3:
            st.selectbox("Status", ["Todos","Aberto","Fechado"], key="dash_status")

    mes_filter = mes_sel if mes_sel != "Todos" else ''

    # --- CHARTS ROW 1 ---
    st.markdown(section_header("📈","Análise de Tickets","Distribuição e evolução"), unsafe_allow_html=True)
    col1, col2 = st.columns([1.6, 1])

    with col1:
        ind_df = get_indicadores_diarios(mes_filter)
        if not ind_df.empty:
            fig = line_chart(ind_df, 'data',
                             ['ligacoes_entrantes_crc','ligacoes_transferidas_emerg'],
                             'Ligações por Dia', 380)
            fig.data[0].name = 'Entrantes CRC'
            fig.data[1].name = 'Transferidas Emergência'
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Importe os dados para visualizar o gráfico de ligações.")

    with col2:
        cat_df = get_tickets_por_categoria()
        if not cat_df.empty:
            fig2 = pie_chart(cat_df, 'categoria', 'total', 'Tickets por Categoria', 380)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados de categorias.")

    # --- CHARTS ROW 2 ---
    col3, col4 = st.columns(2)
    with col3:
        motivo_df = get_tickets_por_motivo()
        if not motivo_df.empty:
            fig3 = bar_chart(motivo_df, 'motivo', 'total', 'Top 10 Motivos de Tickets', height=380)
            fig3.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Sem dados de motivos.")

    with col4:
        op_df = get_tickets_por_operadora()
        if not op_df.empty:
            fig4 = bar_chart(op_df, 'operadora', 'total', 'Tickets por Operadora',
                             color=SOLAR_COLORS['secondary'], height=380)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem dados de operadoras.")

    # --- HEATMAP ---
    st.markdown(section_header("🌡️","Mapa de Calor de Ligações","Distribuição por hora do dia"), unsafe_allow_html=True)
    lig_df = get_ligacoes(mes_filter)
    if not lig_df.empty and 'data_hora' in lig_df.columns:
        lig_df['data_hora'] = pd.to_datetime(lig_df['data_hora'], errors='coerce')
        lig_df = lig_df.dropna(subset=['data_hora'])
        lig_df['hora'] = lig_df['data_hora'].dt.hour
        lig_df['dia_semana'] = lig_df['data_hora'].dt.day_name()
        dias_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        dias_pt = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']
        pivot = lig_df.pivot_table(index='dia_semana', columns='hora', values='id', aggfunc='count', fill_value=0)
        pivot = pivot.reindex(dias_order).fillna(0)
        fig5 = heatmap_chart(
            pivot.values.tolist(),
            list(range(24)),
            dias_pt,
            'Ligações por Hora e Dia da Semana',
            height=300
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Dados insuficientes para o mapa de calor.")

    # --- TOP PACIENTES ---
    st.markdown(section_header("👥","Top Pacientes","Por volume de tickets"), unsafe_allow_html=True)
    top_pac = get_top_pacientes()
    if not top_pac.empty:
        fig6 = bar_chart(top_pac.head(12), 'paciente_nome', 'total', height=320)
        fig6.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Sem dados de pacientes.")

    # --- ALERTAS ---
    st.markdown(section_header("🚨","Alertas Operacionais"), unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        if stats['tickets_abertos'] > 0:
            st.markdown(f'<div class="alert-warning">⚠️ <strong>{stats["tickets_abertos"]}</strong> tickets ainda em aberto aguardando resolução.</div>', unsafe_allow_html=True)
        if stats['ligacoes_abandonadas'] > 0:
            st.markdown(f'<div class="alert-critical">🚨 <strong>{stats["ligacoes_abandonadas"]}</strong> ligações abandonadas registradas.</div>', unsafe_allow_html=True)
    with a2:
        if stats['call_back_abertos'] > 0:
            st.markdown(f'<div class="alert-critical">🔁 <strong>{stats["call_back_abertos"]}</strong> Call Backs pendentes de retorno.</div>', unsafe_allow_html=True)
        if stats['pendencias_abertas'] > 0:
            st.markdown(f'<div class="alert-warning">📋 <strong>{stats["pendencias_abertas"]}</strong> pendências abertas.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="alert-info">✅ Sistema operacional — Dados atualizados.</div>', unsafe_allow_html=True)
