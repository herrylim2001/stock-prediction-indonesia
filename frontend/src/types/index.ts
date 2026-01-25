// User roles
export type UserRole = 'provider' | 'client' | 'host';

// Auth
export interface User {
  id: string;
  email: string;
  role: UserRole;
  name?: string;
  company_name?: string;
  display_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  role: UserRole;
}

export interface LoginResponse {
  token: string;
  expires_at: string;
  user: User;
}

// Provider
export interface Provider {
  id: string;
  name: string;
  email: string;
  phone?: string;
  company_name?: string;
  logo_url?: string;
  created_at: string;
}

// Plan
export interface Plan {
  id: string;
  provider_id: string;
  name: string;
  description?: string;
  max_hosts: number;
  max_concurrent_streams: number;
  storage_gb: number;
  features: Record<string, boolean>;
  price_monthly: number;
  price_yearly: number;
  is_active: boolean;
  created_at: string;
}

// Client
export type ClientStatus = 'pending' | 'active' | 'suspended' | 'terminated';

export interface ClientBranding {
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  custom_domain?: string;
}

export interface Client {
  id: string;
  provider_id: string;
  plan_id?: string;
  company_name: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string;
  branding?: ClientBranding;
  revenue_share_percent: number;
  min_host_payout: number;
  status: ClientStatus;
  plan?: Plan;
  hosts?: Host[];
  created_at: string;
}

// Host
export type HostStatus = 'pending' | 'active' | 'suspended' | 'terminated';

export interface PaymentInfo {
  type: 'bank' | 'ewallet';
  bank_name?: string;
  account_number?: string;
  account_holder?: string;
}

export interface Host {
  id: string;
  client_id: string;
  email: string;
  display_name: string;
  legal_name?: string;
  profile_photo_url?: string;
  bio?: string;
  social_links?: Record<string, string>;
  payout_rate_percent: number;
  payment_info?: PaymentInfo;
  available_balance: number;
  lifetime_earnings: number;
  status: HostStatus;
  verified_at?: string;
  created_at: string;
}

// Live Session
export type SessionStatus = 'scheduled' | 'live' | 'ended' | 'cancelled';

export interface LiveSession {
  id: string;
  host_id: string;
  title: string;
  category?: string;
  status: SessionStatus;
  stream_key?: string;
  scheduled_at?: string;
  started_at?: string;
  ended_at?: string;
  duration_seconds: number;
  peak_viewers: number;
  total_viewers: number;
  total_gifts: number;
  total_gift_value: number;
  total_earnings: number;
  recording_url?: string;
  thumbnail_url?: string;
  host?: Host;
  created_at: string;
}

// Gift
export interface GiftType {
  id: string;
  provider_id: string;
  name: string;
  icon_url?: string;
  animation_url?: string;
  price: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
}

export interface Gift {
  id: string;
  session_id: string;
  gift_type_id: string;
  viewer_id: string;
  quantity: number;
  unit_price: number;
  total_value: number;
  provider_fee: number;
  client_share: number;
  host_earning: number;
  gift_type?: GiftType;
  created_at: string;
}

// Payout
export type PayoutStatus = 'pending' | 'approved' | 'processing' | 'completed' | 'rejected' | 'failed';

export interface Payout {
  id: string;
  host_id: string;
  amount_requested: number;
  processing_fee: number;
  net_amount: number;
  payment_method?: PaymentInfo;
  status: PayoutStatus;
  requested_at: string;
  approved_at?: string;
  approved_by?: string;
  processed_at?: string;
  completed_at?: string;
  reference_number?: string;
  failure_reason?: string;
  notes?: string;
  host?: Host;
  created_at: string;
}

// Dashboard Stats
export interface ProviderDashboardStats {
  total_clients: number;
  active_clients: number;
  total_hosts: number;
  active_sessions: number;
  today_revenue: number;
  month_revenue: number;
}

export interface ClientDashboardStats {
  total_hosts: number;
  active_hosts: number;
  active_sessions: number;
  today_sessions: number;
  today_revenue: number;
  month_revenue: number;
  pending_payouts_count: number;
  pending_payouts_amount: number;
}

export interface HostDashboardStats {
  today_earnings: number;
  week_earnings: number;
  month_earnings: number;
  month_sessions: number;
  month_viewers: number;
}

// API Response wrapper
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
