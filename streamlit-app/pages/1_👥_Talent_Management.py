"""
👥 Talent Management Page
Modern TalentFlow-inspired design
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
from utils.ui_components import get_modern_css, badge, avatar, stat_card, progress_bar, sidebar_menu
import pandas as pd

# Page config
st.set_page_config(
    page_title="Talent Management",
    page_icon="👥",
    layout="wide"
)

# Apply modern CSS
st.markdown(get_modern_css(), unsafe_allow_html=True)

# Sidebar Menu (functional navigation)
with st.sidebar:
    sidebar_menu(active_page="Talent_Management")

# Initialize data manager
dm = get_data_manager()

# Header
st.markdown("""
<div style="margin-bottom: 2.5rem;">
    <h1 class="heading-1">👥 Talent Management</h1>
    <p class="text-muted" style="font-size: 1.125rem; margin-top: 0.75rem;">
        Manage all talents, update profiles, and track performance metrics
    </p>
</div>
""", unsafe_allow_html=True)

# Filters and Search
st.markdown("""
<div class="card" style="margin-bottom: 2rem;">
    <div class="card-content" style="padding: 1.25rem;">
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Live", "Online", "Offline"],
        key="status_filter"
    )

with col2:
    search_query = st.text_input("🔍 Search talents", placeholder="Search by name or username...")

with col3:
    sort_by = st.selectbox(
        "Sort by",
        ["Name", "Followers", "Diamonds", "Level", "Total Streams"],
        key="sort_by"
    )

with col4:
    st.markdown("###")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Get talents
talents = dm.get_all_talents()

# Apply filters
if status_filter != "All":
    talents = [t for t in talents if t['status'] == status_filter.lower()]

if search_query:
    talents = [t for t in talents if
               search_query.lower() in t['name'].lower() or
               search_query.lower() in t['username'].lower()]

# Apply sorting
sort_mapping = {
    "Name": "name",
    "Followers": "followers",
    "Diamonds": "total_diamonds",
    "Level": "level",
    "Total Streams": "total_streams"
}
if sort_by in sort_mapping:
    talents = sorted(talents, key=lambda x: x.get(sort_mapping[sort_by], 0), reverse=(sort_by != "Name"))

# Summary Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(stat_card(
        label="Total Talents",
        value=str(len(dm.get_all_talents())),
        icon="👥",
        icon_color="purple"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(stat_card(
        label="Filtered Results",
        value=str(len(talents)),
        icon="🔍",
        icon_color="blue"
    ), unsafe_allow_html=True)

with col3:
    live_count = len([t for t in talents if t['status'] == 'live'])
    st.markdown(stat_card(
        label="Live Now",
        value=str(live_count),
        icon="🔴",
        icon_color="orange"
    ), unsafe_allow_html=True)

with col4:
    online_count = len([t for t in talents if t['status'] in ['online', 'live']])
    st.markdown(stat_card(
        label="Online",
        value=str(online_count),
        icon="🟢",
        icon_color="green"
    ), unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Display Mode Selection
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <div>
        <h2 class="heading-3">Talent Roster</h2>
        <p class="text-muted">Complete list of all registered talents</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Display mode toggle
display_mode = st.radio(
    "Display Mode",
    ["Table View", "Card View"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

if display_mode == "Table View":
    # Professional Table View
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Talent Directory</h3>
            <p class="text-muted">Detailed view of all talent profiles</p>
        </div>
    """, unsafe_allow_html=True)

    for talent in talents:
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

        # Calculate profile completion
        profile_completion = min(100, (talent['level'] * 10) + 30)

        st.markdown(f"""
        <div class="table-row">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="flex: 0 0 60px;">
                    {avatar(talent['avatar'], size='lg', status=talent['status'])}
                </div>
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; font-size: 1rem;">{talent['name']}</span>
                        {badge(f"{status_icon} {talent['status'].upper()}", variant=status_variant)}
                    </div>
                    <div class="text-muted" style="font-size: 0.875rem; margin-bottom: 0.5rem;">@{talent['username']}</div>
                    <div style="display: flex; gap: 2rem; font-size: 0.875rem; color: hsl(var(--foreground-muted));">
                        <span>👥 {talent['followers']:,} followers</span>
                        <span>💎 {talent['total_diamonds']:,} diamonds</span>
                        <span>📊 Level {talent['level']}</span>
                        <span>📺 {talent.get('total_streams', 0)} streams</span>
                    </div>
                </div>
                <div style="flex: 0 0 200px; text-align: right;">
                    <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.5rem;">Profile Completion</div>
                    {progress_bar(profile_completion)}
                    <div style="font-size: 0.75rem; margin-top: 0.25rem; font-weight: 600; color: hsl(var(--primary));">{profile_completion}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Card View
    cols = st.columns(3)

    for idx, talent in enumerate(talents):
        with cols[idx % 3]:
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

            # Calculate profile completion
            profile_completion = min(100, (talent['level'] * 10) + 30)

            st.markdown(f"""
            <div class="card hover-lift" style="cursor: pointer; margin-bottom: 1.5rem;">
                <div style="padding: 1.5rem;">
                    <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                        {avatar(talent['avatar'], size='xl', status=talent['status'])}
                        <div style="margin-top: 1rem; width: 100%;">
                            <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.5rem;">{talent['name']}</div>
                            <div class="text-muted" style="font-size: 0.875rem; margin-bottom: 0.75rem;">@{talent['username']}</div>
                            <div style="margin-bottom: 1rem;">
                                {badge(f"{status_icon} {talent['status'].upper()}", variant=status_variant)}
                            </div>
                        </div>
                    </div>

                    <div class="separator" style="margin: 1.25rem 0;"></div>

                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem;">
                        <div style="text-align: center;">
                            <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Followers</div>
                            <div style="font-weight: 700; font-size: 1.125rem; color: hsl(var(--primary));">{talent['followers']:,}</div>
                        </div>
                        <div style="text-align: center;">
                            <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Diamonds</div>
                            <div style="font-weight: 700; font-size: 1.125rem; color: hsl(var(--primary));">💎 {talent['total_diamonds']:,}</div>
                        </div>
                        <div style="text-align: center;">
                            <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Level</div>
                            <div style="font-weight: 700; font-size: 1.125rem;">Lv. {talent['level']}</div>
                        </div>
                        <div style="text-align: center;">
                            <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Streams</div>
                            <div style="font-weight: 700; font-size: 1.125rem;">{talent.get('total_streams', 0)}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 0.75rem;">
                        <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.5rem;">Profile Completion</div>
                        {progress_bar(profile_completion)}
                        <div style="font-size: 0.75rem; margin-top: 0.25rem; text-align: right; font-weight: 600; color: hsl(var(--primary));">{profile_completion}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Edit Talent Section (Optional)
with st.expander("✏️ Edit Talent Profile", expanded=False):
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3 class="heading-4">Update Talent Information</h3>
            <p class="text-muted">Select a talent to edit their profile details</p>
        </div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    talent_names = [t['name'] for t in dm.get_all_talents()]
    selected_talent_name = st.selectbox("Select Talent", talent_names)

    if selected_talent_name:
        selected_talent = next(t for t in dm.get_all_talents() if t['name'] == selected_talent_name)

        col1, col2 = st.columns(2)

        with col1:
            new_status = st.selectbox(
                "Status",
                ["online", "offline", "live"],
                index=["online", "offline", "live"].index(selected_talent['status'])
            )

        with col2:
            new_level = st.number_input(
                "Level",
                min_value=1,
                max_value=100,
                value=selected_talent['level']
            )

        col3, col4 = st.columns(2)

        with col3:
            new_followers = st.number_input(
                "Followers",
                min_value=0,
                value=selected_talent['followers']
            )

        with col4:
            new_diamonds = st.number_input(
                "Total Diamonds",
                min_value=0,
                value=selected_talent['total_diamonds']
            )

        col_btn1, col_btn2 = st.columns([1, 4])

        with col_btn1:
            if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                dm.update_talent(
                    selected_talent['id'],
                    status=new_status,
                    level=new_level,
                    followers=new_followers,
                    total_diamonds=new_diamonds
                )
                st.success(f"✅ Updated {selected_talent_name}'s profile!")
                st.rerun()

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; color: hsl(var(--foreground-muted));">
    <p style="font-size: 0.875rem;">
        Showing {0} of {1} talents • Last updated just now
    </p>
    <p style="font-size: 0.75rem; margin-top: 0.25rem;">Talent profiles • Performance tracking • Real-time status</p>
</div>
""".format(len(talents), len(dm.get_all_talents())), unsafe_allow_html=True)
