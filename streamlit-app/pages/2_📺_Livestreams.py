"""
📺 Livestream Monitoring Page
Monitor all active livestreams, viewer counts, engagement metrics
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Livestream Monitoring",
    page_icon="📺",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .livestream-card {
        border: 2px solid #667eea;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    .live-badge {
        background: #ff4444;
        color: white;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .stat-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .category-tag {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.75rem;
        margin: 0.25rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.title("📺 Livestream Monitoring")
st.markdown("Monitor all active livestreams and engagement metrics")
st.markdown("---")

# Controls
col1, col2, col3 = st.columns([3, 2, 1])

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
    st.markdown("###")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Auto-refresh toggle
auto_refresh = st.checkbox("🔁 Auto-refresh every 10 seconds")
if auto_refresh:
    st.markdown("*Auto-refreshing...*")
    # Note: In production, use st.experimental_rerun() with timer

st.markdown("---")

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
col1, col2, col3, col4 = st.columns(4)

total_viewers = sum(ls['viewers'] for ls in livestreams)
total_likes = sum(ls['likes'] for ls in livestreams)
total_diamonds = sum(ls['diamonds'] for ls in livestreams)
avg_viewers = total_viewers / len(livestreams) if livestreams else 0

with col1:
    st.metric("🔴 Active Livestreams", len(livestreams))
with col2:
    st.metric("👁️ Total Viewers", f"{total_viewers:,}")
with col3:
    st.metric("❤️ Total Likes", f"{total_likes:,}")
with col4:
    st.metric("💎 Total Diamonds", f"{total_diamonds:,}")

st.markdown("---")

# Display livestreams
if livestreams:
    st.subheader(f"📡 Active Livestreams ({len(livestreams)})")

    for ls in livestreams:
        with st.container():
            st.markdown(f"""
            <div class="livestream-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="live-badge">🔴 LIVE</span>
                        <span class="category-tag">{ls.get('category', 'General')}</span>
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">
                        Started: {datetime.fromisoformat(ls['started_at']).strftime('%H:%M')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 3])

            with col1:
                # Thumbnail placeholder
                st.image(ls['thumbnail'], use_container_width=True)

            with col2:
                # Stream info
                st.markdown(f"### {ls['title']}")
                st.markdown(f"**👤 Talent:** {ls['talent_name']} (@{ls['talent_username']})")

                if ls.get('description'):
                    st.markdown(f"*{ls['description']}*")

                # Stats grid
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

                with stat_col1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style="font-size: 1.8rem; font-weight: 700; color: #667eea;">{ls['viewers']}</div>
                        <div style="color: #666; font-size: 0.85rem;">👁️ Viewers</div>
                    </div>
                    """, unsafe_allow_html=True)

                with stat_col2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style="font-size: 1.8rem; font-weight: 700; color: #f093fb;">{ls['likes']}</div>
                        <div style="color: #666; font-size: 0.85rem;">❤️ Likes</div>
                    </div>
                    """, unsafe_allow_html=True)

                with stat_col3:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style="font-size: 1.8rem; font-weight: 700; color: #4facfe;">{ls['diamonds']}</div>
                        <div style="color: #666; font-size: 0.85rem;">💎 Diamonds</div>
                    </div>
                    """, unsafe_allow_html=True)

                with stat_col4:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style="font-size: 1.8rem; font-weight: 700; color: #fa709a;">{ls['comments']}</div>
                        <div style="color: #666; font-size: 0.85rem;">💬 Comments</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Tags
                if ls.get('tags'):
                    st.markdown("**Tags:**")
                    tag_html = " ".join([f'<span class="category-tag">#{tag}</span>' for tag in ls['tags']])
                    st.markdown(tag_html, unsafe_allow_html=True)

                # Actions
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    if st.button("📊 View Details", key=f"details_{ls['id']}", use_container_width=True):
                        st.session_state.selected_stream = ls['id']
                with col_b:
                    if st.button("💬 View Chat", key=f"chat_{ls['id']}", use_container_width=True):
                        st.info("Chat view feature (coming soon)")
                with col_c:
                    if st.button("📈 Analytics", key=f"analytics_{ls['id']}", use_container_width=True):
                        st.info("Stream analytics feature (coming soon)")
                with col_d:
                    if st.button("⛔ End Stream", key=f"end_{ls['id']}", type="secondary", use_container_width=True):
                        if dm.end_livestream(ls['id']):
                            st.success(f"✅ Livestream ended: {ls['title']}")
                            st.rerun()

            st.markdown("---")

    # Overall stats
    st.markdown("### 📊 Session Summary")

    col1, col2 = st.columns(2)

    with col1:
        # Viewer distribution
        st.markdown("**👁️ Viewer Distribution**")
        viewer_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Viewers': [ls['viewers'] for ls in livestreams]
        })
        st.bar_chart(viewer_data.set_index('Talent'))

    with col2:
        # Engagement metrics
        st.markdown("**💎 Revenue (Diamonds)**")
        diamond_data = pd.DataFrame({
            'Talent': [ls['talent_name'] for ls in livestreams],
            'Diamonds': [ls['diamonds'] for ls in livestreams]
        })
        st.bar_chart(diamond_data.set_index('Talent'))

else:
    # No livestreams
    st.info("🎬 No active livestreams at the moment")

    st.markdown("""
    ### 🎥 How to Start a Livestream:

    1. Go to **👥 Talent Management** page
    2. Select a talent
    3. Change status to **"Live"**
    4. Livestream will appear here automatically

    Or use the quick action below:
    """)

    # Quick create livestream
    with st.form("quick_create_stream"):
        st.subheader("⚡ Quick Start Livestream")

        col1, col2 = st.columns(2)

        with col1:
            available_talents = [t for t in dm.get_all_talents() if t['status'] != 'live']
            selected_talent = st.selectbox(
                "Select Talent",
                options=[t['name'] for t in available_talents]
            )

        with col2:
            stream_title = st.text_input(
                "Stream Title",
                value=f"{selected_talent}'s Live Stream" if selected_talent else ""
            )

        stream_desc = st.text_area("Description (optional)")

        if st.form_submit_button("🚀 Start Livestream", use_container_width=True):
            if selected_talent:
                talent = next(t for t in available_talents if t['name'] == selected_talent)
                new_stream = dm.create_livestream(
                    talent['id'],
                    stream_title,
                    stream_desc
                )
                if new_stream:
                    st.success(f"✅ Livestream started: {stream_title}")
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💡 Tip: Use filters and sorting to find specific livestreams quickly</p>
    <p style='font-size: 0.85rem;'>Real-time monitoring • Live updates • Engagement tracking</p>
</div>
""", unsafe_allow_html=True)
