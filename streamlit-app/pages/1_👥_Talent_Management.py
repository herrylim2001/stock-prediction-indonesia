"""
👥 Talent Management Page
Professional talent management with shadcn/ui design
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
from utils.ui_components import get_shadcn_css, badge, avatar, card
import pandas as pd

# Page config
st.set_page_config(
    page_title="Talent Management",
    page_icon="👥",
    layout="wide"
)

# Apply shadcn CSS
st.markdown(get_shadcn_css(), unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 class="heading-1">👥 Talent Management</h1>
    <p class="text-muted" style="font-size: 1rem; margin-top: 0.5rem;">
        Manage all talents, update profiles, and track performance
    </p>
</div>
""", unsafe_allow_html=True)

# Filters and actions
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

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

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

# Summary stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Talents", len(dm.get_all_talents()))
with col2:
    st.metric("Filtered Results", len(talents))
with col3:
    live_count = len([t for t in talents if t['status'] == 'live'])
    st.metric("Live Now", live_count)
with col4:
    online_count = len([t for t in talents if t['status'] in ['online', 'live']])
    st.metric("Online", online_count)

st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Display mode toggle
display_mode = st.radio(
    "Display Mode",
    ["📋 Table View", "🎴 Card View"],
    horizontal=True
)

st.markdown("###")

if display_mode == "📋 Table View":
    # Professional Table View
    if talents:
        st.markdown("""
        <div class="card" style="padding: 0;">
            <div class="card-header">
                <h3 class="heading-4">All Talents</h3>
                <p class="text-muted">Showing {} of {} talents</p>
            </div>
            <div class="card-content" style="padding: 0;">
        """.format(len(talents), len(dm.get_all_talents())), unsafe_allow_html=True)

        # Table
        for talent in talents:
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
            <div class="table-row" style="display: flex; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid hsl(var(--border));">
                <div style="flex: 0 0 60px;">
                    {avatar(talent['avatar'], size='md', status=talent['status'])}
                </div>
                <div style="flex: 1; margin-left: 1rem;">
                    <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem;">{talent['name']}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.875rem;">@{talent['username']}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.8rem; margin-top: 0.25rem;">{talent['bio']}</div>
                </div>
                <div style="margin: 0 1.5rem; min-width: 100px;">
                    {badge(f"{status_emoji} {talent['status'].upper()}", variant=status_color)}
                </div>
                <div style="text-align: center; min-width: 100px;">
                    <div style="font-weight: 600; color: hsl(var(--foreground));">{talent['followers']:,}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Followers</div>
                </div>
                <div style="text-align: center; min-width: 100px;">
                    <div style="font-weight: 600; color: hsl(var(--foreground));">💎 {talent['total_diamonds']:,}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Diamonds</div>
                </div>
                <div style="text-align: center; min-width: 80px;">
                    <div style="font-weight: 600; color: hsl(var(--foreground));">Lv. {talent['level']}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Level</div>
                </div>
                <div style="text-align: center; min-width: 80px;">
                    <div style="font-weight: 600; color: hsl(var(--foreground));">{talent.get('total_streams', 0)}</div>
                    <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Streams</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Edit Section
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <h3 class="heading-4">✏️ Edit Talent</h3>
                <p class="text-muted">Update talent information</p>
            </div>
            <div class="card-content">
        """, unsafe_allow_html=True)

        selected_talent_name = st.selectbox(
            "Select talent to edit",
            options=[t['name'] for t in talents],
            key="edit_select"
        )

        if selected_talent_name:
            talent = next(t for t in talents if t['name'] == selected_talent_name)

            with st.form("edit_talent_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input("Name", value=talent['name'])
                    new_bio = st.text_area("Bio", value=talent['bio'])
                    new_status = st.selectbox(
                        "Status",
                        ["online", "offline", "live"],
                        index=["online", "offline", "live"].index(talent['status'])
                    )

                with col2:
                    new_followers = st.number_input(
                        "Followers",
                        value=talent['followers'],
                        min_value=0
                    )
                    new_level = st.number_input(
                        "Level",
                        value=talent['level'],
                        min_value=1,
                        max_value=100
                    )

                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    updates = {
                        'name': new_name,
                        'bio': new_bio,
                        'status': new_status,
                        'followers': new_followers,
                        'level': new_level
                    }
                    dm.update_talent(talent['id'], updates)
                    st.success(f"✅ {new_name} updated successfully!")
                    st.rerun()

        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="alert alert-info">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="font-size: 2rem;">🔍</div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">No Talents Found</div>
                    <div style="font-size: 0.875rem;">Try adjusting your filters or search query.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Card View
    if talents:
        # Grid layout
        cols_per_row = 3
        for i in range(0, len(talents), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(talents):
                    talent = talents[i + j]
                    with col:
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
                        <div class="card" style="text-align: center;">
                            <div style="padding: 1.5rem;">
                                {avatar(talent['avatar'], size='xl', status=talent['status'])}
                                <div style="margin-top: 1rem;">
                                    <h4 style="font-weight: 700; margin-bottom: 0.25rem;">{talent['name']}</h4>
                                    <p style="color: hsl(var(--muted-foreground)); font-size: 0.875rem; margin-bottom: 0.75rem;">@{talent['username']}</p>
                                    {badge(f"{status_emoji} {talent['status'].upper()}", variant=status_color)}
                                </div>
                                <div class="separator" style="margin: 1rem 0;"></div>
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: center;">
                                    <div>
                                        <div style="font-weight: 600; font-size: 1.1rem;">{talent['followers']:,}</div>
                                        <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Followers</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; font-size: 1.1rem;">💎 {talent['total_diamonds']:,}</div>
                                        <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Diamonds</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; font-size: 1.1rem;">Lv. {talent['level']}</div>
                                        <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Level</div>
                                    </div>
                                    <div>
                                        <div style="font-weight: 600; font-size: 1.1rem;">{talent.get('total_streams', 0)}</div>
                                        <div style="color: hsl(var(--muted-foreground)); font-size: 0.75rem;">Streams</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Quick actions
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✏️ Edit", key=f"edit_{talent['id']}", use_container_width=True):
                                st.session_state.editing_talent = talent['id']
                        with col_b:
                            new_status = st.selectbox(
                                "Status",
                                ["online", "offline", "live"],
                                index=["online", "offline", "live"].index(talent['status']),
                                key=f"status_{talent['id']}",
                                label_visibility="collapsed"
                            )
                            if new_status != talent['status']:
                                dm.update_talent_status(talent['id'], new_status)
                                st.rerun()

        st.markdown("")
    else:
        st.markdown("""
        <div class="alert alert-info">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="font-size: 2rem;">🔍</div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">No Talents Found</div>
                    <div style="font-size: 0.875rem;">Try adjusting your filters or search query.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; padding: 1.5rem 0; color: hsl(var(--muted-foreground));'>
    <p style="font-size: 0.875rem;">Showing {len(talents)} of {len(dm.get_all_talents())} talents</p>
</div>
""", unsafe_allow_html=True)
