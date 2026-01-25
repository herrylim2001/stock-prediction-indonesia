import axios, { AxiosError, AxiosInstance } from 'axios';
import { useAuthStore } from '@/lib/store';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(email: string, password: string, role: string) {
    const response = await this.client.post('/auth/login', { email, password, role });
    return response.data;
  }

  async registerProvider(data: { name: string; email: string; password: string; company_name?: string }) {
    const response = await this.client.post('/auth/register/provider', data);
    return response.data;
  }

  async getMe() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Provider APIs
  async getProviderDashboard() {
    const response = await this.client.get('/provider/dashboard');
    return response.data;
  }

  async getClients(params?: { status?: string; search?: string }) {
    const response = await this.client.get('/provider/clients', { params });
    return response.data;
  }

  async getClient(id: string) {
    const response = await this.client.get(`/provider/clients/${id}`);
    return response.data;
  }

  async createClient(data: any) {
    const response = await this.client.post('/provider/clients', data);
    return response.data;
  }

  async updateClient(id: string, data: any) {
    const response = await this.client.put(`/provider/clients/${id}`, data);
    return response.data;
  }

  async deleteClient(id: string) {
    const response = await this.client.delete(`/provider/clients/${id}`);
    return response.data;
  }

  async activateClient(id: string) {
    const response = await this.client.post(`/provider/clients/${id}/activate`);
    return response.data;
  }

  async suspendClient(id: string) {
    const response = await this.client.post(`/provider/clients/${id}/suspend`);
    return response.data;
  }

  async getProviderGiftTypes() {
    const response = await this.client.get('/provider/gifts');
    return response.data;
  }

  async createGiftType(data: any) {
    const response = await this.client.post('/provider/gifts', data);
    return response.data;
  }

  async updateGiftType(id: string, data: any) {
    const response = await this.client.put(`/provider/gifts/${id}`, data);
    return response.data;
  }

  async deleteGiftType(id: string) {
    const response = await this.client.delete(`/provider/gifts/${id}`);
    return response.data;
  }

  // Client APIs
  async getClientDashboard() {
    const response = await this.client.get('/client/dashboard');
    return response.data;
  }

  async getHosts(params?: { status?: string; search?: string }) {
    const response = await this.client.get('/client/hosts', { params });
    return response.data;
  }

  async getHost(id: string) {
    const response = await this.client.get(`/client/hosts/${id}`);
    return response.data;
  }

  async createHost(data: any) {
    const response = await this.client.post('/client/hosts', data);
    return response.data;
  }

  async updateHost(id: string, data: any) {
    const response = await this.client.put(`/client/hosts/${id}`, data);
    return response.data;
  }

  async deleteHost(id: string) {
    const response = await this.client.delete(`/client/hosts/${id}`);
    return response.data;
  }

  async activateHost(id: string) {
    const response = await this.client.post(`/client/hosts/${id}/activate`);
    return response.data;
  }

  async getClientSessions(params?: { status?: string; host_id?: string }) {
    const response = await this.client.get('/client/sessions', { params });
    return response.data;
  }

  async getActiveSessions() {
    const response = await this.client.get('/client/sessions/active');
    return response.data;
  }

  async getClientPayouts(params?: { status?: string; host_id?: string }) {
    const response = await this.client.get('/client/payouts', { params });
    return response.data;
  }

  async getPendingPayouts() {
    const response = await this.client.get('/client/payouts/pending');
    return response.data;
  }

  async approvePayout(id: string) {
    const response = await this.client.post(`/client/payouts/${id}/approve`);
    return response.data;
  }

  async rejectPayout(id: string, reason: string) {
    const response = await this.client.post(`/client/payouts/${id}/reject`, { reason });
    return response.data;
  }

  async completePayout(id: string, reference_number: string) {
    const response = await this.client.post(`/client/payouts/${id}/complete`, { reference_number });
    return response.data;
  }

  // Host APIs
  async getHostDashboard() {
    const response = await this.client.get('/host/dashboard');
    return response.data;
  }

  async getHostProfile() {
    const response = await this.client.get('/host/profile');
    return response.data;
  }

  async updateHostProfile(data: any) {
    const response = await this.client.put('/host/profile', data);
    return response.data;
  }

  async getHostEarnings() {
    const response = await this.client.get('/host/earnings');
    return response.data;
  }

  async getHostSessions(params?: { status?: string }) {
    const response = await this.client.get('/host/sessions', { params });
    return response.data;
  }

  async getActiveSession() {
    const response = await this.client.get('/host/sessions/active');
    return response.data;
  }

  async getSessionDetails(id: string) {
    const response = await this.client.get(`/host/sessions/${id}`);
    return response.data;
  }

  async startSession(data: { title: string; category?: string }) {
    const response = await this.client.post('/host/sessions/start', data);
    return response.data;
  }

  async endSession(id: string) {
    const response = await this.client.post(`/host/sessions/${id}/end`);
    return response.data;
  }

  async getHostPayouts() {
    const response = await this.client.get('/host/payouts');
    return response.data;
  }

  async requestPayout(amount: number) {
    const response = await this.client.post('/host/payouts', { amount });
    return response.data;
  }
}

export const api = new ApiClient();
