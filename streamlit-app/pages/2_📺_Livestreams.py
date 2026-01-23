"""
📺 Livestream Monitoring Page
Professional livestream monitoring with shadcn/ui design
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
from utils.ui_components import get_shadcn_css, badge, stat_card, card, avatar
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Livestream Monitoring",
    page_icon="📺",
    layout="wide"
)

# Apply shadcn CSS
st.markdown(get_shadcn_css(), unsafe_allow_html=True)

# Additional custom CSS for livestream-specific elements
st.markdown("""
<style>
    @keyframes pulse-live {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .pulse-animation {
        animation: pulse-live 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 class="heading-1">📺 Livestream Monitoring</h1>
    <p class="text-muted" style="font-size: 1rem; margin-top: 0.5rem;">
        Monitor all active livestreams and engagement metrics in real-time
    </p>
</div>
""", unsafe_allow_html=True)

# Controls
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

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        title="Active Livestreams",
        value=str(len(livestreams)),
        description="Currently broadcasting",
        icon="🔴",
        color="red"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        title="Total Viewers",
        value=f"{total_viewers:,}",
        description=f"Avg {int(avg_viewers):,} per stream",
        icon="👁️",
        color="blue"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(stat_card(
        title="Total Likes",
        value=f"{total_likes:,}",
        description="Engagement across streams",
        icon="❤️",
        color="pink"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(stat_card(
        title="Total Diamonds",
        value=f"{total_diamonds:,}",
        description="Revenue generated",
        icon="💎",
        color="purple"
    ), unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Display livestreams
if livestreams:
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 class="heading-3">📡 Active Livestreams</h2>
        <p class="text-muted">Showing {len(livestreams)} active stream(s)</p>
    </div>
    """, unsafe_allow_html=True)

    for ls in livestreams:
        # Livestream card
        st.markdown(f"""
        <div class="card">
            <div style="padding: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                    <div style="display: flex; gap: 0.75rem; align-items: center;">
                        <span class="pulse-animation">{badge('🔴 LIVE', variant='error')}</span>
                        {badge(ls.get('category', 'General'), variant='default')}
                    </div>
                    <div class="text-muted" style="font-size: 0.875rem;">
                        Started: {datetime.fromisoformat(ls['started_at']).strftime('%H:%M')}
                    </div>
                </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])

        with col1:
            # Thumbnail with live indicator
            st.markdown(f"""
            <div style="position: relative; border-radius: var(--radius); overflow: hidden; border: 2px solid hsl(var(--error));">
                <img src="{ls['thumbnail']}" style="width: 100%; display: block; aspect-ratio: 16/9; object-fit: cover;">
                <div style="position: absolute; top: 0.5rem; left: 0.5rem; background: hsl(var(--error)); color: white; padding: 0.25rem 0.75rem; border-radius: var(--radius); font-size: 0.75rem; font-weight: 600;">
                    LIVE
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Stream info
            st.markdown(f"""
            <div style="padding-left: 1rem;">
                <h3 class="heading-4" style="margin-bottom: 0.75rem;">{ls['title']}</h3>
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    {avatar(ls.get('talent_avatar', 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + ls['talent_name']), size='sm')}
                    <div>
                        <div style="font-weight: 600; font-size: 0.95rem;">{ls['talent_name']}</div>
                        <div class="text-muted" style="font-size: 0.875rem;">@{ls['talent_username']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if ls.get('description'):
                st.markdown(f"""
                <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 1rem; font-style: italic;">
                    {ls['description']}
                </p>
                """, unsafe_allow_html=True)

            # Stats grid
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.75rem; background: hsl(var(--muted)); border-radius: var(--radius);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: hsl(var(--primary));">{ls['viewers']:,}</div>
                    <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.25rem;">👁️ Viewers</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.75rem; background: hsl(var(--muted)); border-radius: var(--radius);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: hsl(var(--error));">{ls['likes']:,}</div>
                    <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.25rem;">❤️ Likes</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.75rem; background: hsl(var(--muted)); border-radius: var(--radius);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: hsl(var(--primary));">{ls['diamonds']:,}</div>
                    <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.25rem;">💎 Diamonds</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_col4:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.75rem; background: hsl(var(--muted)); border-radius: var(--radius);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: hsl(var(--muted-foreground));">{ls['comments']:,}</div>
                    <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.25rem;">💬 Comments</div>
                </div>
                """, unsafe_allow_html=True)

            # Tags
            if ls.get('tags'):
                st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
                tag_html = " ".join([badge(f'#{tag}', variant='secondary') for tag in ls['tags']])
                st.markdown(tag_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div></div>', unsafe_allow_html=True)

        # Actions
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

        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # Overall stats
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
        # Viewer distribution
        st.markdown("**👁️ Viewer Distribution**")
        viewer_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Viewers': [ls['viewers'] for ls in livestreams]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=viewer_data['Talent'],
                y=viewer_data['Viewers'],
                marker_color='hsl(262, 83%, 58%)',
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
            font=dict(family='Inter, sans-serif'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True, key="viewer_dist")

    with col2:
        # Revenue (Diamonds)
        st.markdown("**💎 Revenue Distribution**")
        diamond_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Diamonds': [ls['diamonds'] for ls in livestreams]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=diamond_data['Talent'],
                y=diamond_data['Diamonds'],
                marker_color='hsl(280, 83%, 58%)',
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
            font=dict(family='Inter, sans-serif'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
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
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 2rem;">📺</div>
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">No Active Livestreams</div>
                <div style="font-size: 0.875rem;">Start a new livestream to begin monitoring</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # Quick create livestream
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

        col_submit, col_cancel = st.columns([1, 3])
        with col_submit:
            submit = st.form_submit_button("🚀 Start Stream", use_container_width=True)

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

    # Instructions
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="background: hsl(var(--muted)); border: 1px dashed hsl(var(--border));">
        <div style="padding: 1.5rem;">
            <h4 class="heading-5" style="margin-bottom: 1rem;">💡 How to Start a Livestream</h4>
            <div style="display: grid; gap: 0.75rem;">
                <div style="display: flex; align-items: start; gap: 0.75rem;">
                    <div style="background: hsl(var(--primary)); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0;">1</div>
                    <div>
                        <div style="font-weight: 500;">Navigate to Talent Management</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Go to 👥 Talent Management page</div>
                    </div>
                </div>
                <div style="display: flex; align-items: start; gap: 0.75rem;">
                    <div style="background: hsl(var(--primary)); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0;">2</div>
                    <div>
                        <div style="font-weight: 500;">Select Talent</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Choose a talent to go live</div>
                    </div>
                </div>
                <div style="display: flex; align-items: start; gap: 0.75rem;">
                    <div style="background: hsl(var(--primary)); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0;">3</div>
                    <div>
                        <div style="font-weight: 500;">Go Live</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Change status to "Live" and the stream will appear here</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; padding: 1.5rem 0; color: hsl(var(--muted-foreground));'>
    <p style="font-size: 0.875rem;">
        {f"Monitoring {len(livestreams)} active stream(s)" if livestreams else "Ready to start monitoring"}
    </p>
    <p style="font-size: 0.75rem; margin-top: 0.25rem;">Real-time monitoring • Live updates • Engagement tracking</p>
</div>
""", unsafe_allow_html=True)
