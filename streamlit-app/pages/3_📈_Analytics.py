"""
📈 Analytics & Reports Page
Comprehensive analytics with charts, graphs, and performance reports
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Analytics & Reports",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.title("📈 Analytics & Reports")
st.markdown("Comprehensive analytics and performance insights")
st.markdown("---")

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
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Full report generation feature (coming soon)")

st.markdown("---")

# Key Metrics Overview
st.subheader("📊 Key Performance Indicators")

stats = dm.get_platform_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0;">💰 Total Revenue</h3>
        <h2 style="margin: 0.5rem 0;">${stats['total_diamonds'] * 0.01:,.2f}</h2>
        <p style="margin: 0; opacity: 0.9;">💎 {stats['total_diamonds']:,} diamonds</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h3 style="margin: 0;">👥 Total Followers</h3>
        <h2 style="margin: 0.5rem 0;">{stats['total_followers']:,}</h2>
        <p style="margin: 0; opacity: 0.9;">Across all talents</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h3 style="margin: 0;">📺 Total Streams</h3>
        <h2 style="margin: 0.5rem 0;">{stats['total_streams']:,}</h2>
        <p style="margin: 0; opacity: 0.9;">All time</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
        <h3 style="margin: 0;">📊 Avg Viewers</h3>
        <h2 style="margin: 0.5rem 0;">{stats['avg_viewers_per_stream']:.0f}</h2>
        <p style="margin: 0; opacity: 0.9;">Per stream</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Charts Section
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📈 Platform Growth")

    growth_data = dm.get_talent_growth_data()
    df_growth = pd.DataFrame(growth_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_growth['Month'],
        y=df_growth['New Talents'],
        name='New Talents',
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=df_growth['Month'],
        y=df_growth['Active Talents'],
        name='Active Talents',
        mode='lines+markers',
        line=dict(color='#f093fb', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("💰 Revenue Trends")

    revenue_data = dm.get_revenue_data()
    df_revenue = pd.DataFrame(revenue_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_revenue['Month'],
        y=df_revenue['Diamonds'],
        name='Diamonds',
        marker_color='#4facfe'
    ))
    fig.add_trace(go.Bar(
        x=df_revenue['Month'],
        y=df_revenue['Gifts'],
        name='Gifts',
        marker_color='#fa709a'
    ))

    fig.update_layout(
        height=350,
        barmode='group',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Top Performers
st.subheader("🌟 Top Performers Analysis")

tab1, tab2, tab3 = st.tabs(["💎 By Diamonds", "👥 By Followers", "📺 By Streams"])

with tab1:
    top_diamonds = dm.get_top_talents('total_diamonds', limit=10)
    df_diamonds = pd.DataFrame([{
        'Talent': t['name'],
        'Diamonds': t['total_diamonds'],
        'Level': t['level'],
        'Status': t['status']
    } for t in top_diamonds])

    fig = px.bar(
        df_diamonds,
        x='Talent',
        y='Diamonds',
        color='Level',
        title='Top 10 Talents by Diamonds Earned',
        color_continuous_scale='Purples'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_diamonds, use_container_width=True, hide_index=True)

with tab2:
    top_followers = dm.get_top_talents('followers', limit=10)
    df_followers = pd.DataFrame([{
        'Talent': t['name'],
        'Followers': t['followers'],
        'Level': t['level'],
        'Status': t['status']
    } for t in top_followers])

    fig = px.bar(
        df_followers,
        x='Talent',
        y='Followers',
        color='Level',
        title='Top 10 Talents by Followers',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_followers, use_container_width=True, hide_index=True)

with tab3:
    top_streams = dm.get_top_talents('total_streams', limit=10)
    df_streams = pd.DataFrame([{
        'Talent': t['name'],
        'Total Streams': t.get('total_streams', 0),
        'Avg Viewers': t.get('avg_viewers', 0),
        'Status': t['status']
    } for t in top_streams])

    fig = px.bar(
        df_streams,
        x='Talent',
        y='Total Streams',
        color='Avg Viewers',
        title='Top 10 Talents by Stream Count',
        color_continuous_scale='Greens'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_streams, use_container_width=True, hide_index=True)

st.markdown("---")

# Status Distribution
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 Talent Status Distribution")

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
        title='Current Talent Status',
        color_discrete_sequence=['#ff4444', '#4CAF50', '#9E9E9E']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350)

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🎯 Engagement Metrics")

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

    fig = px.bar(
        df_engagement,
        x='Talent',
        y='Engagement Score',
        title='Top 5 Talents by Engagement Score',
        color='Engagement Score',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=350)

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Detailed Talent Comparison
st.subheader("🔍 Detailed Talent Comparison")

selected_talents = st.multiselect(
    "Select talents to compare (max 5)",
    options=[t['name'] for t in dm.get_all_talents()],
    default=[t['name'] for t in dm.get_all_talents()[:3]]
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
    fig = go.Figure()

    categories = ['Followers', 'Diamonds', 'Streams', 'Avg Viewers', 'Level']

    for _, row in df_comparison.iterrows():
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
            name=row['Talent']
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        height=500,
        title="Multi-Metric Comparison (Normalized)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# Export functionality
st.markdown("---")
st.subheader("📥 Export Reports")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Export to CSV", use_container_width=True):
        csv = df_comparison.to_csv(index=False) if selected_talents else ""
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="talent_analytics.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 Export Charts", use_container_width=True):
        st.info("Chart export feature (coming soon)")

with col3:
    if st.button("📑 Generate PDF Report", use_container_width=True):
        st.info("PDF report generation (coming soon)")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📊 Analytics powered by real-time data</p>
    <p style='font-size: 0.85rem;'>All metrics are updated automatically • Export capabilities available</p>
</div>
""", unsafe_allow_html=True)
