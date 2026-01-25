'use client';

import { useQuery } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { api } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Building2, Users, Radio, DollarSign } from 'lucide-react';
import Link from 'next/link';

export default function ProviderDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['provider-dashboard'],
    queryFn: () => api.getProviderDashboard(),
  });

  const stats = data?.stats;
  const recentClients = data?.recent_clients || [];

  return (
    <DashboardLayout requiredRole="provider">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Welcome back! Here's your platform overview.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Clients"
            value={isLoading ? '...' : stats?.total_clients || 0}
            icon={Building2}
          />
          <StatCard
            title="Active Clients"
            value={isLoading ? '...' : stats?.active_clients || 0}
            icon={Building2}
          />
          <StatCard
            title="Total Hosts"
            value={isLoading ? '...' : stats?.total_hosts || 0}
            icon={Users}
          />
          <StatCard
            title="Live Now"
            value={isLoading ? '...' : stats?.active_sessions || 0}
            icon={Radio}
          />
        </div>

        {/* Revenue Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StatCard
            title="Today's Revenue"
            value={isLoading ? '...' : formatCurrency(stats?.today_revenue || 0)}
            icon={DollarSign}
          />
          <StatCard
            title="This Month's Revenue"
            value={isLoading ? '...' : formatCurrency(stats?.month_revenue || 0)}
            icon={DollarSign}
          />
        </div>

        {/* Recent Clients */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Clients</CardTitle>
            <Link
              href="/provider/clients"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="animate-pulse space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-100 rounded"></div>
                ))}
              </div>
            ) : recentClients.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No clients yet.{' '}
                <Link href="/provider/clients/new" className="text-primary-600">
                  Add your first client
                </Link>
              </p>
            ) : (
              <div className="space-y-4">
                {recentClients.map((client: any) => (
                  <div
                    key={client.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{client.company_name}</p>
                      <p className="text-sm text-gray-500">{client.contact_email}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge variant="status" status={client.status}>
                        {client.status}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {formatDate(client.created_at)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
