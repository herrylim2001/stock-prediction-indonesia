'use client';

import { useQuery } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { Users, Radio, DollarSign, Wallet, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function ClientDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['client-dashboard'],
    queryFn: () => api.getClientDashboard(),
  });

  const stats = data?.stats;
  const topHosts = data?.top_hosts || [];

  return (
    <DashboardLayout requiredRole="client">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-500">Overview of your streaming operations</p>
          </div>
          <Link href="/client/hosts/new">
            <Button>
              <Users className="w-4 h-4 mr-2" />
              Add Host
            </Button>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Active Hosts"
            value={isLoading ? '...' : stats?.active_hosts || 0}
            icon={Users}
          />
          <StatCard
            title="Live Now"
            value={isLoading ? '...' : stats?.active_sessions || 0}
            icon={Radio}
          />
          <StatCard
            title="Today's Revenue"
            value={isLoading ? '...' : formatCurrency(stats?.today_revenue || 0)}
            icon={DollarSign}
          />
          <StatCard
            title="Month Revenue"
            value={isLoading ? '...' : formatCurrency(stats?.month_revenue || 0)}
            icon={DollarSign}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pending Payouts Alert */}
          {stats?.pending_payouts_count > 0 && (
            <Card className="border-yellow-200 bg-yellow-50">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <AlertCircle className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-yellow-800">Pending Payouts</h3>
                    <p className="text-yellow-700 mt-1">
                      You have {stats?.pending_payouts_count} payout requests totaling{' '}
                      {formatCurrency(stats?.pending_payouts_amount || 0)}
                    </p>
                    <Link href="/client/payouts">
                      <Button variant="outline" size="sm" className="mt-3">
                        Review Payouts
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Top Hosts */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Top Hosts This Month</CardTitle>
              <Link
                href="/client/hosts"
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
              ) : topHosts.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No host activity this month yet.
                </p>
              ) : (
                <div className="space-y-4">
                  {topHosts.map((host: any, index: number) => (
                    <div
                      key={host.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-primary-600">
                            #{index + 1}
                          </span>
                        </div>
                        <span className="font-medium text-gray-900">
                          {host.display_name}
                        </span>
                      </div>
                      <span className="font-semibold text-green-600">
                        {formatCurrency(host.earnings)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Hosts</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {isLoading ? '...' : stats?.total_hosts || 0}
                  </p>
                </div>
                <Link href="/client/hosts">
                  <Button variant="outline" size="sm">
                    Manage Hosts
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Sessions Today</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {isLoading ? '...' : stats?.today_sessions || 0}
                  </p>
                </div>
                <Link href="/client/sessions">
                  <Button variant="outline" size="sm">
                    View Sessions
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
