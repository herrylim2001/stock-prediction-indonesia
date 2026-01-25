# Whitelabel Live Streaming Platform - Backoffice System Design

## Executive Summary

This document outlines the complete system design for a B2B SaaS whitelabel live broadcast platform. The platform enables **Providers** (platform owners) to onboard multiple **Clients** (brands/operators) who manage their own **Hosts** (talent) for live streaming sessions with monetization through virtual gifts.

---

## 1. Role Descriptions and Permissions

### 1.1 Whitelabel Provider (Platform Owner / Super Admin)

**Description:** The entity that owns and operates the SaaS platform. They sell the whitelabel solution to multiple clients (brands) and manage the overall platform infrastructure, billing, and revenue share agreements.

| Permission | Access Level |
|------------|--------------|
| Onboard/suspend/delete clients | Full |
| Configure client plans & limits | Full |
| Set revenue share percentages | Full |
| View all platform analytics | Full |
| Manage gift catalog & pricing | Full |
| Access financial reports (all clients) | Full |
| Configure platform-wide settings | Full |
| Manage API keys & integrations | Full |
| View audit logs | Full |
| Customer support escalation | Full |

### 1.2 Client (Brand / Operator)

**Description:** Businesses that license the whitelabel platform to run their own branded live streaming service. They manage their hosts, campaigns, and handle payouts within limits set by the Provider.

| Permission | Access Level |
|------------|--------------|
| Manage own hosts (CRUD) | Full |
| View own analytics & reports | Own data only |
| Configure host payout rates | Within provider limits |
| Approve/process payouts | Own hosts only |
| Create campaigns & events | Own brand only |
| Customize branding (logo, colors) | Own instance |
| Access API for integration | Own scope only |
| View host performance | Own hosts only |
| Manage gift availability | Select from provider catalog |
| Set streaming schedules | Own hosts only |

### 1.3 Host (Talent)

**Description:** Content creators who broadcast live sessions. They interact with viewers, receive virtual gifts, and earn income through the platform.

| Permission | Access Level |
|------------|--------------|
| Start/end live sessions | Own sessions |
| View own performance metrics | Own data only |
| View earnings & payout history | Own data only |
| Request payout | Own balance |
| Update profile information | Own profile |
| View live session analytics | Own sessions |
| Access host web client | Own account |
| View upcoming schedules | Own schedules |

---

## 2. Main Modules and Pages

### 2.1 Provider Backoffice

```
Provider Dashboard
├── Dashboard (Home)
│   ├── Platform overview metrics
│   ├── Active clients count
│   ├── Total live sessions (today/week/month)
│   ├── Platform revenue summary
│   └── Alert notifications
│
├── Client Management
│   ├── Client List (table with search/filter)
│   ├── Client Detail View
│   ├── Add New Client
│   ├── Edit Client
│   ├── Client Plans Configuration
│   └── Client Suspension/Deletion
│
├── Plans & Pricing
│   ├── Plan List (Basic, Pro, Enterprise)
│   ├── Create/Edit Plan
│   ├── Feature Matrix
│   └── Usage Limits Configuration
│
├── Revenue & Finance
│   ├── Revenue Overview
│   ├── Revenue Share Configuration
│   ├── Client Billing History
│   ├── Platform Earnings Report
│   └── Payout Oversight (all clients)
│
├── Gift Catalog
│   ├── Gift List
│   ├── Create/Edit Gift
│   ├── Gift Pricing Tiers
│   └── Gift Analytics
│
├── Analytics
│   ├── Platform-wide Statistics
│   ├── Client Comparison Report
│   ├── Host Leaderboard (global)
│   ├── Gift Performance Report
│   └── Custom Report Builder
│
├── Settings
│   ├── Platform Configuration
│   ├── API Management
│   ├── Webhook Configuration
│   ├── Email Templates
│   └── Audit Logs
│
└── Support
    ├── Support Tickets (escalated)
    └── Knowledge Base Management
```

### 2.2 Client Backoffice

```
Client Dashboard
├── Dashboard (Home)
│   ├── Today's live sessions
│   ├── Active hosts count
│   ├── Revenue summary
│   ├── Top performing hosts
│   └── Pending payouts alert
│
├── Host Management
│   ├── Host List (table with search/filter)
│   ├── Host Detail View
│   ├── Add New Host
│   ├── Edit Host
│   ├── Host Status Management
│   └── Host Performance Review
│
├── Live Sessions
│   ├── Active Sessions Monitor
│   ├── Session History
│   ├── Session Detail View
│   ├── Scheduled Sessions
│   └── Session Analytics
│
├── Campaigns
│   ├── Campaign List
│   ├── Create Campaign
│   ├── Campaign Performance
│   └── Special Events Management
│
├── Finance & Payouts
│   ├── Revenue Dashboard
│   ├── Host Earnings Overview
│   ├── Payout Queue
│   ├── Payout History
│   ├── Payout Rate Configuration
│   └── Financial Reports
│
├── Gifts
│   ├── Available Gifts (from provider catalog)
│   ├── Gift Performance
│   └── Gift Enabling/Disabling
│
├── Branding
│   ├── Logo & Colors
│   ├── Custom Domain Setup
│   └── Widget Customization
│
├── Analytics
│   ├── Performance Overview
│   ├── Host Rankings
│   ├── Viewer Engagement
│   └── Revenue Trends
│
└── Settings
    ├── Account Settings
    ├── Team Members (sub-accounts)
    ├── API Keys
    ├── Notifications
    └── Billing & Subscription
```

### 2.3 Host Portal

```
Host Dashboard
├── Dashboard (Home)
│   ├── Earnings summary (today/week/month)
│   ├── Next scheduled session
│   ├── Recent performance highlights
│   └── Quick actions (Go Live button)
│
├── Go Live
│   └── [Redirects to Host Web Client]
│
├── My Sessions
│   ├── Session History
│   ├── Session Detail View
│   ├── Scheduled Sessions
│   └── Session Recordings (if enabled)
│
├── Earnings
│   ├── Earnings Overview
│   ├── Gift Breakdown
│   ├── Earnings by Session
│   └── Earnings Trend Chart
│
├── Payouts
│   ├── Available Balance
│   ├── Request Payout
│   ├── Payout History
│   └── Payment Method Setup
│
├── Performance
│   ├── Analytics Dashboard
│   ├── Viewer Stats
│   ├── Gift Statistics
│   └── Growth Trends
│
└── Profile
    ├── Edit Profile
    ├── Profile Picture
    ├── Bio & Social Links
    └── Account Settings
```

### 2.4 Host Web Client (Go Live Interface)

```
Host Web Client (Single Page Application)
├── Pre-Live Screen
│   ├── Camera preview
│   ├── Microphone test
│   ├── Session title input
│   ├── Category selection
│   ├── Go Live button
│   └── Settings (quality, flip camera)
│
├── Live Session Screen
│   ├── Video feed (full/partial)
│   ├── Viewer count (real-time)
│   ├── Live duration timer
│   ├── Gift notifications (animated)
│   ├── Chat/comments stream
│   ├── Session earnings counter
│   ├── End Session button
│   └── Quick actions (mute, flip, effects)
│
└── Post-Live Screen
    ├── Session summary
    ├── Total earnings
    ├── Viewer statistics
    ├── Gift breakdown
    ├── Save recording option
    └── Share/promote links
```

---

## 3. Key User Journeys

### 3.1 Onboarding a Client

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLIENT ONBOARDING JOURNEY                            │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Initial Contact & Agreement
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Provider   │───▶│  Contract   │───▶│   Plan      │
│  Sales Call │    │  Signing    │    │  Selection  │
└─────────────┘    └─────────────┘    └─────────────┘

Step 2: Account Creation (Provider Backoffice)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Provider Admin Actions:                                                      │
│ 1. Navigate to Client Management > Add New Client                           │
│ 2. Fill client details (company name, contact email, phone)                 │
│ 3. Select subscription plan (Basic/Pro/Enterprise)                          │
│ 4. Configure limits (max hosts, concurrent streams, storage)                │
│ 5. Set revenue share percentage (e.g., 70% client / 30% provider)           │
│ 6. Enable/disable specific features                                         │
│ 7. Submit → System generates credentials & sends welcome email              │
└─────────────────────────────────────────────────────────────────────────────┘

Step 3: Client First Login
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Welcome    │───▶│  Password   │───▶│   Setup     │───▶│  Dashboard  │
│  Email      │    │  Setup      │    │   Wizard    │    │   Ready     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

Setup Wizard Steps:
├── 1. Company profile completion
├── 2. Branding setup (logo upload, color scheme)
├── 3. Payment method for billing
├── 4. Payout configuration (bank details for host payments)
└── 5. First host invitation (optional)

Step 4: Activation Complete
┌─────────────────────────────────────────────────────────────────────────────┐
│ Client can now:                                                              │
│ ✓ Access their branded backoffice                                           │
│ ✓ Invite and manage hosts                                                   │
│ ✓ Monitor live sessions                                                     │
│ ✓ Process payouts                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Onboarding a Host

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOST ONBOARDING JOURNEY                             │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Invitation (Client Backoffice)
┌─────────────────────────────────────────────────────────────────────────────┐
│ Client Admin Actions:                                                        │
│ 1. Navigate to Host Management > Add New Host                               │
│ 2. Enter host details (name, email, phone)                                  │
│ 3. Set payout rate (percentage of gift value)                               │
│ 4. Assign category/tags (optional)                                          │
│ 5. Submit → System sends invitation email to host                           │
└─────────────────────────────────────────────────────────────────────────────┘

Step 2: Host Registration
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Invitation  │───▶│  Account    │───▶│  Profile    │
│ Email       │    │  Creation   │    │  Setup      │
└─────────────┘    └─────────────┘    └─────────────┘

Account Creation Form:
├── Email (pre-filled from invitation)
├── Password setup
├── Full legal name
├── Display name
├── Phone number
└── Terms acceptance

Profile Setup:
├── Profile photo upload
├── Bio/description
├── Social media links (optional)
└── Category preferences

Step 3: Verification & Approval
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Email     │───▶│  ID/KYC     │───▶│   Client    │
│ Verification│    │ (optional)  │    │  Approval   │
└─────────────┘    └─────────────┘    └─────────────┘

Step 4: Payment Setup
┌─────────────────────────────────────────────────────────────────────────────┐
│ Host configures payout method:                                              │
│ ├── Bank account details                                                    │
│ ├── E-wallet (GoPay, OVO, Dana - if supported)                             │
│ └── Verification of payment details                                         │
└─────────────────────────────────────────────────────────────────────────────┘

Step 5: Ready to Go Live
┌─────────────────────────────────────────────────────────────────────────────┐
│ Host can now:                                                                │
│ ✓ Access Host Portal dashboard                                              │
│ ✓ Launch Host Web Client                                                    │
│ ✓ Start live sessions                                                       │
│ ✓ Receive gifts and track earnings                                          │
│ ✓ Request payouts                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Host Starting a Live Session

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HOST GOING LIVE JOURNEY                                │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Access Host Web Client
┌─────────────┐    ┌─────────────┐
│ Host Portal │───▶│ "Go Live"   │
│ Dashboard   │    │  Button     │
└─────────────┘    └─────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Host Web Client    │
              │  Opens in Browser   │
              └─────────────────────┘

Step 2: Pre-Live Setup
┌─────────────────────────────────────────────────────────────────────────────┐
│ Pre-Live Screen:                                                             │
│                                                                              │
│  ┌──────────────────────────────┐                                           │
│  │                              │  Session Title: [__________________]      │
│  │    CAMERA PREVIEW            │                                           │
│  │                              │  Category: [Gaming ▼]                     │
│  │    [Host sees themselves]    │                                           │
│  │                              │  ┌─────────────────────────────────┐      │
│  │                              │  │     🎥 Camera: OK               │      │
│  └──────────────────────────────┘  │     🎤 Mic: OK                  │      │
│                                    │     📶 Connection: Good         │      │
│  [⚙️ Settings] [🔄 Flip Camera]    └─────────────────────────────────┘      │
│                                                                              │
│             ┌─────────────────────────────────────────┐                     │
│             │         🔴 START LIVE SESSION           │                     │
│             └─────────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 3: Live Session
┌─────────────────────────────────────────────────────────────────────────────┐
│ Live Session Screen:                                                         │
│                                                                              │
│  🔴 LIVE  │  👁 1,234 viewers  │  ⏱ 00:45:23  │  💰 $127.50               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │                                                                        │ │
│  │                    LIVE VIDEO FEED                                     │ │
│  │                                                                        │ │
│  │                    ┌────────────────┐                                  │ │
│  │                    │ 🎁 Rose x5     │  ← Gift animation overlay        │ │
│  │                    │ from @viewer1  │                                  │ │
│  │                    └────────────────┘                                  │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Chat Stream:                          Quick Actions:                        │
│  ┌────────────────────────┐           ┌─────┐ ┌─────┐ ┌─────┐              │
│  │ @user1: Hello!         │           │ 🔇  │ │ 🔄  │ │ ✨  │              │
│  │ @user2: Great stream!  │           │Mute │ │Flip │ │FX   │              │
│  │ @user3 sent 🌹 x3      │           └─────┘ └─────┘ └─────┘              │
│  │ @user4: 🔥🔥🔥          │                                                │
│  └────────────────────────┘           ┌─────────────────────────┐          │
│                                       │   ⏹ END SESSION        │          │
│                                       └─────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘

Step 4: End Session & Summary
┌─────────────────────────────────────────────────────────────────────────────┐
│ Post-Live Summary Screen:                                                    │
│                                                                              │
│  ✅ Session Ended Successfully                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  📊 SESSION SUMMARY                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Duration:        1h 23m 45s                                        │   │
│  │  Peak Viewers:    2,456                                             │   │
│  │  Total Viewers:   8,901                                             │   │
│  │  Gifts Received:  342                                               │   │
│  │  ─────────────────────────────────────────────                      │   │
│  │  💰 Total Earnings:  $284.50                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Top Gifts:                                                                  │
│  🌹 Rose (156)  │  💎 Diamond (23)  │  🚀 Rocket (12)                      │
│                                                                              │
│  [💾 Save Recording]  [📤 Share]  [📊 View Full Analytics]                 │
│                                                                              │
│            ┌─────────────────────────────────────────┐                     │
│            │       Return to Dashboard               │                     │
│            └─────────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Payout Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PAYOUT WORKFLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                    EARNINGS ACCUMULATION
                    ═══════════════════════

    Viewer          Gift            System           Host
    Sends Gift  →   Purchased   →   Records      →   Earnings
    ($10)           (-Platform      Gift Event       Updated
                     Fee)                            (+$5.60)

    Revenue Split Example:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Gift Value:              $10.00                                    │
    │  ├── Platform Fee (20%):  -$2.00  → Provider                       │
    │  ├── Client Share (24%):  -$2.40  → Client Revenue                 │
    │  └── Host Share (56%):    +$5.60  → Host Earnings Balance          │
    └─────────────────────────────────────────────────────────────────────┘


                    HOST PAYOUT REQUEST
                    ════════════════════

Step 1: Host Requests Payout
┌─────────────────────────────────────────────────────────────────────────────┐
│ Host Portal > Payouts > Request Payout                                       │
│                                                                              │
│  Available Balance: $1,250.00                                               │
│  Minimum Payout: $50.00                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Payout Amount: [$1,250.00    ]  [MAX]                                      │
│                                                                              │
│  Payout Method: [Bank Transfer - ***4521 ▼]                                 │
│                                                                              │
│  Estimated Processing: 3-5 business days                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Summary:                                                           │   │
│  │  Payout Amount:    $1,250.00                                        │   │
│  │  Processing Fee:   -$2.50                                           │   │
│  │  You will receive: $1,247.50                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│            ┌─────────────────────────────────────────┐                     │
│            │       Submit Payout Request             │                     │
│            └─────────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 2: Client Review & Approval
┌─────────────────────────────────────────────────────────────────────────────┐
│ Client Backoffice > Finance > Payout Queue                                   │
│                                                                              │
│  Pending Payouts (3)                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Host        │ Amount    │ Method      │ Requested    │ Action      │   │
│  │─────────────┼───────────┼─────────────┼──────────────┼─────────────│   │
│  │ Jane Doe    │ $1,247.50 │ Bank ****21 │ 2 hours ago  │ [✓] [✗]    │   │
│  │ John Smith  │ $589.00   │ E-Wallet    │ 1 day ago    │ [✓] [✗]    │   │
│  │ Alex Kim    │ $2,100.00 │ Bank ****87 │ 2 days ago   │ [✓] [✗]    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  [Approve Selected]  [Export for Bulk Transfer]                             │
└─────────────────────────────────────────────────────────────────────────────┘

Step 3: Payout Processing
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│  Approved  │───▶│ Processing │───▶│ Transferred│───▶│ Completed  │
│  (Client)  │    │  (System)  │    │  (Bank)    │    │  (Host)    │
└────────────┘    └────────────┘    └────────────┘    └────────────┘

Step 4: Host Notification
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📧 Email Notification to Host:                                               │
│                                                                              │
│ Subject: Payout Completed - $1,247.50                                       │
│                                                                              │
│ Your payout request has been processed!                                     │
│                                                                              │
│ Amount: $1,247.50                                                           │
│ Method: Bank Transfer (****4521)                                            │
│ Reference: PAY-2024-00892                                                   │
│                                                                              │
│ Funds should arrive in 1-2 business days.                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    PAYOUT STATUS TRACKING
                    ═══════════════════════

Host Portal > Payouts > History
┌─────────────────────────────────────────────────────────────────────────────┐
│ Payout History                                                               │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Date       │ Amount    │ Method   │ Status     │ Reference            │ │
│ │────────────┼───────────┼──────────┼────────────┼──────────────────────│ │
│ │ Jan 20     │ $1,247.50 │ Bank     │ ✅ Paid    │ PAY-2024-00892       │ │
│ │ Jan 05     │ $890.00   │ Bank     │ ✅ Paid    │ PAY-2024-00756       │ │
│ │ Dec 22     │ $2,340.00 │ E-Wallet │ ✅ Paid    │ PAY-2024-00621       │ │
│ │ Dec 08     │ $1,100.00 │ Bank     │ ✅ Paid    │ PAY-2024-00489       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Model

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA MODEL OVERVIEW                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Provider   │       │     Plan     │       │   GiftType   │
│──────────────│       │──────────────│       │──────────────│
│ id           │       │ id           │       │ id           │
│ name         │       │ name         │       │ name         │
│ email        │       │ max_hosts    │       │ icon_url     │
│ created_at   │       │ max_streams  │       │ price        │
└──────┬───────┘       │ storage_gb   │       │ provider_id  │
       │               │ price_monthly│       │ is_active    │
       │               │ provider_id  │       └──────┬───────┘
       │               └──────┬───────┘              │
       │                      │                      │
       │ 1:N                  │ 1:N                  │ 1:N
       ▼                      ▼                      ▼
┌──────────────┐       ┌─────────────────────────────────────┐
│    Client    │       │                                     │
│──────────────│◄──────│  Client subscribes to Plan          │
│ id           │       │  Client can use GiftTypes           │
│ provider_id  │       │                                     │
│ plan_id      │       └─────────────────────────────────────┘
│ company_name │
│ contact_email│
│ branding     │───────────────────────┐
│ revenue_share│                       │
│ status       │                       │
│ created_at   │                       │
└──────┬───────┘                       │
       │                               │
       │ 1:N                           │
       ▼                               ▼
┌──────────────┐               ┌──────────────┐
│     Host     │               │ClientGiftMap │
│──────────────│               │──────────────│
│ id           │               │ client_id    │
│ client_id    │               │ gift_type_id │
│ email        │               │ is_enabled   │
│ display_name │               └──────────────┘
│ profile_photo│
│ payout_rate  │
│ payment_info │
│ status       │
│ created_at   │
└──────┬───────┘
       │
       │ 1:N
       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ LiveSession  │       │     Gift     │       │    Payout    │
│──────────────│       │──────────────│       │──────────────│
│ id           │◄──────│ id           │       │ id           │
│ host_id      │  1:N  │ session_id   │       │ host_id      │
│ title        │       │ gift_type_id │       │ amount       │
│ status       │       │ viewer_id    │       │ fee          │
│ started_at   │       │ quantity     │       │ net_amount   │
│ ended_at     │       │ value        │       │ payment_method│
│ peak_viewers │       │ host_earning │       │ status       │
│ total_viewers│       │ client_share │       │ requested_at │
│ total_gifts  │       │ provider_fee │       │ processed_at │
│ total_earnings│      │ created_at   │       │ reference    │
└──────────────┘       └──────────────┘       └──────────────┘
```

### 4.2 Entity Definitions

#### Provider (Super Admin)
```
Provider {
    id: UUID (PK)
    name: String
    email: String (unique)
    password_hash: String
    phone: String
    company_name: String
    logo_url: String
    settings: JSON
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### Plan
```
Plan {
    id: UUID (PK)
    provider_id: UUID (FK → Provider)
    name: String                    // "Basic", "Pro", "Enterprise"
    description: Text
    max_hosts: Integer              // Host limit per client
    max_concurrent_streams: Integer // Simultaneous streams
    storage_gb: Integer             // Recording storage
    features: JSON                  // Feature flags
    price_monthly: Decimal
    price_yearly: Decimal
    is_active: Boolean
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### Client (Brand/Operator)
```
Client {
    id: UUID (PK)
    provider_id: UUID (FK → Provider)
    plan_id: UUID (FK → Plan)
    company_name: String
    contact_name: String
    contact_email: String (unique)
    contact_phone: String
    password_hash: String
    branding: JSON {
        logo_url: String
        primary_color: String
        secondary_color: String
        custom_domain: String
    }
    revenue_share_percent: Decimal  // Client's share (e.g., 70%)
    min_host_payout: Decimal        // Minimum payout threshold
    status: Enum ['pending', 'active', 'suspended', 'terminated']
    settings: JSON
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### Host (Talent)
```
Host {
    id: UUID (PK)
    client_id: UUID (FK → Client)
    email: String (unique per client)
    password_hash: String
    display_name: String
    legal_name: String
    profile_photo_url: String
    bio: Text
    social_links: JSON
    payout_rate_percent: Decimal    // Host's share of client revenue
    payment_info: JSON {
        type: Enum ['bank', 'ewallet']
        bank_name: String
        account_number: String (encrypted)
        account_holder: String
    }
    available_balance: Decimal
    lifetime_earnings: Decimal
    status: Enum ['pending', 'active', 'suspended', 'terminated']
    verified_at: Timestamp
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### LiveSession
```
LiveSession {
    id: UUID (PK)
    host_id: UUID (FK → Host)
    title: String
    category: String
    status: Enum ['scheduled', 'live', 'ended', 'cancelled']
    stream_key: String (unique)
    scheduled_at: Timestamp
    started_at: Timestamp
    ended_at: Timestamp
    duration_seconds: Integer
    peak_viewers: Integer
    total_viewers: Integer
    total_gifts: Integer
    total_gift_value: Decimal
    total_earnings: Decimal         // Host's earnings from this session
    recording_url: String
    thumbnail_url: String
    metadata: JSON
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### GiftType
```
GiftType {
    id: UUID (PK)
    provider_id: UUID (FK → Provider)
    name: String                    // "Rose", "Diamond", "Rocket"
    icon_url: String
    animation_url: String
    price: Decimal                  // Price in platform currency
    sort_order: Integer
    is_active: Boolean
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### Gift (Transaction Record)
```
Gift {
    id: UUID (PK)
    session_id: UUID (FK → LiveSession)
    gift_type_id: UUID (FK → GiftType)
    viewer_id: String               // External viewer identifier
    quantity: Integer
    unit_price: Decimal
    total_value: Decimal            // quantity × unit_price
    provider_fee: Decimal           // Platform cut
    client_share: Decimal           // Client revenue
    host_earning: Decimal           // Host earnings
    created_at: Timestamp
}
```

#### Payout
```
Payout {
    id: UUID (PK)
    host_id: UUID (FK → Host)
    amount_requested: Decimal
    processing_fee: Decimal
    net_amount: Decimal             // amount - fee
    payment_method: JSON
    status: Enum ['pending', 'approved', 'processing', 'completed', 'rejected', 'failed']
    requested_at: Timestamp
    approved_at: Timestamp
    approved_by: UUID (FK → Client user)
    processed_at: Timestamp
    completed_at: Timestamp
    reference_number: String
    failure_reason: String
    notes: Text
    created_at: Timestamp
    updated_at: Timestamp
}
```

#### ClientGiftMapping
```
ClientGiftMapping {
    id: UUID (PK)
    client_id: UUID (FK → Client)
    gift_type_id: UUID (FK → GiftType)
    is_enabled: Boolean
    custom_price: Decimal           // Override if client wants different price
    created_at: Timestamp
    updated_at: Timestamp
}
```

### 4.3 Key Relationships Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| Provider → Client | 1:N | Provider onboards multiple clients |
| Provider → Plan | 1:N | Provider defines subscription plans |
| Provider → GiftType | 1:N | Provider manages gift catalog |
| Client → Host | 1:N | Client manages multiple hosts |
| Client → Plan | N:1 | Client subscribes to one plan |
| Client → GiftType | N:M | Client selects which gifts to enable |
| Host → LiveSession | 1:N | Host conducts multiple sessions |
| LiveSession → Gift | 1:N | Session receives multiple gifts |
| Host → Payout | 1:N | Host requests multiple payouts |

---

## 5. Feature Priority Table (v1)

### 5.1 Must-Have (MVP - Required for Launch)

| # | Feature | Module | Role | Description |
|---|---------|--------|------|-------------|
| 1 | Client CRUD | Client Management | Provider | Create, read, update, delete clients |
| 2 | Plan Assignment | Client Management | Provider | Assign/change subscription plans |
| 3 | Revenue Share Config | Client Management | Provider | Set client revenue percentages |
| 4 | Host CRUD | Host Management | Client | Create, read, update, delete hosts |
| 5 | Host Payout Rate | Host Management | Client | Configure host earning percentages |
| 6 | Gift Catalog Management | Gift Catalog | Provider | Create/edit gift types with pricing |
| 7 | Live Session - Start/End | Host Web Client | Host | Basic go-live functionality |
| 8 | Camera/Mic Setup | Host Web Client | Host | Pre-live equipment check |
| 9 | Real-time Viewer Count | Host Web Client | Host | Display current viewers |
| 10 | Gift Reception | Host Web Client | Host | Receive and display gifts in real-time |
| 11 | Session Earnings Display | Host Web Client | Host | Show current session earnings |
| 12 | Host Earnings Dashboard | Earnings | Host | View earnings summary |
| 13 | Payout Request | Payouts | Host | Submit payout request |
| 14 | Payout Approval | Payouts | Client | Approve/reject host payouts |
| 15 | Basic Analytics | Dashboard | All | Key metrics per role |
| 16 | User Authentication | Auth | All | Login/logout/password reset |
| 17 | Email Notifications | Notifications | All | Critical event emails |

### 5.2 Should-Have (Post-MVP - Next Priority)

| # | Feature | Module | Role | Description |
|---|---------|--------|------|-------------|
| 18 | Client Branding | Branding | Client | Logo, colors, custom domain |
| 19 | Host Profile | Profile | Host | Bio, photo, social links |
| 20 | Session History | Sessions | Host, Client | View past sessions with details |
| 21 | Session Recording | Sessions | Host | Save session recordings |
| 22 | Gift Analytics | Analytics | Client, Provider | Gift performance reports |
| 23 | Host Leaderboard | Analytics | Client | Rank hosts by performance |
| 24 | Bulk Payout Export | Payouts | Client | Export for batch processing |
| 25 | Client Usage Limits | Plans | Provider | Enforce plan limits |
| 26 | Session Scheduling | Sessions | Host, Client | Schedule upcoming sessions |
| 27 | Host Verification | Host Management | Client | KYC/identity verification |
| 28 | Chat Moderation | Host Web Client | Host | Basic chat tools |
| 29 | API Keys Management | Settings | Client | Generate/revoke API keys |
| 30 | Audit Logs | Settings | Provider | Track system changes |
| 31 | Role-based Sub-accounts | Settings | Client | Team member access |
| 32 | Revenue Reports | Finance | Provider, Client | Detailed financial reports |

### 5.3 Nice-to-Have (Future - Lower Priority)

| # | Feature | Module | Role | Description |
|---|---------|--------|------|-------------|
| 33 | Advanced Analytics | Analytics | All | Custom report builder |
| 34 | Stream Quality Settings | Host Web Client | Host | Bitrate/resolution options |
| 35 | Virtual Backgrounds | Host Web Client | Host | Background effects |
| 36 | Beauty Filters | Host Web Client | Host | Face enhancement filters |
| 37 | Multi-host Sessions | Sessions | Host | Co-streaming support |
| 38 | Scheduled Campaigns | Campaigns | Client | Promotional events |
| 39 | Viewer Engagement Tools | Host Web Client | Host | Polls, Q&A, games |
| 40 | Mobile Host App | Mobile | Host | Native mobile streaming |
| 41 | Webhook Integration | Settings | Client | Real-time event webhooks |
| 42 | SSO Integration | Auth | Client | SAML/OAuth for enterprise |
| 43 | Multi-language Support | Platform | All | Localization |
| 44 | Dark Mode | UI | All | Theme switching |
| 45 | Gift Animations | Gifts | Host | Premium gift effects |
| 46 | Tipping (Custom Amount) | Gifts | Host | Free-form donations |
| 47 | Subscription/Membership | Monetization | Host | Recurring viewer support |
| 48 | VOD Content | Content | Host | On-demand video hosting |

### 5.4 Priority Matrix Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FEATURE PRIORITY MATRIX                              │
└─────────────────────────────────────────────────────────────────────────────┘

                        IMPACT
                    High        Low
               ┌──────────┬──────────┐
          High │  MUST    │  SHOULD  │
    EFFORT     │  HAVE    │  HAVE    │
               ├──────────┼──────────┤
          Low  │  SHOULD  │  NICE TO │
               │  HAVE    │  HAVE    │
               └──────────┴──────────┘

Must-Have (17 features):
├── Core functionality required for platform to operate
├── Essential for all three user roles
├── Timeline: v1.0 Launch
└── Focus: Client/Host onboarding, Live streaming, Basic payouts

Should-Have (15 features):
├── Enhances user experience and platform value
├── Important for client retention and growth
├── Timeline: v1.1 - v1.3
└── Focus: Branding, Analytics, Advanced payouts

Nice-to-Have (16 features):
├── Differentiators and premium features
├── Competitive advantage features
├── Timeline: v2.0+
└── Focus: Engagement, Mobile, Advanced monetization
```

---

## 6. Technical Recommendations

### 6.1 Recommended Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | React + TypeScript | Component reusability, type safety |
| UI Framework | Ant Design / MUI | B2B-friendly, comprehensive components |
| State Management | React Query + Zustand | Server state + client state |
| Backend | Node.js + Express / FastAPI | Scalable, good ecosystem |
| Database | PostgreSQL | Relational data, ACID compliance |
| Cache | Redis | Session management, real-time data |
| Streaming | WebRTC + Media Server | Low latency live streaming |
| Real-time | WebSocket / Socket.io | Live updates, chat, gifts |
| Storage | S3-compatible | Recordings, assets |
| Auth | JWT + OAuth2 | Secure, scalable auth |

### 6.2 Security Considerations

- **Data Encryption**: Encrypt sensitive data (payment info) at rest
- **API Security**: Rate limiting, input validation, CORS
- **Authentication**: MFA option for admin roles
- **Audit Trail**: Log all sensitive operations
- **PCI Compliance**: Consider for payment processing
- **Data Isolation**: Strict multi-tenant data separation

### 6.3 Scalability Considerations

- **Microservices**: Separate streaming, gifts, payouts services
- **CDN**: Edge delivery for streaming content
- **Database Sharding**: Plan for client-based partitioning
- **Queue System**: Async processing for payouts, notifications
- **Auto-scaling**: Cloud-native deployment for traffic spikes

---

## 7. Wireframe Sketches

### 7.1 Provider Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏢 StreamPlatform Admin                    🔔  👤 Admin ▼                  │
├─────────────────┬───────────────────────────────────────────────────────────┤
│                 │                                                           │
│  📊 Dashboard   │  Dashboard Overview                                       │
│  👥 Clients     │  ─────────────────────────────────────────────────────   │
│  💳 Plans       │                                                           │
│  💰 Revenue     │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  🎁 Gifts       │  │ 24      │  │ 1,847   │  │ 156     │  │ $45.2K  │     │
│  📈 Analytics   │  │ Clients │  │ Hosts   │  │ Live Now│  │ Revenue │     │
│  ⚙️ Settings    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
│                 │                                                           │
│                 │  Recent Clients                        Revenue Trend      │
│                 │  ┌────────────────────────────┐       ┌────────────────┐ │
│                 │  │ Client        │ Status     │       │    📈          │ │
│                 │  │───────────────┼────────────│       │   /\  /\       │ │
│                 │  │ Brand A       │ 🟢 Active  │       │  /  \/  \      │ │
│                 │  │ Brand B       │ 🟢 Active  │       │ /       \     │ │
│                 │  │ Brand C       │ 🟡 Pending │       └────────────────┘ │
│                 │  └────────────────────────────┘                          │
│                 │                                                           │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 7.2 Client Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎬 BrandName Live                          🔔  👤 Manager ▼                │
├─────────────────┬───────────────────────────────────────────────────────────┤
│                 │                                                           │
│  📊 Dashboard   │  Today's Overview                    Quick Actions        │
│  👤 Hosts       │  ─────────────────────────           ───────────────      │
│  🎥 Sessions    │                                      [+ Add Host]         │
│  📢 Campaigns   │  ┌─────────┐  ┌─────────┐           [View Payouts]       │
│  💰 Finance     │  │ 12      │  │ 5       │                                │
│  🎁 Gifts       │  │ Active  │  │ Live    │           Pending Payouts      │
│  🎨 Branding    │  │ Hosts   │  │ Now     │           ┌────────────────┐   │
│  📈 Analytics   │  └─────────┘  └─────────┘           │ 8 requests     │   │
│  ⚙️ Settings    │                                      │ $4,250 total   │   │
│                 │  ┌─────────┐  ┌─────────┐           │ [Review →]     │   │
│                 │  │ $2.4K   │  │ 892     │           └────────────────┘   │
│                 │  │ Today's │  │ Viewers │                                │
│                 │  │ Revenue │  │ Peak    │                                │
│                 │  └─────────┘  └─────────┘                                │
│                 │                                                           │
│                 │  Top Hosts Today                                          │
│                 │  ┌────────────────────────────────────────────────────┐  │
│                 │  │ #1 Jane ($450) │ #2 John ($380) │ #3 Alex ($290)  │  │
│                 │  └────────────────────────────────────────────────────┘  │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 7.3 Host Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎬 BrandName Live                          🔔  👤 Jane Doe ▼               │
├─────────────────┬───────────────────────────────────────────────────────────┤
│                 │                                                           │
│  📊 Dashboard   │  Welcome back, Jane! 👋                                   │
│  🔴 Go Live     │  ───────────────────────────────────────────────────────  │
│  🎥 My Sessions │                                                           │
│  💰 Earnings    │  ┌─────────────────────────────────────────────────────┐  │
│  💳 Payouts     │  │                                                     │  │
│  📈 Performance │  │         ┌─────────────────────────────┐             │  │
│  👤 Profile     │  │         │    🔴 START LIVE SESSION    │             │  │
│                 │  │         └─────────────────────────────┘             │  │
│                 │  │                                                     │  │
│                 │  └─────────────────────────────────────────────────────┘  │
│                 │                                                           │
│                 │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│                 │  │ $1,250  │  │ $4,890  │  │ 23      │  │ 45.2K   │     │
│                 │  │Available│  │ This    │  │Sessions │  │ Total   │     │
│                 │  │ Balance │  │ Month   │  │ (Month) │  │ Viewers │     │
│                 │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │
│                 │                                                           │
│                 │  Recent Sessions                                          │
│                 │  ┌─────────────────────────────────────────────────────┐ │
│                 │  │ Yesterday 8PM │ 2h 15m │ 1.2K viewers │ $285      │ │
│                 │  │ Jan 18, 9PM   │ 1h 45m │ 980 viewers  │ $195      │ │
│                 │  └─────────────────────────────────────────────────────┘ │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 8. Appendix

### 8.1 Glossary

| Term | Definition |
|------|------------|
| **Provider** | The SaaS platform owner who sells whitelabel solutions |
| **Client** | A brand/company that licenses the platform |
| **Host** | A content creator who broadcasts live |
| **Viewer** | End user who watches streams and sends gifts |
| **Gift** | Virtual item purchased by viewers to support hosts |
| **Payout** | Transfer of earnings from platform to host |
| **Revenue Share** | Percentage split of gift revenue |
| **Whitelabel** | Platform branded as client's own product |

### 8.2 Revenue Flow Example

```
Viewer purchases $10 gift
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    REVENUE DISTRIBUTION                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Gift Value: $10.00                                       │
│  ├── Provider Fee (20%):     $2.00 → Platform Revenue    │
│  └── Remaining (80%):        $8.00                        │
│      ├── Client Share (30%): $2.40 → Client Revenue      │
│      └── Host Share (70%):   $5.60 → Host Earnings       │
│                                                           │
└───────────────────────────────────────────────────────────┘

Note: Percentages are configurable per client and per host.
```

### 8.3 Status Definitions

**Client Status:**
- `pending` - Account created, awaiting verification
- `active` - Fully operational
- `suspended` - Temporarily disabled (payment/policy issue)
- `terminated` - Permanently closed

**Host Status:**
- `pending` - Invited, awaiting registration completion
- `active` - Can go live and earn
- `suspended` - Temporarily disabled
- `terminated` - Permanently removed

**LiveSession Status:**
- `scheduled` - Upcoming scheduled session
- `live` - Currently broadcasting
- `ended` - Session completed normally
- `cancelled` - Session cancelled before starting

**Payout Status:**
- `pending` - Awaiting client approval
- `approved` - Approved, awaiting processing
- `processing` - Payment being processed
- `completed` - Funds transferred successfully
- `rejected` - Declined by client
- `failed` - Transfer failed

---

*Document Version: 1.0*
*Created: January 2026*
*Author: Product Architecture Team*
