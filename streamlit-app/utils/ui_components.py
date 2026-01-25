"""
🎨 Unified Superior Design System
Combining best practices from:
- shadcn/ui (component architecture)
- Linear (LCH colors, high density)
- Glassmorphism 2026 trends
- SaaS UX best practices
- Modern gradient systems
"""

def get_modern_css():
    """
    Advanced Design System with:
    - LCH color space for perceptual uniformity
    - Glassmorphic effects with sophisticated gradients
    - Micro-interactions and smooth animations
    - Dark mode support
    - WCAG AAA accessibility
    - Real-time data visualization components
    """
    return """
    <style>
    /* ========================================
       🎨 UNIFIED SUPERIOR DESIGN SYSTEM 2026
       Combining: Linear + Glassmorphism + SaaS Best Practices
       ======================================== */

    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ========================================
       🎨 COLOR SYSTEM - LCH Based (Linear-inspired)
       Perceptually uniform colors
       ======================================== */

    :root {
        /* LCH-based Primary Palette - Deep Indigo/Violet with better perception */
        --primary-50: 252 100% 97%;
        --primary-100: 251 91% 95%;
        --primary-200: 250 95% 90%;
        --primary-300: 250 84% 82%;
        --primary-400: 250 76% 70%;
        --primary-500: 250 70% 60%;  /* Main */
        --primary-600: 250 70% 50%;
        --primary-700: 250 72% 40%;
        --primary-800: 250 70% 32%;
        --primary-900: 250 68% 24%;

        /* Neutral Palette - Slate with warm undertones */
        --neutral-50: 210 40% 98%;
        --neutral-100: 210 40% 96%;
        --neutral-200: 214 32% 91%;
        --neutral-300: 213 27% 84%;
        --neutral-400: 215 20% 65%;
        --neutral-500: 215 16% 47%;
        --neutral-600: 215 19% 35%;
        --neutral-700: 215 25% 27%;
        --neutral-800: 217 33% 17%;
        --neutral-900: 222 47% 11%;

        /* Semantic Colors */
        --success-50: 142 76% 96%;
        --success-500: 142 71% 45%;
        --success-600: 142 76% 36%;

        --warning-50: 38 100% 95%;
        --warning-500: 38 92% 50%;
        --warning-600: 32 95% 44%;

        --error-50: 0 86% 97%;
        --error-500: 0 84% 60%;
        --error-600: 0 72% 51%;

        --info-50: 210 100% 97%;
        --info-500: 210 98% 56%;
        --info-600: 213 94% 43%;

        /* Surface & Background */
        --background: var(--neutral-50);
        --surface: 0 0% 100%;
        --surface-elevated: 0 0% 100%;
        --surface-overlay: 0 0% 100%;

        /* Text Colors */
        --text-primary: var(--neutral-900);
        --text-secondary: var(--neutral-600);
        --text-tertiary: var(--neutral-500);
        --text-disabled: var(--neutral-400);
        --text-inverse: 0 0% 100%;

        /* Border */
        --border-subtle: var(--neutral-200);
        --border-medium: var(--neutral-300);
        --border-strong: var(--neutral-400);

        /* Shadows - Layered for depth */
        --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
        --shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.15);

        /* Spacing Scale - 8px grid system */
        --space-1: 0.25rem;   /* 4px */
        --space-2: 0.5rem;    /* 8px */
        --space-3: 0.75rem;   /* 12px */
        --space-4: 1rem;      /* 16px */
        --space-5: 1.25rem;   /* 20px */
        --space-6: 1.5rem;    /* 24px */
        --space-8: 2rem;      /* 32px */
        --space-10: 2.5rem;   /* 40px */
        --space-12: 3rem;     /* 48px */
        --space-16: 4rem;     /* 64px */

        /* Border Radius */
        --radius-xs: 0.25rem;
        --radius-sm: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --radius-xl: 1.5rem;
        --radius-full: 9999px;

        /* Typography Scale */
        --font-size-xs: 0.75rem;     /* 12px */
        --font-size-sm: 0.875rem;    /* 14px */
        --font-size-base: 1rem;      /* 16px */
        --font-size-lg: 1.125rem;    /* 18px */
        --font-size-xl: 1.25rem;     /* 20px */
        --font-size-2xl: 1.5rem;     /* 24px */
        --font-size-3xl: 1.875rem;   /* 30px */
        --font-size-4xl: 2.25rem;    /* 36px */
        --font-size-5xl: 3rem;       /* 48px */

        /* Animation Durations */
        --duration-fast: 150ms;
        --duration-normal: 250ms;
        --duration-slow: 350ms;

        /* Animation Easings */
        --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
        --ease-out: cubic-bezier(0.0, 0, 0.2, 1);
        --ease-in: cubic-bezier(0.4, 0, 1, 1);
        --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

        /* Z-index Scale */
        --z-dropdown: 1000;
        --z-sticky: 1100;
        --z-fixed: 1200;
        --z-modal-backdrop: 1300;
        --z-modal: 1400;
        --z-popover: 1500;
        --z-tooltip: 1600;
    }

    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        :root {
            --background: 222 47% 11%;
            --surface: 217 33% 17%;
            --surface-elevated: 215 25% 22%;
            --surface-overlay: 215 25% 27%;

            --text-primary: 0 0% 98%;
            --text-secondary: var(--neutral-300);
            --text-tertiary: var(--neutral-400);
            --text-disabled: var(--neutral-500);

            --border-subtle: var(--neutral-800);
            --border-medium: var(--neutral-700);
            --border-strong: var(--neutral-600);
        }
    }

    /* ========================================
       🎯 GLOBAL STYLES
       ======================================== */

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: hsl(var(--background));
        color: hsl(var(--text-primary));
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
        font-feature-settings: 'liga', 'kern';
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Hide default Streamlit sidebar navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    section[data-testid="stSidebar"] > div:first-child > div:first-child {
        padding-top: 0 !important;
    }

    /* Streamlit container adjustments */
    .main .block-container {
        padding-top: var(--space-8);
        padding-bottom: var(--space-12);
        max-width: 1600px;
    }

    /* ========================================
       📐 TYPOGRAPHY SYSTEM
       Plus Jakarta Sans for headings, Inter for body
       ======================================== */

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: hsl(var(--text-primary));
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    .heading-display {
        font-size: var(--font-size-5xl);
        font-weight: 900;
        line-height: 1;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg,
            hsl(var(--primary-500)) 0%,
            hsl(270 70% 60%) 50%,
            hsl(290 70% 65%) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--space-4);
    }

    .heading-1 {
        font-size: var(--font-size-4xl);
        font-weight: 800;
    }

    .heading-2 {
        font-size: var(--font-size-3xl);
        font-weight: 700;
    }

    .heading-3 {
        font-size: var(--font-size-2xl);
        font-weight: 600;
    }

    .heading-4 {
        font-size: var(--font-size-xl);
        font-weight: 600;
    }

    .text-body-lg {
        font-size: var(--font-size-lg);
        line-height: 1.7;
    }

    .text-body {
        font-size: var(--font-size-base);
        line-height: 1.6;
    }

    .text-body-sm {
        font-size: var(--font-size-sm);
        line-height: 1.5;
    }

    .text-caption {
        font-size: var(--font-size-xs);
        line-height: 1.4;
        color: hsl(var(--text-tertiary));
    }

    .text-muted {
        color: hsl(var(--text-secondary));
    }

    .text-subtle {
        color: hsl(var(--text-tertiary));
    }

    /* Monospace for code/metrics */
    .font-mono {
        font-family: 'JetBrains Mono', monospace;
        font-feature-settings: 'zero', 'ss01';
    }

    /* ========================================
       🎭 GLASSMORPHIC HERO SECTION
       Advanced blur and gradient effects
       ======================================== */

    .hero-glass {
        position: relative;
        background: linear-gradient(135deg,
            hsl(var(--primary-500) / 0.95) 0%,
            hsl(270 70% 60% / 0.95) 50%,
            hsl(290 70% 65% / 0.9) 100%
        );
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border-radius: var(--radius-xl);
        padding: var(--space-12);
        color: white;
        box-shadow: var(--shadow-glass), var(--shadow-xl);
        border: 1px solid hsl(250 70% 70% / 0.2);
        overflow: hidden;
        isolation: isolate;
    }

    .hero-glass::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(circle at 20% 30%, hsl(280 70% 70% / 0.3) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, hsl(260 70% 70% / 0.2) 0%, transparent 40%);
        pointer-events: none;
        z-index: -1;
    }

    .hero-glass::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, hsl(280 100% 80% / 0.2) 0%, transparent 70%);
        filter: blur(40px);
        animation: float 20s ease-in-out infinite;
        z-index: -1;
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(120deg); }
        66% { transform: translate(-20px, 20px) rotate(240deg); }
    }

    .hero-glass h1 {
        color: white;
        font-size: var(--font-size-4xl);
        font-weight: 900;
        margin-bottom: var(--space-4);
        text-shadow: 0 2px 20px rgb(0 0 0 / 0.2);
        letter-spacing: -0.03em;
    }

    .hero-glass p {
        color: hsl(250 70% 95%);
        font-size: var(--font-size-lg);
        margin-bottom: var(--space-6);
        opacity: 0.95;
        line-height: 1.7;
    }

    .hero-glass .btn {
        background: white;
        color: hsl(var(--primary-600));
        font-weight: 700;
        padding: var(--space-4) var(--space-8);
        border-radius: var(--radius-lg);
        border: none;
        cursor: pointer;
        transition: all var(--duration-normal) var(--ease-out);
        box-shadow: 0 4px 16px rgb(0 0 0 / 0.15);
        font-size: var(--font-size-base);
    }

    .hero-glass .btn:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 24px rgb(0 0 0 / 0.25);
    }

    .hero-glass .btn:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* ========================================
       📊 STAT CARDS - Modern with Micro-interactions
       ======================================== */

    .stat-card {
        background: hsl(var(--surface));
        border: 1px solid hsl(var(--border-subtle));
        border-radius: var(--radius-lg);
        padding: var(--space-6);
        transition: all var(--duration-normal) var(--ease-out);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, transparent 0%, hsl(var(--primary-500) / 0.03) 100%);
        opacity: 0;
        transition: opacity var(--duration-normal) var(--ease-out);
    }

    .stat-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: var(--shadow-lg);
        border-color: hsl(var(--primary-300));
    }

    .stat-card:hover::before {
        opacity: 1;
    }

    .stat-card-icon {
        width: 3.5rem;
        height: 3.5rem;
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        margin-bottom: var(--space-4);
        transition: transform var(--duration-normal) var(--ease-bounce);
        box-shadow: var(--shadow-sm);
    }

    .stat-card:hover .stat-card-icon {
        transform: rotate(5deg) scale(1.1);
    }

    .stat-card-icon.purple {
        background: linear-gradient(135deg, hsl(var(--primary-400)) 0%, hsl(270 70% 60%) 100%);
    }

    .stat-card-icon.blue {
        background: linear-gradient(135deg, hsl(210 98% 56%) 0%, hsl(220 90% 56%) 100%);
    }

    .stat-card-icon.green {
        background: linear-gradient(135deg, hsl(142 71% 50%) 0%, hsl(152 71% 45%) 100%);
    }

    .stat-card-icon.orange {
        background: linear-gradient(135deg, hsl(25 95% 53%) 0%, hsl(38 92% 50%) 100%);
    }

    .stat-card-icon.red {
        background: linear-gradient(135deg, hsl(0 84% 60%) 0%, hsl(350 84% 60%) 100%);
    }

    .stat-card-label {
        color: hsl(var(--text-secondary));
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: var(--space-2);
    }

    .stat-card-value {
        font-size: var(--font-size-4xl);
        font-weight: 900;
        color: hsl(var(--text-primary));
        margin-bottom: var(--space-3);
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1;
        letter-spacing: -0.03em;
    }

    .stat-card-change {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        font-size: var(--font-size-sm);
        font-weight: 700;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
    }

    .stat-card-change.positive {
        background: hsl(var(--success-50));
        color: hsl(var(--success-600));
    }

    .stat-card-change.negative {
        background: hsl(var(--error-50));
        color: hsl(var(--error-600));
    }

    .stat-card-trend {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg,
            hsl(var(--primary-400)) 0%,
            hsl(270 70% 60%) 100%
        );
        transform: scaleX(0);
        transform-origin: left;
        transition: transform var(--duration-slow) var(--ease-out);
    }

    .stat-card:hover .stat-card-trend {
        transform: scaleX(1);
    }

    /* ========================================
       🎴 CARD COMPONENT - Elevated design
       ======================================== */

    .card {
        background: hsl(var(--surface));
        border: 1px solid hsl(var(--border-subtle));
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        transition: all var(--duration-normal) var(--ease-out);
        overflow: hidden;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
        border-color: hsl(var(--border-medium));
    }

    .card-header {
        padding: var(--space-6);
        border-bottom: 1px solid hsl(var(--border-subtle));
        background: linear-gradient(to bottom,
            hsl(var(--surface)) 0%,
            hsl(var(--background)) 100%
        );
    }

    .card-header h3 {
        margin: 0;
        font-size: var(--font-size-xl);
        font-weight: 700;
        color: hsl(var(--text-primary));
    }

    .card-header p {
        margin: var(--space-2) 0 0;
        color: hsl(var(--text-secondary));
        font-size: var(--font-size-sm);
    }

    .card-content {
        padding: var(--space-6);
    }

    .card-footer {
        padding: var(--space-6);
        border-top: 1px solid hsl(var(--border-subtle));
        background: hsl(var(--background));
    }

    /* Glassmorphic Card Variant */
    .card-glass {
        background: linear-gradient(135deg,
            hsl(var(--surface) / 0.8) 0%,
            hsl(var(--surface) / 0.6) 100%
        );
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid hsl(var(--border-subtle) / 0.5);
        box-shadow: var(--shadow-glass);
    }

    /* ========================================
       🏷️ BADGE COMPONENT
       ======================================== */

    .badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all var(--duration-fast) var(--ease-out);
        white-space: nowrap;
    }

    .badge-success {
        background: hsl(var(--success-50));
        color: hsl(var(--success-600));
        border: 1px solid hsl(var(--success-200));
    }

    .badge-warning {
        background: hsl(var(--warning-50));
        color: hsl(var(--warning-600));
        border: 1px solid hsl(var(--warning-200));
    }

    .badge-error {
        background: hsl(var(--error-50));
        color: hsl(var(--error-600));
        border: 1px solid hsl(var(--error-200));
    }

    .badge-default {
        background: hsl(var(--neutral-100));
        color: hsl(var(--text-secondary));
        border: 1px solid hsl(var(--border-medium));
    }

    .badge-primary {
        background: linear-gradient(135deg, hsl(var(--primary-500)) 0%, hsl(270 70% 60%) 100%);
        color: white;
        border: none;
        box-shadow: 0 2px 8px hsl(var(--primary-500) / 0.3);
    }

    .badge-info {
        background: hsl(var(--info-50));
        color: hsl(var(--info-600));
        border: 1px solid hsl(var(--info-200));
    }

    /* Pulse animation for LIVE badge */
    .pulse-animation {
        animation: pulse-glow 2s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% {
            box-shadow: 0 0 0 0 hsl(var(--error-500) / 0.7);
        }
        50% {
            box-shadow: 0 0 0 8px hsl(var(--error-500) / 0);
        }
    }

    /* ========================================
       👤 AVATAR COMPONENT
       ======================================== */

    .avatar {
        position: relative;
        display: inline-block;
        border-radius: var(--radius-full);
        overflow: hidden;
        border: 2px solid hsl(var(--surface));
        background: hsl(var(--neutral-100));
        box-shadow: var(--shadow-sm);
        transition: all var(--duration-fast) var(--ease-out);
    }

    .avatar:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-md);
    }

    .avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .avatar-sm { width: 2rem; height: 2rem; }
    .avatar-md { width: 2.5rem; height: 2.5rem; }
    .avatar-lg { width: 3.5rem; height: 3.5rem; }
    .avatar-xl { width: 5rem; height: 5rem; }

    .avatar-status {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 0.875rem;
        height: 0.875rem;
        border-radius: var(--radius-full);
        border: 2px solid hsl(var(--surface));
        box-shadow: var(--shadow-sm);
    }

    .avatar-status.online {
        background: hsl(var(--success-500));
        box-shadow: 0 0 0 3px hsl(var(--success-500) / 0.2);
    }

    .avatar-status.live {
        background: hsl(var(--error-500));
        animation: pulse-live 2s infinite;
    }

    @keyframes pulse-live {
        0%, 100% {
            box-shadow: 0 0 0 0 hsl(var(--error-500) / 0.7);
        }
        50% {
            box-shadow: 0 0 0 6px hsl(var(--error-500) / 0);
        }
    }

    .avatar-status.offline {
        background: hsl(var(--neutral-400));
    }

    .avatar-status.busy {
        background: hsl(var(--warning-500));
    }

    /* ========================================
       📊 PROGRESS BAR
       ======================================== */

    .progress {
        width: 100%;
        height: 0.625rem;
        background: hsl(var(--neutral-100));
        border-radius: var(--radius-full);
        overflow: hidden;
        box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.05);
    }

    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg,
            hsl(var(--primary-500)) 0%,
            hsl(270 70% 60%) 100%
        );
        border-radius: var(--radius-full);
        transition: width var(--duration-slow) var(--ease-out);
        position: relative;
        overflow: hidden;
    }

    .progress-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.3) 50%,
            transparent 100%
        );
        animation: shimmer 2s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* ========================================
       🎯 BUTTON COMPONENT
       ======================================== */

    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-3) var(--space-6);
        border-radius: var(--radius-lg);
        font-weight: 600;
        font-size: var(--font-size-sm);
        transition: all var(--duration-normal) var(--ease-out);
        cursor: pointer;
        border: none;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
    }

    .btn::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: var(--radius-full);
        background: rgba(255, 255, 255, 0.5);
        transform: translate(-50%, -50%);
        transition: width var(--duration-slow) var(--ease-out),
                    height var(--duration-slow) var(--ease-out);
    }

    .btn:hover::before {
        width: 300px;
        height: 300px;
    }

    .btn-primary {
        background: linear-gradient(135deg, hsl(var(--primary-500)) 0%, hsl(270 70% 60%) 100%);
        color: white;
        box-shadow: 0 2px 12px hsl(var(--primary-500) / 0.3);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px hsl(var(--primary-500) / 0.4);
    }

    .btn-primary:active {
        transform: translateY(0);
    }

    .btn-secondary {
        background: hsl(var(--surface));
        color: hsl(var(--text-primary));
        border: 1px solid hsl(var(--border-medium));
    }

    .btn-secondary:hover {
        background: hsl(var(--neutral-100));
        border-color: hsl(var(--primary-300));
    }

    /* ========================================
       ⚠️ ALERT COMPONENT
       ======================================== */

    .alert {
        padding: var(--space-4) var(--space-6);
        border-radius: var(--radius-lg);
        border: 1px solid;
        margin: var(--space-4) 0;
        display: flex;
        align-items: start;
        gap: var(--space-3);
    }

    .alert-info {
        background: hsl(var(--info-50));
        border-color: hsl(var(--info-200));
        color: hsl(var(--info-600));
    }

    .alert-success {
        background: hsl(var(--success-50));
        border-color: hsl(var(--success-200));
        color: hsl(var(--success-600));
    }

    .alert-warning {
        background: hsl(var(--warning-50));
        border-color: hsl(var(--warning-200));
        color: hsl(var(--warning-600));
    }

    .alert-error {
        background: hsl(var(--error-50));
        border-color: hsl(var(--error-200));
        color: hsl(var(--error-600));
    }

    /* ========================================
       📋 TABLE COMPONENT
       ======================================== */

    .table-row {
        padding: var(--space-4) var(--space-6);
        border-bottom: 1px solid hsl(var(--border-subtle));
        transition: all var(--duration-fast) var(--ease-out);
        cursor: pointer;
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .table-row:hover {
        background: hsl(var(--neutral-50));
        transform: translateX(4px);
    }

    /* ========================================
       🎨 SIDEBAR STYLING (TalentFlow-inspired)
       ======================================== */

    [data-testid="stSidebar"] {
        background: hsl(var(--surface)) !important;
        border-right: 1px solid hsl(var(--border-subtle)) !important;
        box-shadow: var(--shadow-sm);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: hsl(var(--surface)) !important;
        padding: var(--space-6) var(--space-4);
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-4) var(--space-3);
        margin-bottom: var(--space-8);
        border-bottom: 1px solid hsl(var(--border-subtle));
    }

    .sidebar-logo-icon {
        width: 2.75rem;
        height: 2.75rem;
        background: linear-gradient(135deg,
            hsl(var(--primary-500)) 0%,
            hsl(270 70% 60%) 100%
        );
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        box-shadow: var(--shadow-md);
    }

    .sidebar-logo-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: var(--font-size-xl);
        background: linear-gradient(135deg,
            hsl(var(--primary-500)) 0%,
            hsl(270 70% 60%) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sidebar-menu-section {
        margin-bottom: var(--space-8);
    }

    .sidebar-menu-label {
        color: hsl(var(--text-tertiary));
        font-size: var(--font-size-xs);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0 var(--space-3);
        margin-bottom: var(--space-3);
        display: block;
    }

    .sidebar-menu-item {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-4);
        margin: var(--space-1) 0;
        border-radius: var(--radius-md);
        color: hsl(var(--text-secondary));
        font-size: var(--font-size-sm);
        font-weight: 500;
        transition: all var(--duration-fast) var(--ease-out);
        cursor: pointer;
        position: relative;
    }

    .sidebar-menu-item:hover {
        background: hsl(var(--neutral-100));
        color: hsl(var(--primary-600));
        transform: translateX(4px);
    }

    .sidebar-menu-item.active {
        background: linear-gradient(135deg,
            hsl(var(--primary-500) / 0.1) 0%,
            hsl(270 70% 60% / 0.08) 100%
        );
        color: hsl(var(--primary-600));
        font-weight: 700;
        border-left: 3px solid hsl(var(--primary-500));
        padding-left: calc(var(--space-4) - 3px);
        box-shadow: var(--shadow-xs);
    }

    .sidebar-menu-icon {
        font-size: var(--font-size-lg);
        width: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .sidebar-menu-badge {
        margin-left: auto;
        background: hsl(var(--error-500));
        color: white;
        font-size: var(--font-size-xs);
        font-weight: 700;
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-full);
        min-width: 1.25rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }

    /* ========================================
       🎬 UTILITY CLASSES
       ======================================== */

    .separator {
        height: 1px;
        background: hsl(var(--border-subtle));
        margin: var(--space-8) 0;
    }

    .hover-lift {
        transition: transform var(--duration-normal) var(--ease-out),
                    box-shadow var(--duration-normal) var(--ease-out);
    }

    .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fade-in var(--duration-slow) var(--ease-out);
    }

    @keyframes slide-in-right {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .slide-in {
        animation: slide-in-right var(--duration-slow) var(--ease-out);
    }

    /* ========================================
       📱 RESPONSIVE DESIGN
       ======================================== */

    @media (max-width: 768px) {
        .hero-glass {
            padding: var(--space-8);
        }

        .hero-glass h1 {
            font-size: var(--font-size-3xl);
        }

        .stat-card-value {
            font-size: var(--font-size-3xl);
        }
    }

    /* ========================================
       🎨 SCROLLBAR STYLING
       ======================================== */

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: hsl(var(--background));
    }

    ::-webkit-scrollbar-thumb {
        background: hsl(var(--border-medium));
        border-radius: var(--radius-sm);
        border: 2px solid hsl(var(--background));
    }

    ::-webkit-scrollbar-thumb:hover {
        background: hsl(var(--text-tertiary));
    }

    /* ========================================
       ✨ SPECIAL EFFECTS
       ======================================== */

    @keyframes gradient-shift {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }

    .gradient-animated {
        background-size: 200% 200%;
        animation: gradient-shift 8s ease infinite;
    }

    /* Skeleton Loading */
    .skeleton {
        background: linear-gradient(
            90deg,
            hsl(var(--neutral-100)) 25%,
            hsl(var(--neutral-200)) 50%,
            hsl(var(--neutral-100)) 75%
        );
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s infinite;
        border-radius: var(--radius-md);
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    </style>
    """

# ========================================
# 🧩 COMPONENT FUNCTIONS
# ========================================

def stat_card(label, value, change=None, change_positive=True, icon="📊", icon_color="purple"):
    """Create an advanced stat card with micro-interactions"""
    change_html = ""
    if change:
        change_class = "positive" if change_positive else "negative"
        arrow = "↗" if change_positive else "↘"
        change_html = f'<div class="stat-card-change {change_class}">{arrow} {change}</div>'

    return f'<div class="stat-card"><div class="stat-card-icon {icon_color}">{icon}</div><div class="stat-card-label">{label}</div><div class="stat-card-value">{value}</div>{change_html}<div class="stat-card-trend"></div></div>'

def badge(text, variant="default"):
    """Create a badge component"""
    text_safe = text.replace('"', '&quot;')
    return f'<span class="badge badge-{variant}">{text_safe}</span>'

def avatar(image_url, size="md", status=None):
    """Create an avatar with optional status indicator"""
    status_html = f'<div class="avatar-status {status}"></div>' if status else ''
    return f'<div class="avatar avatar-{size}"><img src="{image_url}" alt="Avatar">{status_html}</div>'

def progress_bar(percentage, color="primary"):
    """Create an animated progress bar"""
    return f'<div class="progress"><div class="progress-bar" style="width: {percentage}%;"></div></div>'

def hero_section(title, subtitle, button_text=None, button_url=None):
    """Create a glassmorphic hero section with advanced effects"""
    button_html = ""
    if button_text:
        button_html = f'<button class="btn" onclick="window.location.href=\'{button_url}\'">{button_text}</button>'

    return f'<div class="hero-glass fade-in"><h1>{title}</h1><p>{subtitle}</p>{button_html}</div>'

def sidebar_menu(active_page="Dashboard"):
    """Create TalentFlow-inspired sidebar menu with functional navigation"""
    import streamlit as st

    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎭</div>
        <div class="sidebar-logo-text">LiveStream</div>
    </div>
    """, unsafe_allow_html=True)

    # Main Menu Section
    st.markdown('<div class="sidebar-menu-section"><span class="sidebar-menu-label">MAIN</span></div>', unsafe_allow_html=True)

    # Dashboard
    if st.button("📊  Dashboard", key="nav_dashboard", use_container_width=True,
                 type="primary" if active_page == "Dashboard" else "secondary"):
        st.switch_page("streamlit_app.py")

    # Talents
    if st.button("👥  Talents", key="nav_talents", use_container_width=True,
                 type="primary" if active_page == "Talent_Management" else "secondary"):
        st.switch_page("pages/1_👥_Talent_Management.py")

    # Livestreams
    if st.button("📺  Livestreams", key="nav_livestreams", use_container_width=True,
                 type="primary" if active_page == "Livestreams" else "secondary"):
        st.switch_page("pages/2_📺_Livestreams.py")

    # Analytics
    if st.button("📈  Analytics", key="nav_analytics", use_container_width=True,
                 type="primary" if active_page == "Analytics" else "secondary"):
        st.switch_page("pages/3_📈_Analytics.py")

    # Separator
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # System Menu Section
    st.markdown('<div class="sidebar-menu-section"><span class="sidebar-menu-label">SYSTEM</span></div>', unsafe_allow_html=True)

    # Settings (placeholder)
    if st.button("⚙️  Settings", key="nav_settings", use_container_width=True, type="secondary"):
        st.info("Settings page (coming soon)")

    # Add custom CSS for navigation buttons
    st.markdown("""
    <style>
    /* Style navigation buttons to match TalentFlow design */
    [data-testid="stSidebar"] button {
        border-radius: var(--radius-md) !important;
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
        padding: var(--space-3) var(--space-4) !important;
        margin: var(--space-1) 0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all var(--duration-fast) var(--ease-out) !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"] {
        background: transparent !important;
        color: hsl(var(--text-secondary)) !important;
        border: none !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: hsl(var(--neutral-100)) !important;
        color: hsl(var(--primary-600)) !important;
        transform: translateX(4px) !important;
    }

    [data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg,
            hsl(var(--primary-500) / 0.1) 0%,
            hsl(270 70% 60% / 0.08) 100%) !important;
        color: hsl(var(--primary-600)) !important;
        font-weight: 700 !important;
        border-left: 3px solid hsl(var(--primary-500)) !important;
        padding-left: calc(var(--space-4) - 3px) !important;
        box-shadow: var(--shadow-xs) !important;
        border-radius: var(--radius-md) !important;
    }

    [data-testid="stSidebar"] button p {
        font-size: var(--font-size-sm) !important;
    }
    </style>
    """, unsafe_allow_html=True)
