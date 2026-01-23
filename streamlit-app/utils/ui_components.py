"""
Shared UI Components & Styles
Inspired by shadcn/ui design system
"""

def get_shadcn_css():
    """Return shadcn-inspired CSS for professional UI"""
    return """
    <style>
    /* ============================
       shadcn/ui Inspired Design System
       ============================ */

    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* CSS Variables - Design Tokens */
    :root {
        /* Colors */
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 84% 4.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 222.2 84% 4.9%;
        --primary: 262 83% 58%;
        --primary-foreground: 210 40% 98%;
        --secondary: 210 40% 96.1%;
        --secondary-foreground: 222.2 47.4% 11.2%;
        --muted: 210 40% 96.1%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --accent: 210 40% 96.1%;
        --accent-foreground: 222.2 47.4% 11.2%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 210 40% 98%;
        --border: 214.3 31.8% 91.4%;
        --input: 214.3 31.8% 91.4%;
        --ring: 262 83% 58%;
        --radius: 0.5rem;

        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }

    /* Global Resets */
    * {
        border-color: hsl(var(--border));
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: hsl(var(--background));
        color: hsl(var(--foreground));
        line-height: 1.6;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ============================
       Typography
       ============================ */

    .heading-1 {
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 2.5rem;
        letter-spacing: -0.025em;
        color: hsl(var(--foreground));
    }

    .heading-2 {
        font-size: 1.875rem;
        font-weight: 700;
        line-height: 2.25rem;
        letter-spacing: -0.025em;
        color: hsl(var(--foreground));
    }

    .heading-3 {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 2rem;
        color: hsl(var(--foreground));
    }

    .heading-4 {
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.75rem;
        color: hsl(var(--foreground));
    }

    .text-muted {
        color: hsl(var(--muted-foreground));
        font-size: 0.875rem;
    }

    .text-sm {
        font-size: 0.875rem;
        line-height: 1.25rem;
    }

    .text-xs {
        font-size: 0.75rem;
        line-height: 1rem;
    }

    /* ============================
       Card Component
       ============================ */

    .card {
        background-color: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
        border-color: hsl(var(--primary) / 0.3);
    }

    .card-header {
        padding: 1.5rem;
        border-bottom: 1px solid hsl(var(--border));
    }

    .card-content {
        padding: 1.5rem;
    }

    .card-footer {
        padding: 1.5rem;
        border-top: 1px solid hsl(var(--border));
    }

    /* ============================
       Stat Cards (Metrics)
       ============================ */

    .stat-card {
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--primary) / 0.8) 100%);
        border: 1px solid hsl(var(--primary) / 0.2);
        border-radius: calc(var(--radius) + 2px);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    .stat-card-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .stat-card-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .stat-card-description {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 400;
    }

    .stat-card-icon {
        position: absolute;
        right: 1.5rem;
        top: 1.5rem;
        font-size: 2.5rem;
        opacity: 0.2;
    }

    /* Color variants */
    .stat-card.blue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .stat-card.green {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    .stat-card.purple {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    .stat-card.orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }

    /* ============================
       Badge Component
       ============================ */

    .badge {
        display: inline-flex;
        align-items: center;
        border-radius: calc(var(--radius) - 2px);
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-default {
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
    }

    .badge-secondary {
        background-color: hsl(var(--secondary));
        color: hsl(var(--secondary-foreground));
    }

    .badge-outline {
        border: 1px solid hsl(var(--border));
        background-color: transparent;
        color: hsl(var(--foreground));
    }

    .badge-success {
        background-color: hsl(142 76% 36%);
        color: white;
    }

    .badge-warning {
        background-color: hsl(38 92% 50%);
        color: white;
    }

    .badge-error {
        background-color: hsl(var(--destructive));
        color: hsl(var(--destructive-foreground));
    }

    /* ============================
       Button Component
       ============================ */

    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius);
        font-size: 0.875rem;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid transparent;
        padding: 0.625rem 1.25rem;
        text-decoration: none;
        gap: 0.5rem;
    }

    .btn:hover {
        transform: translateY(-1px);
    }

    .btn-primary {
        background-color: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
        box-shadow: var(--shadow-sm);
    }

    .btn-primary:hover {
        background-color: hsl(var(--primary) / 0.9);
        box-shadow: var(--shadow);
    }

    .btn-secondary {
        background-color: hsl(var(--secondary));
        color: hsl(var(--secondary-foreground));
    }

    .btn-secondary:hover {
        background-color: hsl(var(--secondary) / 0.8);
    }

    .btn-outline {
        border: 1px solid hsl(var(--border));
        background-color: transparent;
        color: hsl(var(--foreground));
    }

    .btn-outline:hover {
        background-color: hsl(var(--accent));
    }

    .btn-ghost {
        background-color: transparent;
        color: hsl(var(--foreground));
    }

    .btn-ghost:hover {
        background-color: hsl(var(--accent));
    }

    /* ============================
       Table Component
       ============================ */

    .table-container {
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        overflow: hidden;
        background-color: hsl(var(--card));
        box-shadow: var(--shadow-sm);
    }

    .table-header {
        background-color: hsl(var(--muted));
        padding: 1rem 1.5rem;
        border-bottom: 1px solid hsl(var(--border));
    }

    .table-row {
        border-bottom: 1px solid hsl(var(--border));
        transition: background-color 0.2s ease;
    }

    .table-row:hover {
        background-color: hsl(var(--muted) / 0.5);
    }

    .table-cell {
        padding: 1rem 1.5rem;
        font-size: 0.875rem;
    }

    /* ============================
       Alert Component
       ============================ */

    .alert {
        border-radius: var(--radius);
        padding: 1rem 1.5rem;
        border: 1px solid hsl(var(--border));
        margin: 1rem 0;
    }

    .alert-info {
        background-color: hsl(221 83% 97%);
        border-color: hsl(221 83% 85%);
        color: hsl(221 83% 30%);
    }

    .alert-success {
        background-color: hsl(142 76% 97%);
        border-color: hsl(142 76% 85%);
        color: hsl(142 76% 25%);
    }

    .alert-warning {
        background-color: hsl(38 92% 97%);
        border-color: hsl(38 92% 85%);
        color: hsl(38 92% 30%);
    }

    .alert-error {
        background-color: hsl(0 84% 97%);
        border-color: hsl(0 84% 85%);
        color: hsl(0 84% 35%);
    }

    /* ============================
       Avatar Component
       ============================ */

    .avatar {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 9999px;
        background-color: hsl(var(--muted));
    }

    .avatar-sm {
        width: 2rem;
        height: 2rem;
    }

    .avatar-md {
        width: 3rem;
        height: 3rem;
    }

    .avatar-lg {
        width: 4rem;
        height: 4rem;
    }

    .avatar-xl {
        width: 6rem;
        height: 6rem;
    }

    .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .avatar-status {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 25%;
        height: 25%;
        border-radius: 9999px;
        border: 2px solid hsl(var(--background));
    }

    .avatar-status.online {
        background-color: hsl(142 76% 36%);
    }

    .avatar-status.offline {
        background-color: hsl(var(--muted-foreground));
    }

    .avatar-status.live {
        background-color: hsl(0 84% 60%);
        animation: pulse-status 2s infinite;
    }

    @keyframes pulse-status {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.7;
            transform: scale(1.1);
        }
    }

    /* ============================
       Separator
       ============================ */

    .separator {
        height: 1px;
        background-color: hsl(var(--border));
        margin: 1.5rem 0;
    }

    /* ============================
       Grid Layouts
       ============================ */

    .grid {
        display: grid;
        gap: 1.5rem;
    }

    .grid-cols-1 {
        grid-template-columns: repeat(1, minmax(0, 1fr));
    }

    .grid-cols-2 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .grid-cols-3 {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .grid-cols-4 {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }

    /* ============================
       Utility Classes
       ============================ */

    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }

    .flex {
        display: flex;
    }

    .flex-col {
        flex-direction: column;
    }

    .items-center {
        align-items: center;
    }

    .justify-between {
        justify-content: space-between;
    }

    .gap-2 {
        gap: 0.5rem;
    }

    .gap-4 {
        gap: 1rem;
    }

    .gap-6 {
        gap: 1.5rem;
    }

    .p-4 {
        padding: 1rem;
    }

    .p-6 {
        padding: 1.5rem;
    }

    .mb-4 {
        margin-bottom: 1rem;
    }

    .mb-6 {
        margin-bottom: 1.5rem;
    }

    .mt-4 {
        margin-top: 1rem;
    }

    .mt-6 {
        margin-top: 1.5rem;
    }

    .rounded {
        border-radius: var(--radius);
    }

    .rounded-lg {
        border-radius: calc(var(--radius) + 4px);
    }

    .shadow {
        box-shadow: var(--shadow);
    }

    .shadow-md {
        box-shadow: var(--shadow-md);
    }

    .shadow-lg {
        box-shadow: var(--shadow-lg);
    }

    /* ============================
       Animations
       ============================ */

    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-fade-in {
        animation: fade-in 0.3s ease-out;
    }

    @keyframes slide-in {
        from {
            transform: translateX(-100%);
        }
        to {
            transform: translateX(0);
        }
    }

    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }

    /* ============================
       Streamlit Overrides
       ============================ */

    .stButton>button {
        background-color: hsl(var(--primary)) !important;
        color: hsl(var(--primary-foreground)) !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton>button:hover {
        background-color: hsl(var(--primary) / 0.9) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow) !important;
    }

    .stSelectbox, .stTextInput, .stTextArea {
        border-radius: var(--radius) !important;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: hsl(var(--muted-foreground)) !important;
    }

    </style>
    """

def stat_card(title, value, description, icon="📊", color="blue"):
    """Create a professional stat card"""
    return f"""
    <div class="stat-card {color}">
        <div class="stat-card-icon">{icon}</div>
        <div class="stat-card-title">{title}</div>
        <div class="stat-card-value">{value}</div>
        <div class="stat-card-description">{description}</div>
    </div>
    """

def card(content, header=None, footer=None):
    """Create a card component"""
    header_html = f'<div class="card-header"><h3 class="heading-4">{header}</h3></div>' if header else ''
    footer_html = f'<div class="card-footer">{footer}</div>' if footer else ''

    return f"""
    <div class="card">
        {header_html}
        <div class="card-content">
            {content}
        </div>
        {footer_html}
    </div>
    """

def badge(text, variant="default"):
    """Create a badge"""
    # Use HTML entity to avoid quote conflicts
    text_safe = text.replace('"', '&quot;')
    return f'<span class="badge badge-{variant}">{text_safe}</span>'

def avatar(image_url, size="md", status=None):
    """Create an avatar with optional status indicator"""
    status_html = f'<div class="avatar-status {status}"></div>' if status else ''
    # Return single-line HTML to avoid quote conflicts in f-strings
    return f'<div class="avatar avatar-{size}"><img src="{image_url}" alt="Avatar">{status_html}</div>'
