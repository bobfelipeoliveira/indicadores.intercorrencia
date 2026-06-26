import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from repository.data_repo import (
    get_stats_overview, get_tickets_por_categoria, get_tickets_por_motivo,
    get_top_pacientes, get_indicadores_diarios, get_consolidado
)
from utils.charts import bar_chart, line_chart, pie_chart, kpi_html, section_header, SOLAR_COLORS

def render():
    st.markdown("""
    <div class="page-title">👔 Dashboard Diretoria</div>
    <div class="page-subtitle">Visão executiva estratégica — Solar Cuidados</div>
    """, unsafe_allow_html=True)

    stats = get_stats_overview()

    # --- Resumo Executivo ---
    st.markdown(section_header("📊","Resumo Operacional","Indicadores estratégicos consolidados"), unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    total_lig = stats['total_ligacoes']
    aband = stats['ligacoes_abandonadas']
    sla = round((1 - aband/total_lig)*100,1) if total_lig > 0 else 0
    eficiencia = round(stats['tickets_fechados']/(stats['total_tickets'] or 1)*100,1)

    kpis = [
        (c1,"SLA Atendimento",f"{sla}%","Meta: 90%","success" if sla >= 90 else "danger","🎯"),
        (c2,"Taxa Resolução",f"{eficiencia}%","Tickets fechados/total","success" if eficiencia >= 70 else "warning","✅"),
        (c3,"Volume Total",f"{stats['total_tickets']:,}","Tickets no período","primary","🎫"),
        (c4,"Pacientes Ativos",f"{stats['total_pacientes']:,}","Cadastrados","primary","👥"),
    ]
    for col, label, val, sub, color, icon in kpis:
        with col:
            st.markdown(kpi_html(label, val, sub, color, icon), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- META x RESULTADO ---
    st.markdown(section_header("🏆","Meta × Resultado"), unsafe_allow_html=True)

    metas = {
        'SLA Atendimento (%)': (sla, 90),
        'Taxa Resolução (%)': (eficiencia, 80),
        'Call Back Abertos': (100 - stats['call_back_abertos'], 95),
        'Monitoramentos Ativos': (min(100, stats['monitoramentos_ativos']), 50),
    }

    fig_meta = go.Figure()
    indicadores = list(metas.keys())
    resultados = [v[0] for v in metas.values()]
    metas_vals = [v[1] for v in metas.values()]
    colors = [SOLAR_COLORS['success'] if r >= m else SOLAR_COLORS['danger']
              for r, m in zip(resultados, metas_vals)]

    fig_meta.add_trace(go.Bar(name='Meta', x=indicadores, y=metas_vals,
                               marker_color='rgba(26,82,118,0.15)',
                               marker_line_color=SOLAR_COLORS['primary'],
                               marker_line_width=2))
    fig_meta.add_trace(go.Bar(name='Resultado', x=indicadores, y=resultados,
                               marker_color=colors))
    fig_meta.update_layout(
        barmode='overlay', height=320, paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Inter'), margin=dict(l=10,r=10,t=20,b=10),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#EBF5FB'),
        legend=dict(orientation='h', y=1.05),
    )
    st.plotly_chart(fig_meta, use_container_width=True)

    # --- COMPARATIVO MENSAL ---
    st.markdown(section_header("📅","Comparativo Mensal"), unsafe_allow_html=True)
    ind_mai = get_indicadores_diarios('2026-05')
    ind_jun = get_indicadores_diarios('2026-06')

    col1, col2 = st.columns(2)
    with col1:
        if not ind_mai.empty or not ind_jun.empty:
            frames = []
            if not ind_mai.empty:
                s = ind_mai[['data','ligacoes_entrantes_crc']].copy()
                s['mes'] = 'Maio'
                frames.append(s)
            if not ind_jun.empty:
                s = ind_jun[['data','ligacoes_entrantes_crc']].copy()
                s['mes'] = 'Junho'
                frames.append(s)

            if frames:
                all_df = pd.concat(frames)
                fig2 = go.Figure()
                for mes_name, color in [('Maio', SOLAR_COLORS['primary']), ('Junho', SOLAR_COLORS['accent'])]:
                    sub = all_df[all_df['mes'] == mes_name]
                    if not sub.empty:
                        # Use day of month for x-axis comparison
                        sub = sub.copy()
                        sub['dia'] = pd.to_datetime(sub['data']).dt.day
                        fig2.add_trace(go.Scatter(
                            x=sub['dia'], y=sub['ligacoes_entrantes_crc'],
                            name=mes_name, mode='lines+markers',
                            line=dict(color=color, width=2.5),
                            marker=dict(size=6)
                        ))
                fig2.update_layout(
                    title='Ligações CRC — Comparativo',
                    height=300, paper_bgcolor='white', plot_bgcolor='white',
                    font=dict(family='Inter'), margin=dict(l=10,r=10,t=40,b=10),
                    xaxis=dict(title='Dia do Mês', showgrid=False),
                    yaxis=dict(gridcolor='#EBF5FB'),
                    legend=dict(orientation='h', y=1.08),
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados para comparativo.")

    with col2:
        cats = get_tickets_por_categoria()
        if not cats.empty:
            fig3 = pie_chart(cats, 'categoria', 'total', 'Distribuição por Categoria', 300)
            st.plotly_chart(fig3, use_container_width=True)

    # --- RANKING DOS INDICADORES ---
    st.markdown(section_header("🏅","Ranking de Causas","Top 10 motivos de acionamento"), unsafe_allow_html=True)
    mot_df = get_tickets_por_motivo()
    if not mot_df.empty:
        mot_df['rank'] = range(1, len(mot_df)+1)
        for _, row in mot_df.iterrows():
            pct = round(row['total'] / mot_df['total'].sum() * 100, 1)
            medal = "🥇" if row['rank'] == 1 else "🥈" if row['rank'] == 2 else "🥉" if row['rank'] == 3 else f"#{int(row['rank'])}"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;padding:0.5rem 0.75rem;
                        background:white;border-radius:8px;margin-bottom:0.4rem;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                <div style="font-size:1.1rem;min-width:2rem;">{medal}</div>
                <div style="flex:1;font-size:0.875rem;color:#2C3E50;">{row['motivo']}</div>
                <div style="font-weight:700;color:#1A5276;min-width:3rem;text-align:right;">{int(row['total'])}</div>
                <div style="min-width:60px;">
                    <div style="background:#EBF5FB;border-radius:4px;height:8px;overflow:hidden;">
                        <div style="background:#1A5276;height:100%;width:{pct}%;border-radius:4px;"></div>
                    </div>
                    <div style="font-size:0.7rem;color:#566573;text-align:right;">{pct}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- ALERTAS ESTRATÉGICOS ---
    st.markdown(section_header("🚨","Alertas Estratégicos"), unsafe_allow_html=True)
    alertas = []
    if sla < 90:
        alertas.append(('critical', f"SLA abaixo da meta: {sla}% (meta: 90%)"))
    if stats['call_back_abertos'] > 10:
        alertas.append(('warning', f"{stats['call_back_abertos']} Call Backs em aberto"))
    if stats['pendencias_abertas'] > 5:
        alertas.append(('warning', f"{stats['pendencias_abertas']} pendências não resolvidas"))
    if eficiencia < 70:
        alertas.append(('critical', f"Taxa de resolução baixa: {eficiencia}% (meta: 80%)"))

    if not alertas:
        st.markdown('<div class="alert-info">✅ Todos os indicadores estratégicos dentro das metas.</div>', unsafe_allow_html=True)
    else:
        for tipo, msg in alertas:
            css_class = "alert-critical" if tipo == 'critical' else "alert-warning"
            icon = "🚨" if tipo == 'critical' else "⚠️"
            st.markdown(f'<div class="{css_class}">{icon} {msg}</div>', unsafe_allow_html=True)
