import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from repository.data_repo import get_indicadores_diarios, get_consolidado, get_ligacoes, get_tickets
from utils.charts import bar_chart, line_chart, kpi_html, section_header, SOLAR_COLORS

def render():
    st.markdown("""
    <div class="page-title">📅 Indicadores Mensais</div>
    <div class="page-subtitle">Acompanhamento detalhado dos indicadores operacionais</div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2,6])
    with col_f1:
        mes_sel = st.selectbox("📅 Selecionar Mês", ["2026-06","2026-05"], key="ind_mes")

    # CONSOLIDADO
    consol = get_consolidado(mes_sel)
    ind_df = get_indicadores_diarios(mes_sel)

    mes_nome = "Junho/2026" if mes_sel == "2026-06" else "Maio/2026"
    st.markdown(section_header("📊", f"Consolidado — {mes_nome}"), unsafe_allow_html=True)

    if not consol.empty:
        row = consol.iloc[0]
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        metrics = [
            (c1,"Lig. Entrantes",f"{int(row.get('ligacoes_entrantes_grupo',0)):,}","primary","📥"),
            (c2,"Lig. Atendidas",f"{int(row.get('ligacoes_atendidas_grupo',0)):,}","success","✅"),
            (c3,"% Atendimento",f"{row.get('perc_atendida',0)*100:.1f}%","success","🎯"),
            (c4,"CB Abertos",f"{int(row.get('tickets_abertos_callback',0)):,}","warning","🔁"),
            (c5,"CB Fechados",f"{int(row.get('tickets_fechados_callback',0)):,}","success","✔️"),
            (c6,"SLA Call Back",f"{row.get('sla_callback',0):.1f}%","accent","⏱️"),
        ]
        for col, label, val, color, icon in metrics:
            with col:
                st.markdown(kpi_html(label, val, "", color, icon), unsafe_allow_html=True)
    else:
        st.info("Sem dados consolidados para este mês. Importe o arquivo Excel.")

    st.markdown("<br>", unsafe_allow_html=True)

    if not ind_df.empty:
        st.markdown(section_header("📈","Evolução Diária de Ligações"), unsafe_allow_html=True)

        fig = go.Figure()
        if 'ligacoes_entrantes_crc' in ind_df.columns:
            fig.add_trace(go.Bar(name='Entrantes CRC', x=ind_df['data'], y=ind_df['ligacoes_entrantes_crc'],
                                  marker_color=SOLAR_COLORS['primary']))
        if 'ligacoes_transferidas_emerg' in ind_df.columns:
            fig.add_trace(go.Bar(name='Transferidas Emerg.', x=ind_df['data'], y=ind_df['ligacoes_transferidas_emerg'],
                                  marker_color=SOLAR_COLORS['secondary']))
        if 'ligacoes_entrantes_emerg_dia' in ind_df.columns:
            fig.add_trace(go.Scatter(name='Emerg. Dia', x=ind_df['data'], y=ind_df['ligacoes_entrantes_emerg_dia'],
                                      mode='lines+markers', line=dict(color=SOLAR_COLORS['accent'], width=2.5),
                                      marker=dict(size=7)))
        fig.update_layout(
            barmode='group',
            paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family='Inter', size=12),
            height=380,
            legend=dict(orientation='h', y=1.05),
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#EBF5FB'),
        )
        st.plotly_chart(fig, use_container_width=True)

        # % Atendimento
        if 'perc_atendidas' in ind_df.columns:
            st.markdown(section_header("🎯","Taxa de Atendimento Diária"), unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=ind_df['data'],
                y=(ind_df['perc_atendidas'] * 100).round(1),
                mode='lines+markers+text',
                line=dict(color=SOLAR_COLORS['success'], width=2.5),
                marker=dict(size=8, color=SOLAR_COLORS['success']),
                fill='tozeroy',
                fillcolor='rgba(39,174,96,0.08)',
                name='% Atendidas'
            ))
            fig2.add_hline(y=90, line_dash='dash', line_color=SOLAR_COLORS['danger'],
                           annotation_text="Meta 90%", annotation_position="top left")
            fig2.update_layout(
                paper_bgcolor='white', plot_bgcolor='white',
                height=280, margin=dict(l=10, r=10, t=20, b=10),
                yaxis=dict(range=[0,110], gridcolor='#EBF5FB'),
                xaxis=dict(showgrid=False),
                font=dict(family='Inter'),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Tickets sem sucesso
        if 'tickets_abertos_sem_sucesso' in ind_df.columns:
            st.markdown(section_header("⚠️","Tickets por Transferência Sem Sucesso"), unsafe_allow_html=True)
            fig3 = bar_chart(ind_df, 'data', 'tickets_abertos_sem_sucesso',
                             color=SOLAR_COLORS['danger'], height=280)
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("📋 Nenhum dado de indicadores diários para este mês. Importe o arquivo Excel.")

    # --- DESEMPENHO POR HORA ---
    st.markdown(section_header("⏰","Desempenho por Hora — Ligações"), unsafe_allow_html=True)
    lig_df = get_ligacoes(mes_sel)
    if not lig_df.empty and 'data_hora' in lig_df.columns:
        lig_df['data_hora'] = pd.to_datetime(lig_df['data_hora'], errors='coerce')
        lig_df = lig_df.dropna(subset=['data_hora'])
        lig_df['hora'] = lig_df['data_hora'].dt.hour
        hora_grp = lig_df.groupby('hora').agg(
            total=('id','count'),
            abandonadas=('abandonada','sum')
        ).reset_index()
        hora_grp['atendidas'] = hora_grp['total'] - hora_grp['abandonadas']

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name='Atendidas', x=hora_grp['hora'], y=hora_grp['atendidas'],
                               marker_color=SOLAR_COLORS['success']))
        fig4.add_trace(go.Bar(name='Abandonadas', x=hora_grp['hora'], y=hora_grp['abandonadas'],
                               marker_color=SOLAR_COLORS['danger']))
        fig4.update_layout(
            barmode='stack', height=320, paper_bgcolor='white', plot_bgcolor='white',
            font=dict(family='Inter'), margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(title='Hora do Dia', showgrid=False, dtick=1),
            yaxis=dict(gridcolor='#EBF5FB'),
            legend=dict(orientation='h', y=1.05),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Dados insuficientes para análise por hora.")

    # --- TABELA RESUMO ---
    st.markdown(section_header("📋","Dados Brutos — Indicadores Diários"), unsafe_allow_html=True)
    if not ind_df.empty:
        display = ind_df.copy()
        display.columns = [c.replace('_',' ').title() for c in display.columns]
        st.dataframe(display, use_container_width=True, height=300)
