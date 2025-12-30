"""
Dashboard Components for QBR Auto-Drafter
Visual metrics, charts, and portfolio overview using Plotly and Streamlit
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

# Monday.com Color Palette
# Note: These colors are used for Plotly charts which cannot use CSS variables
# For inline HTML styles, use CSS variables (--app-*) defined in app.py for dark mode support
COLORS = {
    'primary': '#6161FF',
    'primary_dark': '#4B4BCC',
    'success': '#00CA72',
    'warning': '#FDAB3D',
    'danger': '#E2445C',
    'info': '#579BFC',
    'purple': '#A25DDC',
    'text_primary': '#323338',
    'text_secondary': '#676879',
    'bg': '#F6F7FB',
    'white': '#FFFFFF'
}


def get_risk_color(risk_score: float) -> str:
    """Return color based on risk score threshold"""
    if risk_score >= 0.6:
        return COLORS['danger']
    elif risk_score >= 0.3:
        return COLORS['warning']
    return COLORS['success']


def get_risk_label(risk_score: float) -> str:
    """Return risk label based on score"""
    if risk_score >= 0.6:
        return "High Risk"
    elif risk_score >= 0.3:
        return "Medium Risk"
    return "Low Risk"


def create_risk_gauge(risk_score: float, account_name: str = "") -> go.Figure:
    """Create a radial gauge chart for risk score"""
    color = get_risk_color(risk_score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score * 100,
        number={'suffix': '%', 'font': {'size': 36, 'color': COLORS['text_primary']}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': COLORS['text_secondary']},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': COLORS['bg'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 202, 114, 0.2)'},
                {'range': [30, 60], 'color': 'rgba(253, 171, 61, 0.2)'},
                {'range': [60, 100], 'color': 'rgba(226, 68, 92, 0.2)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.8,
                'value': risk_score * 100
            }
        },
        title={'text': f"Churn Risk", 'font': {'size': 16, 'color': COLORS['text_secondary']}}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig


def create_health_gauge(scat_score: float) -> go.Figure:
    """Create a health score gauge (SCAT score)"""
    if scat_score >= 80:
        color = COLORS['success']
    elif scat_score >= 60:
        color = COLORS['info']
    elif scat_score >= 40:
        color = COLORS['warning']
    else:
        color = COLORS['danger']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=scat_score,
        number={'suffix': '', 'font': {'size': 36, 'color': COLORS['text_primary']}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': COLORS['text_secondary']},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': COLORS['bg'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(226, 68, 92, 0.15)'},
                {'range': [40, 60], 'color': 'rgba(253, 171, 61, 0.15)'},
                {'range': [60, 80], 'color': 'rgba(87, 155, 252, 0.15)'},
                {'range': [80, 100], 'color': 'rgba(0, 202, 114, 0.15)'}
            ]
        },
        title={'text': "Health Score (SCAT)", 'font': {'size': 14, 'color': COLORS['text_secondary']}}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig


def create_nps_indicator(nps_score: float) -> go.Figure:
    """Create NPS score visualization"""
    if nps_score >= 8:
        color = COLORS['success']
        label = "Promoter"
    elif nps_score >= 6:
        color = COLORS['warning']
        label = "Passive"
    else:
        color = COLORS['danger']
        label = "Detractor"
    
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=nps_score,
        number={'font': {'size': 42, 'color': color}},
        delta={'reference': 7, 'relative': False, 'position': 'bottom'},
        title={'text': f"NPS Score<br><span style='font-size:12px;color:{color}'>{label}</span>",
               'font': {'size': 14, 'color': COLORS['text_secondary']}}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig


def create_usage_growth_chart(growth_pct: float, account_name: str) -> go.Figure:
    """Create usage growth bar visualization"""
    color = COLORS['success'] if growth_pct >= 0 else COLORS['danger']
    
    fig = go.Figure(go.Bar(
        x=[growth_pct * 100],
        y=[''],
        orientation='h',
        marker_color=color,
        text=[f"{growth_pct * 100:+.1f}%"],
        textposition='outside',
        textfont={'size': 18, 'color': COLORS['text_primary'], 'family': 'Arial Black'}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=80,
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis={'range': [-50, 50], 'showgrid': True, 'gridcolor': 'rgba(0,0,0,0.08)',
               'zeroline': True, 'zerolinecolor': COLORS['text_secondary'], 'zerolinewidth': 2,
               'tickfont': {'size': 10}},
        yaxis={'visible': False},
        showlegend=False
    )
    
    return fig


def create_automation_progress(adoption_pct: float) -> None:
    """Render automation adoption as a styled progress bar"""
    color = COLORS['success'] if adoption_pct >= 0.6 else (COLORS['warning'] if adoption_pct >= 0.3 else COLORS['danger'])
    
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="color: var(--app-text-secondary); font-size: 14px;">Automation Adoption</span>
            <span style="color: {color}; font-weight: 600;">{adoption_pct * 100:.0f}%</span>
        </div>
        <div style="background: var(--app-bg-primary); border-radius: 10px; height: 12px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, {color}, {COLORS['primary']}); 
                        width: {adoption_pct * 100}%; height: 100%; border-radius: 10px;
                        transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_radar_chart(accounts_df: pd.DataFrame) -> go.Figure:
    """Create radar chart comparing all accounts across key metrics"""
    categories = ['Usage Growth', 'Automation', 'NPS', 'Health (SCAT)', 'Low Risk']
    
    fig = go.Figure()
    
    colors = [COLORS['primary'], COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['purple']]
    
    for idx, (_, row) in enumerate(accounts_df.iterrows()):
        # Normalize values to 0-100 scale
        values = [
            max(0, min(100, (row['usage_growth_qoq'] + 0.5) * 100)),  # -50% to +50% -> 0-100
            row['automation_adoption_pct'] * 100,
            row['nps_score'] * 10,  # 0-10 -> 0-100
            row['scat_score'],
            (1 - row['risk_engine_score']) * 100  # Invert risk for "Low Risk"
        ]
        values.append(values[0])  # Close the polygon
        
        categories_closed = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_closed,
            fill='toself',
            fillcolor=f'rgba{tuple(int(colors[idx % len(colors)].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}',
            line=dict(color=colors[idx % len(colors)], width=2),
            name=row['account_name']
        ))
    
    fig.update_layout(
        title=dict(
            text='Account Comparison',
            font=dict(size=16, color=COLORS['text_primary']),
            x=0.5,
            xanchor='center'
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont={'size': 10},
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont={'size': 11, 'color': COLORS['text_primary']}
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=450,
        margin=dict(l=60, r=60, t=50, b=80)
    )
    
    return fig


def create_portfolio_risk_pie(accounts_df: pd.DataFrame) -> go.Figure:
    """Create pie chart showing risk distribution across portfolio"""
    risk_counts = {
        'Low Risk': len(accounts_df[accounts_df['risk_engine_score'] < 0.3]),
        'Medium Risk': len(accounts_df[(accounts_df['risk_engine_score'] >= 0.3) & (accounts_df['risk_engine_score'] < 0.6)]),
        'High Risk': len(accounts_df[accounts_df['risk_engine_score'] >= 0.6])
    }
    
    colors = [COLORS['success'], COLORS['warning'], COLORS['danger']]
    
    fig = go.Figure(data=[go.Pie(
        labels=list(risk_counts.keys()),
        values=list(risk_counts.values()),
        hole=0.6,
        marker_colors=colors,
        textinfo='label+value',
        textposition='outside',
        textfont={'size': 12}
    )])
    
    # Add center annotation
    total = sum(risk_counts.values())
    fig.add_annotation(
        text=f"<b>{total}</b><br>Accounts",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text='Risk Distribution',
            font=dict(size=16, color=COLORS['text_primary']),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def render_account_metrics(client_data: Dict[str, Any]) -> None:
    """Render comprehensive metrics dashboard for a single account"""
    # Account header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['purple']} 100%);
                padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 1.5rem; color: white;">
        <h2 style="margin: 0; font-size: 1.8rem;">{client_data['account_name']}</h2>
        <div style="display: flex; gap: 1rem; margin-top: 0.5rem; align-items: center;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.25rem 0.75rem; border-radius: 12px; 
                        font-size: 0.875rem; font-weight: 600;">{client_data['plan_type']}</span>
            <span style="opacity: 0.9;">{client_data['active_users']} active users</span>
            <span style="opacity: 0.9;">•</span>
            <span style="opacity: 0.9;">Prefers {client_data['preferred_channel']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics Row - 4 equal columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.plotly_chart(create_risk_gauge(client_data['risk_engine_score']), use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.plotly_chart(create_health_gauge(client_data['scat_score']), use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        st.plotly_chart(create_nps_indicator(client_data['nps_score']), use_container_width=True, config={'displayModeBar': False})
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: var(--app-bg-card); border-radius: 12px; padding: 1.5rem; text-align: center;
                    box-shadow: 0 2px 8px var(--app-shadow); border: 1px solid var(--app-border); height: 200px; display: flex;
                    flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 2.8rem; font-weight: 700; color: var(--app-text-primary);">
                {client_data['tickets_last_quarter']}
            </div>
            <div style="color: var(--app-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Support Tickets
            </div>
            <div style="color: var(--app-text-secondary); font-size: 0.8rem; margin-top: 0.25rem;">
                Avg Response: {client_data['avg_response_time']}h
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row - Growth and Automation
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="color: var(--app-text-secondary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.25rem;">
            Quarter-over-Quarter Growth
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_usage_growth_chart(client_data['usage_growth_qoq'], client_data['account_name']), 
                       use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        create_automation_progress(client_data['automation_adoption_pct'])
        st.markdown(f"""
        <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--app-border);">
            <div style="font-size: 0.7rem; color: var(--app-text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">CRM Notes</div>
            <div style="font-size: 0.8rem; color: var(--app-text-primary); margin-top: 0.4rem; 
                        font-style: italic; line-height: 1.4;">"{client_data['crm_notes'][:120]}..."</div>
        </div>
        """, unsafe_allow_html=True)


def render_portfolio_overview(df: pd.DataFrame) -> None:
    """Render portfolio-level overview dashboard"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['purple']} 100%);
                padding: 2rem; border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; font-size: 2rem;">📊 Portfolio Overview</h2>
        <p style="opacity: 0.9; margin-top: 0.5rem;">Q3 2025 Customer Health Summary</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Accounts", len(df))
    
    with col2:
        high_risk = len(df[df['risk_engine_score'] >= 0.6])
        st.metric("High Risk", high_risk, delta=f"-{high_risk}" if high_risk > 0 else "0", delta_color="inverse")
    
    with col3:
        avg_nps = df['nps_score'].mean()
        st.metric("Avg NPS", f"{avg_nps:.1f}")
    
    with col4:
        total_users = df['active_users'].sum()
        st.metric("Total Active Users", f"{total_users:,}")
    
    with col5:
        avg_automation = df['automation_adoption_pct'].mean() * 100
        st.metric("Avg Automation", f"{avg_automation:.0f}%")
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Charts row
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(create_portfolio_risk_pie(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_radar_chart(df), use_container_width=True)


def render_dashboard(df: pd.DataFrame, selected_account: str = None) -> None:
    """Main dashboard renderer - handles both portfolio and account views"""
    if selected_account:
        client_data = df[df['account_name'] == selected_account].iloc[0].to_dict()
        render_account_metrics(client_data)
    else:
        render_portfolio_overview(df)

