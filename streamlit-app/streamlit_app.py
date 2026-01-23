"""
🎥 LiveStream Platform - Professional Dashboard
Streamlit App dengan shadcn/ui inspired design
"""
import streamlit as st
from utils.data_manager import get_data_manager
from utils.ui_components import get_shadcn_css, stat_card, card, badge, avatar
import pandas as pd

# Page config
st.set_page_config(
    page_title="LiveStream Platform - Dashboard",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply shadcn/ui CSS
st.markdown(get_shadcn_css(), unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header Section
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 class="heading-1">🎥 LiveStream Platform</h1>
    <p class="text-muted" style="font-size: 1rem; margin-top: 0.5rem;">
        Professional broadcasting platform management system
    </p>
</div>
""", unsafe_allow_html=True)

# Top Action Bar
col_left, col_right = st.columns([3, 1])
with col_right:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_top"):
        st.cache_resource.clear()
        st.rerun()

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Get platform stats
stats = dm.get_platform_stats()

# Statistics Cards with professional shadcn design
st.markdown("### 📊 Platform Overview")
st.markdown('<div class="grid grid-cols-4" style="margin-top: 1rem; margin-bottom: 2rem;">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        title="Total Talents",
        value=f"{stats['total_talents']}",
        description=f"{stats['online_talents']} currently online",
        icon="👥",
        color="blue"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        title="Live Streams",
        value=f"{stats['active_livestreams']}",
        description="Active broadcasts",
        icon="📺",
        color="green"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(stat_card(
        title="Total Viewers",
        value=f"{stats['total_viewers']:,}",
        description="Watching now",
        icon="👁️",
        color="purple"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(stat_card(
        title="Total Revenue",
        value=f"💎 {stats['total_diamonds']:,}",
        description="Diamonds earned",
        icon="💰",
        color="orange"
    ), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Main Content Grid
col_main, col_sidebar = st.columns([2, 1])

# Left Column - Top Performers
with col_main:
    st.markdown("""
    <div class="card" style="padding: 0;">
        <div class="card-header">
            <h3 class="heading-4">🌟 Top Performers</h3>
            <p class="text-muted">Ranked by total diamonds earned</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    top_talents = dm.get_top_talents('total_diamonds', limit=8)

    # Create professional table
    for i, talent in enumerate(top_talents, 1):
        status_color = {
            "live": "error",
            "online": "success",
            "offline": "secondary"
        }.get(talent['status'], "secondary")

        status_emoji = {
            "live": "🔴",
            "online": "🟢",
            "offline": "⚫"
        }.get(talent['status'], "⚫")

        st.markdown(f"""
        <div class="table-row" style="display: flex; align-items: center; padding: 1rem 0;">
            <div style="width: 50px; text-align: center; font-weight: 700; font-size: 1.25rem; color: hsl(var(--muted-foreground));">
                #{i}
            </div>
            <div style="flex: 0 0 48px;">
                {avatar(talent['avatar'], size='md', status=talent['status'])}
            </div>
            <div style="flex: 1; margin-left: 1rem;">
                <div style="font-weight: 600; font-size: 0.95rem;">{talent['name']}</div>
                <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem;">@{talent['username']}</div>
            </div>
            <div style="margin: 0 1rem;">
                {badge(f"{status_emoji} {talent['status'].upper()}", variant=status_color)}
            </div>
            <div style="text-align: right; min-width: 120px;">
                <div style="font-weight: 700; font-size: 1.1rem;">💎 {talent['total_diamonds']:,}</div>
                <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">{talent['followers']:,} followers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# Right Column - Quick Stats & Metrics
with col_sidebar:
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">📈 Platform Metrics</h3>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    # Metrics
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-bottom: 0.25rem;">Total Followers</div>
        <div style="font-size: 1.75rem; font-weight: 700;">{stats['total_followers']:,}</div>
        <div style="color: hsl(142 76% 36%); font-size: 0.875rem; margin-top: 0.25rem;">
            <span style="font-weight: 600;">↗ +2.5K</span> this month
        </div>
    </div>
    <div class="separator"></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-bottom: 0.25rem;">Total Streams</div>
        <div style="font-size: 1.75rem; font-weight: 700;">{stats['total_streams']:,}</div>
        <div style="color: hsl(142 76% 36%); font-size: 0.875rem; margin-top: 0.25rem;">
            <span style="font-weight: 600;">↗ +156</span> this month
        </div>
    </div>
    <div class="separator"></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-bottom: 0.25rem;">Avg Viewers/Stream</div>
        <div style="font-size: 1.75rem; font-weight: 700;">{stats['avg_viewers_per_stream']:.0f}</div>
        <div style="color: hsl(142 76% 36%); font-size: 0.875rem; margin-top: 0.25rem;">
            <span style="font-weight: 600;">↗ +12.3%</span> increase
        </div>
    </div>
    <div class="separator"></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div>
        <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-bottom: 0.25rem;">Online Rate</div>
        <div style="font-size: 1.75rem; font-weight: 700;">{(stats['online_talents']/stats['total_talents']*100):.0f}%</div>
        <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-top: 0.25rem;">
            {stats['online_talents']} of {stats['total_talents']} talents
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Active Livestreams Section
st.markdown("""
<div style="margin: 2rem 0 1rem 0;">
    <h2 class="heading-3">📡 Active Livestreams</h2>
    <p class="text-muted" style="margin-top: 0.5rem;">Currently broadcasting</p>
</div>
""", unsafe_allow_html=True)

recent_livestreams = dm.get_all_livestreams()

if recent_livestreams:
    # Create grid of livestream cards
    cols = st.columns(3)

    for idx, ls in enumerate(recent_livestreams[:6]):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card" style="cursor: pointer; transition: all 0.3s ease;">
                <div style="position: relative; padding-top: 56.25%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 0.5rem 0.5rem 0 0; overflow: hidden;">
                    <img src="{ls['thumbnail']}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
                    <div style="position: absolute; top: 0.75rem; left: 0.75rem;">
                        {badge("🔴 LIVE", variant="error")}
                    </div>
                    <div style="position: absolute; top: 0.75rem; right: 0.75rem; background: rgba(0,0,0,0.75); color: white; padding: 0.375rem 0.75rem; border-radius: 0.375rem; font-size: 0.875rem; font-weight: 600;">
                        👁️ {ls['viewers']}
                    </div>
                </div>
                <div style="padding: 1.25rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                        {avatar(ls['talent_avatar'], size='sm', status='live')}
                        <div>
                            <div style="font-weight: 600; font-size: 0.95rem;">{ls['talent_name']}</div>
                            <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem;">@{ls['talent_username']}</div>
                        </div>
                    </div>
                    <div style="font-weight: 500; font-size: 0.9rem; margin-bottom: 0.75rem; color: hsl(var(--foreground));">
                        {ls['title']}
                    </div>
                    <div style="display: flex; gap: 1rem; font-size: 0.875rem; color: hsl(var(--muted-foreground));">
                        <span>❤️ {ls['likes']}</span>
                        <span>💎 {ls['diamonds']}</span>
                        <span>💬 {ls['comments']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert alert-info">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 2rem;">🎬</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">No Active Livestreams</div>
                <div style="font-size: 0.875rem;">Check back later for live shows!</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Navigation Guide
st.markdown("""
<div class="card">
    <div class="card-header">
        <h3 class="heading-4">🧭 Quick Navigation</h3>
    </div>
    <div class="card-content">
        <div class="grid grid-cols-3" style="gap: 1.5rem;">
            <div>
                <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">👥</span>
                    <span>Talent Management</span>
                </div>
                <p class="text-muted">View and manage all talents, edit profiles, and track performance metrics.</p>
            </div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">📺</span>
                    <span>Livestreams</span>
                </div>
                <p class="text-muted">Monitor active livestreams, viewer counts, and engagement metrics in real-time.</p>
            </div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">📈</span>
                    <span>Analytics</span>
                </div>
                <p class="text-muted">Comprehensive analytics with charts, graphs, and detailed performance reports.</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0; color: hsl(var(--muted-foreground));">
    <p style="font-weight: 600; font-size: 0.95rem;">LiveStream Platform</p>
    <p style="font-size: 0.875rem; margin-top: 0.25rem;">Professional Broadcasting Platform Management • v1.0</p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem;">© 2025 - Built with Streamlit & shadcn/ui Design System</p>
</div>
""", unsafe_allow_html=True)
