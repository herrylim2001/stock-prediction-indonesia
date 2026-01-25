"""
📺 Livestream Monitoring Page
Modern TalentFlow-inspired design
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
from utils.ui_components import get_modern_css, badge, stat_card, avatar, sidebar_menu
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Livestream Monitoring",
    page_icon="📺",
    layout="wide"
)

# Apply modern CSS
st.markdown(get_modern_css(), unsafe_allow_html=True)

# Sidebar Menu (functional navigation)
with st.sidebar:
    sidebar_menu(active_page="Livestreams")

# Initialize data manager
dm = get_data_manager()

# Header
st.markdown("""
<div style="margin-bottom: 2.5rem;">
    <h1 class="heading-1">📺 Livestream Monitoring</h1>
    <p class="text-muted" style="font-size: 1.125rem; margin-top: 0.75rem;">
        Monitor all active livestreams and engagement metrics in real-time
    </p>
</div>
""", unsafe_allow_html=True)

# Controls and Filters
st.markdown("""
<div class="card" style="margin-bottom: 2rem;">
    <div class="card-content" style="padding: 1.25rem;">
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    category_filter = st.multiselect(
        "Filter by Category",
        options=["Gaming", "Lifestyle", "Music", "Fitness", "Cooking", "Tech", "General"],
        default=[]
    )

with col2:
    sort_option = st.selectbox(
        "Sort by",
        ["Viewers (High to Low)", "Viewers (Low to High)", "Likes", "Diamonds", "Latest"]
    )

with col3:
    auto_refresh = st.checkbox("🔁 Auto-refresh")
    if auto_refresh:
        st.caption("*Monitoring...*")

with col4:
    st.markdown("###")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Get livestreams
livestreams = dm.get_all_livestreams()

# Apply filters
if category_filter:
    livestreams = [ls for ls in livestreams if ls.get('category') in category_filter]

# Apply sorting
if sort_option == "Viewers (High to Low)":
    livestreams = sorted(livestreams, key=lambda x: x['viewers'], reverse=True)
elif sort_option == "Viewers (Low to High)":
    livestreams = sorted(livestreams, key=lambda x: x['viewers'])
elif sort_option == "Likes":
    livestreams = sorted(livestreams, key=lambda x: x['likes'], reverse=True)
elif sort_option == "Diamonds":
    livestreams = sorted(livestreams, key=lambda x: x['diamonds'], reverse=True)

# Summary metrics
total_viewers = sum(ls['viewers'] for ls in livestreams)
total_likes = sum(ls['likes'] for ls in livestreams)
total_diamonds = sum(ls['diamonds'] for ls in livestreams)
avg_viewers = total_viewers / len(livestreams) if livestreams else 0

# Stats Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        label="Active Livestreams",
        value=str(len(livestreams)),
        change="+4" if len(livestreams) > 0 else None,
        change_positive=True,
        icon="🔴",
        icon_color="orange"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        label="Total Viewers",
        value=f"{total_viewers:,}",
        change=f"Avg {int(avg_viewers):,}" if livestreams else None,
        change_positive=True,
        icon="👁️",
        icon_color="blue"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(stat_card(
        label="Total Likes",
        value=f"{total_likes:,}",
        icon="❤️",
        icon_color="purple"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(stat_card(
        label="Total Diamonds",
        value=f"{total_diamonds:,}",
        icon="💎",
        icon_color="green"
    ), unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Active Livestreams Section
if livestreams:
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h2 class="heading-3">📡 Active Livestreams</h2>
        <p class="text-muted">Showing {len(livestreams)} active stream(s)</p>
    </div>
    """, unsafe_allow_html=True)

    for ls in livestreams:
        # Livestream Card
        st.markdown(f"""
        <div class="card hover-lift" style="margin-bottom: 1.5rem;">
            <div style="padding: 0;">
                <div style="display: flex; gap: 0;">
        """, unsafe_allow_html=True)

        col_thumb, col_info = st.columns([1, 2])

        with col_thumb:
            # Thumbnail with LIVE badge
            st.markdown(f"""
            <div style="position: relative; border-radius: var(--radius-lg) 0 0 var(--radius-lg); overflow: hidden; border-right: 1px solid hsl(var(--border));">
                <img src="{ls['thumbnail']}" style="width: 100%; display: block; aspect-ratio: 16/9; object-fit: cover;">
                <div style="position: absolute; top: 1rem; left: 1rem;">
                    <span class="badge badge-error pulse-animation">
                        <span style="animation: pulse-live 2s infinite;">🔴</span> LIVE
                    </span>
                </div>
                <div style="position: absolute; top: 1rem; right: 1rem; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); color: white; padding: 0.5rem 0.875rem; border-radius: var(--radius); font-weight: 600; font-size: 0.875rem;">
                    👁️ {ls['viewers']:,}
                </div>
                <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%); padding: 1.5rem 1rem 1rem;">
                    <div style="color: white; font-size: 0.75rem; opacity: 0.9;">
                        Started: {datetime.fromisoformat(ls['started_at']).strftime('%H:%M')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            # Stream Info
            st.markdown(f"""
            <div style="padding: 1.5rem;">
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                        {avatar(ls.get('talent_avatar', 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + ls['talent_name']), size='md', status='live')}
                        <div>
                            <div style="font-weight: 600; font-size: 1rem;">{ls['talent_name']}</div>
                            <div class="text-muted" style="font-size: 0.875rem;">@{ls['talent_username']}</div>
                        </div>
                        {badge(ls.get('category', 'General'), variant='primary')}
                    </div>
                    <h3 class="heading-4" style="margin-bottom: 0.5rem;">{ls['title']}</h3>
            """, unsafe_allow_html=True)

            if ls.get('description'):
                st.markdown(f"""
                    <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 1rem;">
                        {ls['description']}
                    </p>
                """, unsafe_allow_html=True)

            st.markdown("""
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem;">
            """, unsafe_allow_html=True)

            # Stats Grid
            st.markdown(f"""
                    <div style="text-align: center; padding: 0.75rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border));">
                        <div style="font-size: 1.25rem; font-weight: 700; color: hsl(var(--primary)); margin-bottom: 0.25rem;">{ls['viewers']:,}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Viewers</div>
                    </div>
                    <div style="text-align: center; padding: 0.75rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border));">
                        <div style="font-size: 1.25rem; font-weight: 700; color: hsl(var(--error)); margin-bottom: 0.25rem;">❤️ {ls['likes']:,}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Likes</div>
                    </div>
                    <div style="text-align: center; padding: 0.75rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border));">
                        <div style="font-size: 1.25rem; font-weight: 700; color: hsl(var(--success)); margin-bottom: 0.25rem;">💎 {ls['diamonds']:,}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Diamonds</div>
                    </div>
                    <div style="text-align: center; padding: 0.75rem; background: hsl(var(--background)); border-radius: var(--radius); border: 1px solid hsl(var(--border));">
                        <div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">💬 {ls['comments']:,}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Comments</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Tags
            if ls.get('tags'):
                tag_html = " ".join([badge(f'#{tag}', variant='default') for tag in ls['tags']])
                st.markdown(f'<div style="margin-bottom: 1rem;">{tag_html}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Action Buttons
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            if st.button("📊 Details", key=f"details_{ls['id']}", use_container_width=True):
                st.session_state.selected_stream = ls['id']
        with col_b:
            if st.button("💬 Chat", key=f"chat_{ls['id']}", use_container_width=True):
                st.info("Chat view feature (coming soon)")
        with col_c:
            if st.button("📈 Analytics", key=f"analytics_{ls['id']}", use_container_width=True):
                st.info("Stream analytics feature (coming soon)")
        with col_d:
            if st.button("⛔ End", key=f"end_{ls['id']}", type="secondary", use_container_width=True):
                if dm.end_livestream(ls['id']):
                    st.success(f"✅ Livestream ended: {ls['title']}")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Analytics Charts
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">📊 Session Analytics</h3>
            <p class="text-muted">Performance overview across all active streams</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👁️ Viewer Distribution**")
        viewer_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Viewers': [ls['viewers'] for ls in livestreams]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=viewer_data['Talent'],
                y=viewer_data['Viewers'],
                marker=dict(
                    color='hsl(250, 70%, 60%)',
                    line=dict(color='hsl(250, 70%, 50%)', width=1)
                ),
                text=viewer_data['Viewers'],
                textposition='auto',
            )
        ])
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif', color='hsl(222, 47%, 11%)'),
            xaxis=dict(showgrid=False, showline=False),
            yaxis=dict(showgrid=True, gridcolor='hsl(220, 13%, 91%)', showline=False)
        )
        st.plotly_chart(fig, use_container_width=True, key="viewer_dist")

    with col2:
        st.markdown("**💎 Revenue Distribution**")
        diamond_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Diamonds': [ls['diamonds'] for ls in livestreams]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=diamond_data['Talent'],
                y=diamond_data['Diamonds'],
                marker=dict(
                    color='hsl(142, 71%, 45%)',
                    line=dict(color='hsl(142, 71%, 35%)', width=1)
                ),
                text=diamond_data['Diamonds'],
                textposition='auto',
            )
        ])
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, sans-serif', color='hsl(222, 47%, 11%)'),
            xaxis=dict(showgrid=False, showline=False),
            yaxis=dict(showgrid=True, gridcolor='hsl(220, 13%, 91%)', showline=False)
        )
        st.plotly_chart(fig, use_container_width=True, key="diamond_dist")

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # No livestreams
    st.markdown("""
    <div class="alert alert-info">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 3rem;">📺</div>
            <div>
                <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.5rem;">No Active Livestreams</div>
                <div style="font-size: 0.875rem;">Start a new livestream to begin monitoring</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # Quick Start Section
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">⚡ Quick Start Livestream</h3>
            <p class="text-muted">Launch a new livestream instantly</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    with st.form("quick_create_stream"):
        col1, col2 = st.columns(2)

        with col1:
            available_talents = [t for t in dm.get_all_talents() if t['status'] != 'live']
            if available_talents:
                selected_talent = st.selectbox(
                    "Select Talent",
                    options=[t['name'] for t in available_talents]
                )
            else:
                st.warning("⚠️ No available talents (all are already live)")
                selected_talent = None

        with col2:
            stream_title = st.text_input(
                "Stream Title",
                value=f"{selected_talent}'s Live Stream" if selected_talent else ""
            )

        stream_desc = st.text_area("Description (optional)", placeholder="Enter stream description...")

        category = st.selectbox(
            "Category",
            options=["Gaming", "Lifestyle", "Music", "Fitness", "Cooking", "Tech", "General"]
        )

        col_submit, col_cancel = st.columns([1, 4])
        with col_submit:
            submit = st.form_submit_button("🚀 Start Stream", use_container_width=True, type="primary")

        if submit and selected_talent:
            talent = next(t for t in available_talents if t['name'] == selected_talent)
            new_stream = dm.create_livestream(
                talent['id'],
                stream_title,
                stream_desc
            )
            if new_stream:
                st.success(f"✅ Livestream started: {stream_title}")
                st.rerun()

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0; color: hsl(var(--foreground-muted));">
    <p style="font-size: 0.875rem;">
        {f"Monitoring {len(livestreams)} active stream(s)" if livestreams else "Ready to start monitoring"}
    </p>
    <p style="font-size: 0.75rem; margin-top: 0.25rem;">Real-time monitoring • Live updates • Engagement tracking</p>
</div>
""", unsafe_allow_html=True)
