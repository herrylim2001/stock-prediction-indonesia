import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Whitelabel Streaming Platform Design",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better markdown rendering
st.markdown("""
<style>
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    h1 {
        color: #1f2937;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    h2 {
        color: #374151;
        margin-top: 2rem;
    }
    h3 {
        color: #4b5563;
    }
    code {
        background-color: #f3f4f6;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
    }
    pre {
        background-color: #1f2937 !important;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    table {
        width: 100%;
    }
    th {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🎬 Navigation")
st.sidebar.markdown("---")

sections = [
    ("📋 Executive Summary", "executive-summary"),
    ("👥 Role Descriptions", "1-role-descriptions-and-permissions"),
    ("📱 Modules & Pages", "2-main-modules-and-pages"),
    ("🚀 User Journeys", "3-key-user-journeys"),
    ("🗄️ Data Model", "4-data-model"),
    ("📊 Feature Priority", "5-feature-priority-table-v1"),
    ("⚙️ Technical Recommendations", "6-technical-recommendations"),
    ("🖼️ Wireframes", "7-wireframe-sketches"),
    ("📚 Appendix", "8-appendix"),
]

st.sidebar.markdown("### Quick Links")
for name, anchor in sections:
    st.sidebar.markdown(f"- [{name}](#{anchor})")

st.sidebar.markdown("---")
st.sidebar.info("""
**About this Document**

This is a comprehensive design specification for a B2B SaaS whitelabel live streaming platform with:
- 3 user roles
- 4 interfaces
- 48 prioritized features
""")

st.sidebar.markdown("---")
st.sidebar.success("""
**Full Implementation Available!**

This design has been fully implemented with:
- **Backend**: Go + Gin + PostgreSQL
- **Frontend**: Next.js + TypeScript + Tailwind

[View Source Code](https://github.com/herrylim2001/stock-prediction-indonesia)
""")

# Load and display the markdown content
@st.cache_data
def load_markdown():
    md_path = Path(__file__).parent / "WHITELABEL_STREAMING_BACKOFFICE_DESIGN.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")
    return "# Error\nMarkdown file not found."

markdown_content = load_markdown()

# Display the markdown
st.markdown(markdown_content)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        <p>Whitelabel Live Streaming Platform - Product Design Document</p>
        <p>Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
