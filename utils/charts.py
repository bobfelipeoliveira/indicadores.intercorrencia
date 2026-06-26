import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

SOLAR_COLORS = {
    'primary': '#1A5276',
    'secondary': '#2E86C1',
    'accent': '#F39C12',
    'success': '#27AE60',
    'warning': '#E67E22',
    'danger': '#E74C3C',
    'light': '#85C1E9',
    'palette': ['#1A5276','#2E86C1','#F39C12','#27AE60','#E74C3C','#8E44AD','#E67E22','#17A589']
}

def solar_layout(fig, title='', height=350):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#1A2733', family='Inter'), x=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', color='#2C3E50', size=12),
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        height=height,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(showgrid=False, linecolor='#D5DBDB'),
        yaxis=dict(gridcolor='#EBF5FB', linecolor='#D5DBDB'),
        hoverlabel=dict(bgcolor='white', bordercolor='#1A5276', font_family='Inter'),
    )
    return fig

def bar_chart(df, x, y, title='', color=None, height=350):
    colors = [color or SOLAR_COLORS['primary']] * len(df) if not isinstance(color, list) else color
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        marker_color=colors,
        marker_line_width=0,
        text=df[y].round(0) if df[y].dtype in ['float64','int64'] else df[y],
        textposition='outside',
        textfont=dict(size=11),
    ))
    return solar_layout(fig, title, height)

def line_chart(df, x, y_cols, title='', height=350):
    fig = go.Figure()
    for i, col in enumerate(y_cols if isinstance(y_cols, list) else [y_cols]):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            name=col,
            mode='lines+markers',
            line=dict(color=SOLAR_COLORS['palette'][i % len(SOLAR_COLORS['palette'])], width=2.5),
            marker=dict(size=7),
            fill='tozeroy' if i == 0 and len(y_cols if isinstance(y_cols, list) else [y_cols]) == 1 else None,
            fillcolor='rgba(26,82,118,0.08)' if i == 0 else None,
        ))
    return solar_layout(fig, title, height)

def pie_chart(df, names, values, title='', height=320):
    fig = go.Figure(go.Pie(
        labels=df[names], values=df[values],
        hole=0.45,
        marker_colors=SOLAR_COLORS['palette'],
        textfont_size=12,
    ))
    return solar_layout(fig, title, height)

def heatmap_chart(z, x, y, title='', height=400):
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y,
        colorscale=[[0,'#EBF5FB'],[0.5,'#2E86C1'],[1,'#1A5276']],
        showscale=True,
    ))
    return solar_layout(fig, title, height)

def kpi_html(label, value, sub='', color='primary', icon='📊'):
    color_map = {
        'primary': '#1A5276', 'success': '#27AE60',
        'danger': '#E74C3C', 'warning': '#F39C12', 'accent': '#E67E22'
    }
    c = color_map.get(color, '#1A5276')
    return f"""
    <div style="background:white;border-radius:12px;padding:1.1rem 1.25rem;
                box-shadow:0 2px 12px rgba(26,82,118,0.10);border-left:4px solid {c};
                transition:all 0.25s ease;height:100%;">
        <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.08em;color:#566573;margin-bottom:0.3rem;">{icon} {label}</div>
        <div style="font-size:1.85rem;font-weight:800;color:{c};line-height:1;">{value}</div>
        <div style="font-size:0.75rem;color:#95A5A6;margin-top:0.25rem;">{sub}</div>
    </div>
    """

def section_header(icon, title, subtitle=''):
    return f"""
    <div style="display:flex;align-items:center;gap:0.75rem;
                margin:1.5rem 0 0.75rem 0;padding-bottom:0.75rem;
                border-bottom:2px solid #EBF5FB;">
        <span style="font-size:1.5rem;">{icon}</span>
        <div>
            <div style="font-size:1.2rem;font-weight:800;color:#1A2733;">{title}</div>
            {"<div style='font-size:0.8rem;color:#566573;'>"+subtitle+"</div>" if subtitle else ""}
        </div>
    </div>
    """
