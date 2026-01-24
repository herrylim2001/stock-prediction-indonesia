"""
Shared UI Components & Styles
Modern TalentFlow-inspired Design System
"""

def get_modern_css():
    """Return modern CSS with deep indigo/violet palette"""
    return """
    <style>
    /* ============================
       Modern Professional Design System
       Inspired by TalentFlow
       ============================ */

    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* CSS Variables - Deep Indigo/Violet Palette */
    :root {
        /* Primary Colors - Deep Indigo/Violet */
        --primary: 250 70% 60%;
        --primary-dark: 250 70% 50%;
        --primary-light: 250 70% 70%;

        /* Backgrounds - Soft Slate */
        --background: 210 40% 98%;
        --surface: 0 0% 100%;
        --surface-hover: 210 40% 96%;

        /* Text Colors */
        --foreground: 222 47% 11%;
        --foreground-muted: 215 16% 47%;
        --foreground-light: 215 16% 65%;

        /* Accent Colors */
        --success: 142 71% 45%;
        --success-light: 142 71% 95%;
        --warning: 38 92% 50%;
        --warning-light: 38 92% 95%;
        --error: 0 84% 60%;
        --error-light: 0 84% 95%;

        /* Borders & Dividers */
        --border: 220 13% 91%;
        --border-hover: 250 70% 60%;

        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

        /* Radius */
        --radius: 0.75rem;
        --radius-sm: 0.5rem;
        --radius-lg: 1rem;
    }

    /* Global Resets */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: hsl(var(--background));
        color: hsl(var(--foreground));
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Streamlit container adjustments */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ============================
       TalentFlow Sidebar Styling
       ============================ */

    /* Sidebar Container */
    [data-testid="stSidebar"] {
        background: hsl(var(--surface)) !important;
        border-right: 1px solid hsl(var(--border)) !important;
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: hsl(var(--surface)) !important;
        padding: 1.5rem 1rem;
    }

    /* Sidebar Logo/Branding */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 0.75rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid hsl(var(--border));
    }

    .sidebar-logo-icon {
        width: 2.5rem;
        height: 2.5rem;
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    .sidebar-logo-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Sidebar Menu Items */
    .sidebar-menu {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .sidebar-menu-section {
        margin-bottom: 2rem;
    }

    .sidebar-menu-label {
        color: hsl(var(--foreground-muted));
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0 0.75rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .sidebar-menu-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0.875rem;
        margin: 0.25rem 0;
        border-radius: var(--radius);
        color: hsl(var(--foreground));
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
        text-decoration: none;
        position: relative;
    }

    .sidebar-menu-item:hover {
        background: hsl(var(--surface-hover));
        color: hsl(var(--primary));
        transform: translateX(4px);
    }

    .sidebar-menu-item.active {
        background: linear-gradient(135deg, hsl(var(--primary) / 0.1) 0%, hsl(270 70% 60% / 0.1) 100%);
        color: hsl(var(--primary));
        font-weight: 600;
        border-left: 3px solid hsl(var(--primary));
        padding-left: calc(0.875rem - 3px);
    }

    .sidebar-menu-item.active::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 60%;
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        border-radius: 0 2px 2px 0;
    }

    .sidebar-menu-icon {
        font-size: 1.125rem;
        width: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .sidebar-menu-badge {
        margin-left: auto;
        background: hsl(var(--error));
        color: white;
        font-size: 0.625rem;
        font-weight: 700;
        padding: 0.125rem 0.5rem;
        border-radius: 9999px;
        min-width: 1.25rem;
        text-align: center;
    }

    .sidebar-menu-item.logout {
        color: hsl(var(--error));
    }

    .sidebar-menu-item.logout:hover {
        background: hsl(var(--error-light));
        color: hsl(var(--error));
    }

    /* Sidebar Footer */
    .sidebar-footer {
        padding: 1rem 0.75rem;
        margin-top: auto;
        border-top: 1px solid hsl(var(--border));
        font-size: 0.75rem;
        color: hsl(var(--foreground-muted));
        text-align: center;
    }

    /* ============================
       Typography
       ============================ */

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: hsl(var(--foreground));
    }

    .heading-hero {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(250 70% 50%) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .heading-1 {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.2;
        letter-spacing: -0.02em;
        color: hsl(var(--foreground));
    }

    .heading-2 {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.3;
        letter-spacing: -0.01em;
    }

    .heading-3 {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.4;
    }

    .heading-4 {
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.5;
    }

    .text-muted {
        color: hsl(var(--foreground-muted));
        font-size: 0.875rem;
        line-height: 1.5;
    }

    .text-light {
        color: hsl(var(--foreground-light));
    }

    /* ============================
       Glassmorphic Hero Section
       ============================ */

    .hero-glass {
        background: linear-gradient(135deg,
            hsl(250 70% 60% / 0.95) 0%,
            hsl(270 70% 60% / 0.95) 100%
        );
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: var(--radius-lg);
        padding: 3rem;
        color: white;
        box-shadow: var(--shadow-xl);
        border: 1px solid hsl(250 70% 70% / 0.2);
        position: relative;
        overflow: hidden;
    }

    .hero-glass::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at top right, hsl(280 70% 70% / 0.3) 0%, transparent 50%);
        pointer-events: none;
    }

    .hero-glass h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
        text-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
    }

    .hero-glass p {
        color: hsl(250 70% 95%);
        font-size: 1.125rem;
        margin-bottom: 1.5rem;
        opacity: 0.95;
    }

    .hero-glass .btn {
        background: white;
        color: hsl(var(--primary));
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius);
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgb(0 0 0 / 0.15);
    }

    .hero-glass .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgb(0 0 0 / 0.2);
    }

    /* ============================
       Stats Cards (Modern)
       ============================ */

    .stat-card {
        background: hsl(var(--surface));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: hsl(var(--border-hover));
    }

    .stat-card-icon {
        width: 3rem;
        height: 3rem;
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .stat-card-icon.purple {
        background: linear-gradient(135deg, hsl(250 70% 60%) 0%, hsl(270 70% 60%) 100%);
    }

    .stat-card-icon.blue {
        background: linear-gradient(135deg, hsl(210 70% 60%) 0%, hsl(220 70% 60%) 100%);
    }

    .stat-card-icon.green {
        background: linear-gradient(135deg, hsl(142 71% 50%) 0%, hsl(152 71% 50%) 100%);
    }

    .stat-card-icon.orange {
        background: linear-gradient(135deg, hsl(25 90% 60%) 0%, hsl(35 90% 60%) 100%);
    }

    .stat-card-label {
        color: hsl(var(--foreground-muted));
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .stat-card-value {
        font-size: 2rem;
        font-weight: 800;
        color: hsl(var(--foreground));
        margin-bottom: 0.5rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stat-card-change {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: var(--radius-sm);
    }

    .stat-card-change.positive {
        background: hsl(var(--success-light));
        color: hsl(var(--success));
    }

    .stat-card-change.negative {
        background: hsl(var(--error-light));
        color: hsl(var(--error));
    }

    /* ============================
       Card Component
       ============================ */

    .card {
        background: hsl(var(--surface));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        overflow: hidden;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
    }

    .card-header {
        padding: 1.5rem;
        border-bottom: 1px solid hsl(var(--border));
        background: hsl(var(--surface));
    }

    .card-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: hsl(var(--foreground));
    }

    .card-content {
        padding: 1.5rem;
    }

    .card-footer {
        padding: 1.5rem;
        border-top: 1px solid hsl(var(--border));
        background: hsl(var(--background));
    }

    /* ============================
       Badge Component
       ============================ */

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.2s ease;
    }

    .badge-success {
        background: hsl(var(--success-light));
        color: hsl(var(--success));
        border: 1px solid hsl(var(--success) / 0.2);
    }

    .badge-warning {
        background: hsl(var(--warning-light));
        color: hsl(var(--warning));
        border: 1px solid hsl(var(--warning) / 0.2);
    }

    .badge-error {
        background: hsl(var(--error-light));
        color: hsl(var(--error));
        border: 1px solid hsl(var(--error) / 0.2);
    }

    .badge-default {
        background: hsl(var(--background));
        color: hsl(var(--foreground-muted));
        border: 1px solid hsl(var(--border));
    }

    .badge-primary {
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        color: white;
        border: none;
    }

    /* ============================
       Avatar Component
       ============================ */

    .avatar {
        position: relative;
        display: inline-block;
        border-radius: 9999px;
        overflow: hidden;
        border: 2px solid hsl(var(--border));
        background: hsl(var(--background));
    }

    .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .avatar-sm {
        width: 2rem;
        height: 2rem;
    }

    .avatar-md {
        width: 2.5rem;
        height: 2.5rem;
    }

    .avatar-lg {
        width: 3rem;
        height: 3rem;
    }

    .avatar-xl {
        width: 4rem;
        height: 4rem;
    }

    .avatar-status {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 0.75rem;
        height: 0.75rem;
        border-radius: 9999px;
        border: 2px solid hsl(var(--surface));
    }

    .avatar-status.online {
        background: hsl(var(--success));
        box-shadow: 0 0 0 2px hsl(var(--success) / 0.2);
    }

    .avatar-status.live {
        background: hsl(var(--error));
        box-shadow: 0 0 0 2px hsl(var(--error) / 0.2);
        animation: pulse-live 2s infinite;
    }

    .avatar-status.offline {
        background: hsl(var(--foreground-light));
    }

    @keyframes pulse-live {
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
       Table Component
       ============================ */

    .table-row {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid hsl(var(--border));
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .table-row:hover {
        background: hsl(var(--surface-hover));
        border-radius: var(--radius);
    }

    /* ============================
       Progress Bar
       ============================ */

    .progress {
        width: 100%;
        height: 0.5rem;
        background: hsl(var(--background));
        border-radius: 9999px;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        border-radius: 9999px;
        transition: width 0.3s ease;
    }

    /* ============================
       Button Component
       ============================ */

    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius);
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        cursor: pointer;
        border: none;
        font-family: 'Inter', sans-serif;
    }

    .btn-primary {
        background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(270 70% 60%) 100%);
        color: white;
        box-shadow: 0 2px 8px hsl(var(--primary) / 0.3);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px hsl(var(--primary) / 0.4);
    }

    .btn-secondary {
        background: hsl(var(--surface));
        color: hsl(var(--foreground));
        border: 1px solid hsl(var(--border));
    }

    .btn-secondary:hover {
        background: hsl(var(--surface-hover));
        border-color: hsl(var(--border-hover));
    }

    /* ============================
       Alert Component
       ============================ */

    .alert {
        padding: 1rem 1.5rem;
        border-radius: var(--radius);
        border: 1px solid;
        margin: 1rem 0;
    }

    .alert-info {
        background: hsl(210 70% 96%);
        border-color: hsl(210 70% 80%);
        color: hsl(210 70% 40%);
    }

    .alert-success {
        background: hsl(var(--success-light));
        border-color: hsl(var(--success) / 0.3);
        color: hsl(var(--success));
    }

    .alert-warning {
        background: hsl(var(--warning-light));
        border-color: hsl(var(--warning) / 0.3);
        color: hsl(var(--warning));
    }

    .alert-error {
        background: hsl(var(--error-light));
        border-color: hsl(var(--error) / 0.3);
        color: hsl(var(--error));
    }

    /* ============================
       Separator
       ============================ */

    .separator {
        height: 1px;
        background: hsl(var(--border));
        margin: 2rem 0;
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

    .gap-1 {
        gap: 0.25rem;
    }

    .gap-2 {
        gap: 0.5rem;
    }

    .gap-3 {
        gap: 0.75rem;
    }

    .gap-4 {
        gap: 1rem;
    }

    .mb-1 {
        margin-bottom: 0.25rem;
    }

    .mb-2 {
        margin-bottom: 0.5rem;
    }

    .mb-3 {
        margin-bottom: 0.75rem;
    }

    .mb-4 {
        margin-bottom: 1rem;
    }

    .mt-4 {
        margin-top: 1rem;
    }

    /* ============================
       Hover Effects & Animations
       ============================ */

    .hover-lift {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .hover-lift:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

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

    .fade-in {
        animation: fade-in 0.3s ease;
    }

    /* ============================
       Scrollbar Styling
       ============================ */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: hsl(var(--background));
    }

    ::-webkit-scrollbar-thumb {
        background: hsl(var(--border));
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: hsl(var(--foreground-muted));
    }
    </style>
    """

def stat_card(label, value, change=None, change_positive=True, icon="📊", icon_color="purple"):
    """Create a modern stat card"""
    change_html = ""
    if change:
        change_class = "positive" if change_positive else "negative"
        arrow = "↗" if change_positive else "↘"
        change_html = f'<div class="stat-card-change {change_class}">{arrow} {change}</div>'

    return f'<div class="stat-card hover-lift"><div class="stat-card-icon {icon_color}">{icon}</div><div class="stat-card-label">{label}</div><div class="stat-card-value">{value}</div>{change_html}</div>'

def badge(text, variant="default"):
    """Create a badge"""
    text_safe = text.replace('"', '&quot;')
    return f'<span class="badge badge-{variant}">{text_safe}</span>'

def avatar(image_url, size="md", status=None):
    """Create an avatar with optional status indicator"""
    status_html = f'<div class="avatar-status {status}"></div>' if status else ''
    return f'<div class="avatar avatar-{size}"><img src="{image_url}" alt="Avatar">{status_html}</div>'

def progress_bar(percentage, color="primary"):
    """Create a progress bar"""
    return f'<div class="progress"><div class="progress-bar" style="width: {percentage}%;"></div></div>'

def hero_section(title, subtitle, button_text=None, button_url=None):
    """Create a glassmorphic hero section"""
    button_html = ""
    if button_text:
        button_html = f'<button class="btn" onclick="window.location.href=\'{button_url}\'">{button_text}</button>'

    return f'<div class="hero-glass fade-in"><h1>{title}</h1><p>{subtitle}</p>{button_html}</div>'

def sidebar_menu(active_page="Dashboard"):
    """Create TalentFlow-style sidebar menu"""
    menu_items = {
        "Main": [
            {"label": "Dashboard", "icon": "📊", "page": "Dashboard", "badge": None},
            {"label": "Talents", "icon": "👥", "page": "Talent_Management", "badge": None},
            {"label": "Livestreams", "icon": "📺", "page": "Livestreams", "badge": None},
            {"label": "Analytics", "icon": "📈", "page": "Analytics", "badge": None},
        ],
        "System": [
            {"label": "Settings", "icon": "⚙️", "page": "Settings", "badge": None},
        ]
    }

    html = '<div class="sidebar-logo"><div class="sidebar-logo-icon">🎭</div><div class="sidebar-logo-text">LiveStream</div></div>'

    for section, items in menu_items.items():
        html += f'<div class="sidebar-menu-section"><span class="sidebar-menu-label">{section}</span><div class="sidebar-menu">'

        for item in items:
            active_class = "active" if active_page == item["page"] else ""
            badge_html = f'<span class="sidebar-menu-badge">{item["badge"]}</span>' if item["badge"] else ""

            html += f'<div class="sidebar-menu-item {active_class}"><span class="sidebar-menu-icon">{item["icon"]}</span><span>{item["label"]}</span>{badge_html}</div>'

        html += '</div></div>'

    return html
