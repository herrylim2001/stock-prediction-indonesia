"""
📱 LiveStream Platform - Main Dashboard
Modern TalentFlow-inspired design
"""
import streamlit as st
import sys
sys.path.append('.')
from utils.data_manager import get_data_manager
from utils.ui_components import get_modern_css, stat_card, badge, avatar, hero_section, sidebar_menu
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="LiveStream Platform - Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply modern CSS
st.markdown(get_modern_css(), unsafe_allow_html=True)

# Sidebar Menu (functional navigation)
with st.sidebar:
    sidebar_menu(active_page="Dashboard")

# Initialize data manager
dm = get_data_manager()

# Get platform stats
stats = dm.get_platform_stats()

# Glassmorphic Hero Section
st.markdown("""
<div class="hero-glass">
    <h1>Welcome back, Admin!</h1>
    <p>You have {0} online talents and {1} active livestreams. Everything looks on track.</p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
        <button class="btn">View Reports</button>
        <button class="btn" style="background: transparent; border: 2px solid white; color: white;">Manage Talents</button>
    </div>
</div>
""".format(stats['online_talents'], len(dm.get_all_livestreams())), unsafe_allow_html=True)

st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

# Overview Stats Section
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <div>
        <h2 class="heading-2">Overview</h2>
        <p class="text-muted">Platform performance metrics</p>
    </div>
    <div style="display: flex; gap: 0.75rem;">
        <button class="btn btn-secondary">Today</button>
        <button class="btn btn-secondary">Export</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Stats Grid
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        label="Total Talents",
        value=str(stats['total_talents']),
        change="+12.5%",
        change_positive=True,
        icon="👥",
        icon_color="purple"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        label="Active Streams",
        value=str(len(dm.get_all_livestreams())),
        change="+4.2%",
        change_positive=True,
        icon="📺",
        icon_color="blue"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(stat_card(
        label="Total Followers",
        value=f"{stats['total_followers']:,}",
        change="+8.3%",
        change_positive=True,
        icon="⭐",
        icon_color="orange"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(stat_card(
        label="Revenue",
        value=f"${stats['total_diamonds'] * 0.01:,.0f}",
        change="+8.1%",
        change_positive=True,
        icon="💰",
        icon_color="green"
    ), unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Main Content Grid
col_main, col_sidebar = st.columns([2, 1])

# Left Column - Top Performers
with col_main:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">🌟 Top Performers</h3>
            <p class="text-muted">Ranked by total diamonds earned</p>
        </div>
    """, unsafe_allow_html=True)

    # Get top talents
    top_talents = dm.get_top_talents('total_diamonds', limit=8)

    for i, talent in enumerate(top_talents, 1):
        # Status badge variant
        status_variant = {
            "live": "error",
            "online": "success",
            "offline": "default"
        }.get(talent['status'], "default")

        status_icon = {
            "live": "🔴",
            "online": "🟢",
            "offline": "⚫"
        }.get(talent['status'], "⚫")

        st.markdown(f"""
        <div class="table-row">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="width: 40px; text-align: center;">
                    <span style="font-weight: 700; font-size: 1.25rem; color: hsl(var(--foreground-muted));">#{i}</span>
                </div>
                {avatar(talent['avatar'], size='md', status=talent['status'])}
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.25rem;">{talent['name']}</div>
                    <div class="text-muted">@{talent['username']}</div>
                </div>
                <div>
                    {badge(f"{status_icon} {talent['status'].upper()}", variant=status_variant)}
                </div>
                <div style="text-align: right; min-width: 140px;">
                    <div style="font-weight: 700; font-size: 1.1rem; color: hsl(var(--primary));">💎 {talent['total_diamonds']:,}</div>
                    <div class="text-muted">{talent['followers']:,} followers</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Right Column - Platform Metrics
with col_sidebar:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">📈 Platform Metrics</h3>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    # Total Followers
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div class="text-muted" style="margin-bottom: 0.5rem;">Total Followers</div>
        <div style="font-size: 2rem; font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif; color: hsl(var(--foreground));">
            {stats['total_followers']:,}
        </div>
        <div class="stat-card-change positive" style="margin-top: 0.5rem;">↗ +2.5K this month</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="separator" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Total Streams
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div class="text-muted" style="margin-bottom: 0.5rem;">Total Streams</div>
        <div style="font-size: 2rem; font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif; color: hsl(var(--foreground));">
            {stats['total_streams']:,}
        </div>
        <div class="stat-card-change positive" style="margin-top: 0.5rem;">↗ +156 this month</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="separator" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Avg Viewers
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div class="text-muted" style="margin-bottom: 0.5rem;">Avg Viewers/Stream</div>
        <div style="font-size: 2rem; font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif; color: hsl(var(--foreground));">
            {stats['avg_viewers_per_stream']:.0f}
        </div>
        <div class="stat-card-change positive" style="margin-top: 0.5rem;">↗ +12.3% increase</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="separator" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Online Rate
    online_rate = (stats['online_talents'] / stats['total_talents'] * 100)
    st.markdown(f"""
    <div>
        <div class="text-muted" style="margin-bottom: 0.5rem;">Online Rate</div>
        <div style="font-size: 2rem; font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif; color: hsl(var(--foreground));">
            {online_rate:.0f}%
        </div>
        <div class="text-muted" style="margin-top: 0.5rem;">{stats['online_talents']} of {stats['total_talents']} talents</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Active Livestreams Section
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <div>
        <h2 class="heading-3">📡 Currently Broadcasting</h2>
        <p class="text-muted">Live streams happening now</p>
    </div>
</div>
""", unsafe_allow_html=True)

recent_livestreams = dm.get_all_livestreams()

if recent_livestreams:
    # Create grid of livestream cards
    cols = st.columns(3)

    for idx, ls in enumerate(recent_livestreams[:6]):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card hover-lift" style="cursor: pointer;">
                <div style="position: relative; padding-top: 56.25%; background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%); overflow: hidden;">
                    <img src="{ls['thumbnail']}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
                    <div style="position: absolute; top: 0.75rem; left: 0.75rem;">
                        <span class="badge badge-error">
                            <span style="animation: pulse-live 2s infinite;">🔴</span> LIVE
                        </span>
                    </div>
                    <div style="position: absolute; top: 0.75rem; right: 0.75rem; background: rgba(0,0,0,0.75); backdrop-filter: blur(10px); color: white; padding: 0.375rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.875rem; font-weight: 600;">
                        👁️ {ls['viewers']:,}
                    </div>
                </div>
                <div style="padding: 1.25rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                        {avatar(ls.get('talent_avatar', 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + ls['talent_name']), size='sm', status='live')}
                        <div style="flex: 1; overflow: hidden;">
                            <div style="font-weight: 600; font-size: 0.875rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{ls['talent_name']}</div>
                            <div class="text-muted" style="font-size: 0.75rem;">@{ls['talent_username']}</div>
                        </div>
                    </div>
                    <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 0.75rem; color: hsl(var(--foreground)); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {ls['title']}
                    </div>
                    <div style="display: flex; gap: 1rem; font-size: 0.75rem; color: hsl(var(--foreground-muted));">
                        <span>❤️ {ls['likes']:,}</span>
                        <span>💎 {ls['diamonds']:,}</span>
                        <span>💬 {ls['comments']:,}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert alert-info">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">📺</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">No Active Livestreams</div>
                <div style="font-size: 0.875rem;">Check back later for live shows!</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Quick Links Section
st.markdown("""
<div class="card">
    <div class="card-header">
        <h3 class="heading-4">🚀 Quick Actions</h3>
        <p class="text-muted">Navigate to key platform features</p>
    </div>
    <div class="card-content">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
            <div style="padding: 1.5rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border)); transition: all 0.2s ease; cursor: pointer;" onmouseover="this.style.borderColor='hsl(var(--border-hover))'" onmouseout="this.style.borderColor='hsl(var(--border))'">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">👥</div>
                <div style="font-weight: 600; margin-bottom: 0.5rem;">Talent Management</div>
                <p class="text-muted" style="margin: 0;">View and manage all talents, edit profiles, track performance</p>
            </div>
            <div style="padding: 1.5rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border)); transition: all 0.2s ease; cursor: pointer;" onmouseover="this.style.borderColor='hsl(var(--border-hover))'" onmouseout="this.style.borderColor='hsl(var(--border))'">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📺</div>
                <div style="font-weight: 600; margin-bottom: 0.5rem;">Livestreams</div>
                <p class="text-muted" style="margin: 0;">Monitor active streams, viewer counts, engagement metrics</p>
            </div>
            <div style="padding: 1.5rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border)); transition: all 0.2s ease; cursor: pointer;" onmouseover="this.style.borderColor='hsl(var(--border-hover))'" onmouseout="this.style.borderColor='hsl(var(--border))'">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📈</div>
                <div style="font-weight: 600; margin-bottom: 0.5rem;">Analytics</div>
                <p class="text-muted" style="margin: 0;">Comprehensive analytics with charts, graphs, detailed reports</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: hsl(var(--foreground-muted));">
    <p style="font-weight: 600; font-size: 1rem; font-family: 'Plus Jakarta Sans', sans-serif;">LiveStream Platform</p>
    <p style="font-size: 0.875rem; margin-top: 0.5rem;">Professional Broadcasting Platform Management • v1.0</p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem; color: hsl(var(--foreground-light));">© 2025 - Powered by Modern Design System</p>
</div>
""", unsafe_allow_html=True)
