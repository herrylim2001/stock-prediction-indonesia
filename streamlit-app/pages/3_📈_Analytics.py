"""
📈 Analytics & Reports Page
Professional analytics with shadcn/ui design
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
from utils.ui_components import get_shadcn_css, stat_card, badge
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Analytics & Reports",
    page_icon="📈",
    layout="wide"
)

# Apply shadcn CSS
st.markdown(get_shadcn_css(), unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 class="heading-1">📈 Analytics & Reports</h1>
    <p class="text-muted" style="font-size: 1rem; margin-top: 0.5rem;">
        Comprehensive analytics and performance insights across all talents
    </p>
</div>
""", unsafe_allow_html=True)

# Date range selector
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "All Time"]
    )

with col2:
    metric_focus = st.selectbox(
        "Focus Metric",
        ["All Metrics", "Revenue", "Engagement", "Growth"]
    )

with col3:
    st.markdown("###")
    if st.button("📊 Report", use_container_width=True):
        st.info("Full report generation feature (coming soon)")

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Key Metrics Overview
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 class="heading-3">📊 Key Performance Indicators</h2>
    <p class="text-muted">Platform-wide metrics and performance overview</p>
</div>
""", unsafe_allow_html=True)

stats = dm.get_platform_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        title="Total Revenue",
        value=f"${stats['total_diamonds'] * 0.01:,.2f}",
        description=f"💎 {stats['total_diamonds']:,} diamonds",
        icon="💰",
        color="green"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        title="Total Followers",
        value=f"{stats['total_followers']:,}",
        description="Across all talents",
        icon="👥",
        color="blue"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(stat_card(
        title="Total Streams",
        value=f"{stats['total_streams']:,}",
        description="All time broadcasts",
        icon="📺",
        color="purple"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(stat_card(
        title="Avg Viewers",
        value=f"{stats['avg_viewers_per_stream']:.0f}",
        description="Per stream session",
        icon="📊",
        color="pink"
    ), unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Charts Section
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 class="heading-3">📈 Trend Analysis</h2>
    <p class="text-muted">Growth and revenue trends over time</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Platform Growth</h3>
            <p class="text-muted">New and active talent trends</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    growth_data = dm.get_talent_growth_data()
    df_growth = pd.DataFrame(growth_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_growth['Month'],
        y=df_growth['New Talents'],
        name='New Talents',
        mode='lines+markers',
        line=dict(color='hsl(262, 83%, 58%)', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=df_growth['Month'],
        y=df_growth['Active Talents'],
        name='Active Talents',
        mode='lines+markers',
        line=dict(color='hsl(280, 83%, 58%)', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(192, 132, 252, 0.1)'
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )

    st.plotly_chart(fig, use_container_width=True, key="growth_chart")

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Revenue Trends</h3>
            <p class="text-muted">Diamonds and gifts distribution</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    revenue_data = dm.get_revenue_data()
    df_revenue = pd.DataFrame(revenue_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_revenue['Month'],
        y=df_revenue['Diamonds'],
        name='Diamonds',
        marker_color='hsl(262, 83%, 58%)'
    ))
    fig.add_trace(go.Bar(
        x=df_revenue['Month'],
        y=df_revenue['Gifts'],
        name='Gifts',
        marker_color='hsl(280, 83%, 58%)'
    ))

    fig.update_layout(
        height=350,
        barmode='group',
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )

    st.plotly_chart(fig, use_container_width=True, key="revenue_chart")

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Top Performers
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 class="heading-3">🌟 Top Performers Analysis</h2>
    <p class="text-muted">Leaderboards across different performance metrics</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💎 By Diamonds", "👥 By Followers", "📺 By Streams"])

with tab1:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Top 10 Talents by Diamonds</h3>
            <p class="text-muted">Highest revenue generators</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    top_diamonds = dm.get_top_talents('total_diamonds', limit=10)
    df_diamonds = pd.DataFrame([{
        'Talent': t['name'],
        'Diamonds': t['total_diamonds'],
        'Level': t['level'],
        'Status': t['status']
    } for t in top_diamonds])

    fig = go.Figure(data=[
        go.Bar(
            x=df_diamonds['Talent'],
            y=df_diamonds['Diamonds'],
            marker=dict(
                color=df_diamonds['Level'],
                colorscale='Purples',
                showscale=True,
                colorbar=dict(title="Level")
            ),
            text=df_diamonds['Diamonds'],
            textposition='auto',
        )
    ])
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True, key="diamonds_chart")

    st.dataframe(df_diamonds, use_container_width=True, hide_index=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Top 10 Talents by Followers</h3>
            <p class="text-muted">Most followed talents</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    top_followers = dm.get_top_talents('followers', limit=10)
    df_followers = pd.DataFrame([{
        'Talent': t['name'],
        'Followers': t['followers'],
        'Level': t['level'],
        'Status': t['status']
    } for t in top_followers])

    fig = go.Figure(data=[
        go.Bar(
            x=df_followers['Talent'],
            y=df_followers['Followers'],
            marker=dict(
                color=df_followers['Level'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="Level")
            ),
            text=df_followers['Followers'],
            textposition='auto',
        )
    ])
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True, key="followers_chart")

    st.dataframe(df_followers, use_container_width=True, hide_index=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Top 10 Talents by Streams</h3>
            <p class="text-muted">Most active broadcasters</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    top_streams = dm.get_top_talents('total_streams', limit=10)
    df_streams = pd.DataFrame([{
        'Talent': t['name'],
        'Total Streams': t.get('total_streams', 0),
        'Avg Viewers': t.get('avg_viewers', 0),
        'Status': t['status']
    } for t in top_streams])

    fig = go.Figure(data=[
        go.Bar(
            x=df_streams['Talent'],
            y=df_streams['Total Streams'],
            marker=dict(
                color=df_streams['Avg Viewers'],
                colorscale='Greens',
                showscale=True,
                colorbar=dict(title="Avg Viewers")
            ),
            text=df_streams['Total Streams'],
            textposition='auto',
        )
    ])
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True, key="streams_chart")

    st.dataframe(df_streams, use_container_width=True, hide_index=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Status Distribution and Engagement
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h2 class="heading-3">📊 Distribution Analysis</h2>
    <p class="text-muted">Status distribution and engagement metrics</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Talent Status Distribution</h3>
            <p class="text-muted">Current status breakdown</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    talents = dm.get_all_talents()
    status_counts = {}
    for talent in talents:
        status = talent['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    df_status = pd.DataFrame({
        'Status': list(status_counts.keys()),
        'Count': list(status_counts.values())
    })

    fig = px.pie(
        df_status,
        values='Count',
        names='Status',
        color_discrete_sequence=['#EF4444', '#10B981', '#6B7280'],
        hole=0.4
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=14
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True, key="status_pie")

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Engagement Metrics</h3>
            <p class="text-muted">Top 5 talents by engagement score</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    # Calculate engagement scores
    engagement_data = []
    for talent in talents[:5]:  # Top 5
        engagement_score = (
            talent['total_diamonds'] * 0.5 +
            talent['followers'] * 0.3 +
            talent.get('total_streams', 0) * 0.2
        )
        engagement_data.append({
            'Talent': talent['name'],
            'Engagement Score': engagement_score / 1000  # Normalize
        })

    df_engagement = pd.DataFrame(engagement_data)

    fig = go.Figure(data=[
        go.Bar(
            x=df_engagement['Talent'],
            y=df_engagement['Engagement Score'],
            marker=dict(
                color=df_engagement['Engagement Score'],
                colorscale='RdYlGn',
                showscale=False
            ),
            text=df_engagement['Engagement Score'].round(1),
            textposition='auto',
        )
    ])
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    )

    st.plotly_chart(fig, use_container_width=True, key="engagement_chart")

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Detailed Talent Comparison
st.markdown("""
<div class="card">
    <div class="card-header">
        <h3 class="heading-4">🔍 Detailed Talent Comparison</h3>
        <p class="text-muted">Multi-metric performance analysis</p>
    </div>
    <div class="card-content">
""", unsafe_allow_html=True)

selected_talents = st.multiselect(
    "Select talents to compare (max 5)",
    options=[t['name'] for t in dm.get_all_talents()],
    default=[t['name'] for t in dm.get_all_talents()[:3]],
    max_selections=5
)

if selected_talents:
    comparison_data = []
    for name in selected_talents:
        talent = next(t for t in dm.get_all_talents() if t['name'] == name)
        comparison_data.append({
            'Talent': talent['name'],
            'Followers': talent['followers'],
            'Diamonds': talent['total_diamonds'],
            'Streams': talent.get('total_streams', 0),
            'Avg Viewers': talent.get('avg_viewers', 0),
            'Level': talent['level']
        })

    df_comparison = pd.DataFrame(comparison_data)

    # Radar chart
    st.markdown('<div style="margin: 1.5rem 0;">', unsafe_allow_html=True)

    fig = go.Figure()

    categories = ['Followers', 'Diamonds', 'Streams', 'Avg Viewers', 'Level']
    colors = ['hsl(262, 83%, 58%)', 'hsl(280, 83%, 58%)', 'hsl(300, 83%, 58%)',
              'hsl(320, 83%, 58%)', 'hsl(340, 83%, 58%)']

    for idx, row in df_comparison.iterrows():
        # Normalize values for radar chart
        values = [
            row['Followers'] / 1000,  # Normalize
            row['Diamonds'] / 100,
            row['Streams'] / 10,
            row['Avg Viewers'],
            row['Level'] * 10
        ]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=row['Talent'],
            line=dict(color=colors[idx % len(colors)], width=2)
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.1)'
            )
        ),
        showlegend=True,
        height=450,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True, key="radar_comparison")
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed table
    st.markdown("**Detailed Metrics**")
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div class="alert alert-info">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 2rem;">📊</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">Select Talents to Compare</div>
                <div style="font-size: 0.875rem;">Choose up to 5 talents to see detailed comparison</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Export functionality
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="card-header">
        <h3 class="heading-4">📥 Export Reports</h3>
        <p class="text-muted">Download analytics data and reports</p>
    </div>
    <div class="card-content">
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Export CSV", use_container_width=True):
        if selected_talents and len(selected_talents) > 0:
            csv = df_comparison.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV File",
                data=csv,
                file_name="talent_analytics.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Select talents to export")

with col2:
    if st.button("📊 Export Charts", use_container_width=True):
        st.info("Chart export feature (coming soon)")

with col3:
    if st.button("📑 PDF Report", use_container_width=True):
        st.info("PDF report generation (coming soon)")

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 1.5rem 0; color: hsl(var(--muted-foreground));'>
    <p style="font-size: 0.875rem;">📊 Analytics powered by real-time data</p>
    <p style="font-size: 0.75rem; margin-top: 0.25rem;">All metrics updated automatically • Export capabilities available</p>
</div>
""", unsafe_allow_html=True)
