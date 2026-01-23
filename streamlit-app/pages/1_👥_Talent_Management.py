"""
👥 Talent Management Page
Manage all talents - view, edit, update status
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.data_manager import get_data_manager
import pandas as pd

# Page config
st.set_page_config(
    page_title="Talent Management",
    page_icon="👥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .talent-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .status-live {
        background: #ff4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-online {
        background: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-offline {
        background: #9E9E9E;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data manager
dm = get_data_manager()

# Header
st.title("👥 Talent Management")
st.markdown("Manage all talents, update profiles, and track performance")
st.markdown("---")

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
    refresh = st.button("🔄 Refresh", use_container_width=True)
    if refresh:
        st.rerun()

st.markdown("---")

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

st.markdown("---")

# Display mode
display_mode = st.radio(
    "Display Mode",
    ["📋 Table View", "🎴 Card View"],
    horizontal=True
)

st.markdown("###")

if display_mode == "📋 Table View":
    # Table View
    if talents:
        # Prepare dataframe
        df_data = []
        for talent in talents:
            df_data.append({
                "Avatar": talent['avatar'],
                "Name": talent['name'],
                "Username": f"@{talent['username']}",
                "Status": talent['status'].upper(),
                "Followers": f"{talent['followers']:,}",
                "Viewers": f"{talent['total_viewers']:,}",
                "Diamonds": f"{talent['total_diamonds']:,}",
                "Level": talent['level'],
                "Streams": talent.get('total_streams', 0),
                "ID": talent['id']
            })

        df = pd.DataFrame(df_data)

        # Display table with colored status
        st.dataframe(
            df[["Name", "Username", "Status", "Followers", "Viewers", "Diamonds", "Level", "Streams"]],
            use_container_width=True,
            hide_index=True,
            height=500
        )

        # Edit section
        st.markdown("---")
        st.subheader("✏️ Edit Talent")

        selected_talent = st.selectbox(
            "Select talent to edit",
            options=[t['name'] for t in talents],
            key="edit_select"
        )

        if selected_talent:
            talent = next(t for t in talents if t['name'] == selected_talent)

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

                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with col2:
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

    else:
        st.info("No talents found matching your criteria.")

else:
    # Card View
    if talents:
        # Display in grid
        cols_per_row = 3
        for i in range(0, len(talents), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(talents):
                    talent = talents[i + j]
                    with col:
                        with st.container():
                            # Status badge
                            status_class = f"status-{talent['status']}"
                            status_html = f'<span class="{status_class}">{talent["status"].upper()}</span>'

                            st.markdown(f"""
                            <div class="talent-card">
                                <div style="text-align: center;">
                                    <img src="{talent['avatar']}" width="80" style="border-radius: 50%; border: 3px solid #667eea;">
                                    <h4 style="margin-top: 0.5rem;">{talent['name']}</h4>
                                    <p style="color: #666; font-size: 0.9rem;">@{talent['username']}</p>
                                    {status_html}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Stats
                            st.markdown(f"**👥 Followers:** {talent['followers']:,}")
                            st.markdown(f"**💎 Diamonds:** {talent['total_diamonds']:,}")
                            st.markdown(f"**📊 Level:** {talent['level']}")
                            st.markdown(f"**📺 Streams:** {talent.get('total_streams', 0)}")

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
        st.info("No talents found matching your criteria.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Showing {len(talents)} of {len(dm.get_all_talents())} talents</p>
</div>
""", unsafe_allow_html=True)
