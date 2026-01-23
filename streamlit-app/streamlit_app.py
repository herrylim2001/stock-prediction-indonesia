"""
🎥 LiveStream Platform - Dashboard & Management
Streamlit App untuk manage livestreaming platform seperti Bigo Live & Hot51
"""
import streamlit as st
from utils.data_manager import get_data_manager
import pandas as pd

# Page config
st.set_page_config(
    page_title="LiveStream Platform",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .feature-card {
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1 class="main-header">🎥 LiveStream Platform</h1>', unsafe_allow_html=True)
    st.markdown("**Dashboard & Management System** - Prototype untuk Broadcasting Platform")

with col2:
    st.markdown("### ")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

st.markdown("---")

# Get platform stats
stats = dm.get_platform_stats()

# Statistics Cards
st.markdown("### 📊 Platform Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">👥 Total Talents</div>
        <div class="stat-value">{stats['total_talents']}</div>
        <div class="stat-label">{stats['online_talents']} Online</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="stat-label">📺 Active Streams</div>
        <div class="stat-value">{stats['active_livestreams']}</div>
        <div class="stat-label">Live Now</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="stat-label">👁️ Total Viewers</div>
        <div class="stat-value">{stats['total_viewers']:,}</div>
        <div class="stat-label">Watching Now</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
        <div class="stat-label">💎 Total Diamonds</div>
        <div class="stat-value">{stats['total_diamonds']:,}</div>
        <div class="stat-label">All Time</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Quick Stats
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌟 Top Performers (Diamonds)")
    top_talents = dm.get_top_talents('total_diamonds', limit=5)

    for i, talent in enumerate(top_talents, 1):
        with st.container():
            col_a, col_b, col_c = st.columns([1, 4, 2])
            with col_a:
                st.markdown(f"**#{i}**")
            with col_b:
                status_emoji = {"live": "🔴", "online": "🟢", "offline": "⚫"}
                st.markdown(f"{status_emoji.get(talent['status'], '⚫')} **{talent['name']}**")
            with col_c:
                st.markdown(f"💎 {talent['total_diamonds']:,}")

with col2:
    st.markdown("### 📈 Platform Metrics")

    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:
        st.metric(
            label="Total Followers",
            value=f"{stats['total_followers']:,}",
            delta="+2.5K this month"
        )
        st.metric(
            label="Total Streams",
            value=f"{stats['total_streams']:,}",
            delta="+156 this month"
        )

    with metrics_col2:
        st.metric(
            label="Avg Viewers/Stream",
            value=f"{stats['avg_viewers_per_stream']:.0f}",
            delta="+12.3%"
        )
        st.metric(
            label="Active Talents",
            value=f"{stats['online_talents']} / {stats['total_talents']}",
            delta=f"{(stats['online_talents']/stats['total_talents']*100):.0f}% online"
        )

st.markdown("---")

# Features Overview
st.markdown("### 🎯 Platform Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>👥 Talent Management</h3>
        <p>Manage all talents, update profiles, track performance, and monitor status in real-time.</p>
        <ul>
            <li>View all talents</li>
            <li>Edit profiles & status</li>
            <li>Track statistics</li>
            <li>Performance metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📺 Livestream Monitoring</h3>
        <p>Monitor all active livestreams, viewer counts, engagement metrics, and revenue.</p>
        <ul>
            <li>Active streams</li>
            <li>Real-time viewers</li>
            <li>Engagement stats</li>
            <li>Revenue tracking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Analytics & Reports</h3>
        <p>Comprehensive analytics with charts, graphs, and detailed performance reports.</p>
        <ul>
            <li>Growth analytics</li>
            <li>Revenue reports</li>
            <li>Trend analysis</li>
            <li>Engagement metrics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Navigation Guide
st.markdown("### 🧭 Navigation")

st.info("""
**📱 Gunakan sidebar di sebelah kiri untuk navigasi:**

- **📊 Dashboard** - Overview & statistics (halaman ini)
- **👥 Talent Management** - Manage all talents
- **📺 Livestreams** - Monitor active livestreams
- **📈 Analytics** - Detailed analytics & reports
""")

# Recent Activity
st.markdown("### 🕐 Recent Activity")

recent_livestreams = dm.get_all_livestreams()[:3]

if recent_livestreams:
    for ls in recent_livestreams:
        with st.expander(f"🔴 {ls['title']} - {ls['viewers']} viewers"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Talent:** {ls['talent_name']}")
                st.markdown(f"**Category:** {ls['category']}")
            with col2:
                st.markdown(f"**👁️ Viewers:** {ls['viewers']}")
                st.markdown(f"**❤️ Likes:** {ls['likes']}")
            with col3:
                st.markdown(f"**💎 Diamonds:** {ls['diamonds']}")
                st.markdown(f"**💬 Comments:** {ls['comments']}")
else:
    st.info("No active livestreams at the moment.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>LiveStream Platform</strong> - Demo Version 1.0</p>
    <p>Prototype untuk Broadcasting Platform Management System</p>
    <p style='font-size: 0.8rem;'>© 2025 - Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
