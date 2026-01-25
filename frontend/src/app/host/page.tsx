'use client';

import { useQuery } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import { formatCurrency, formatDuration, formatDateTime } from '@/lib/utils';
import { DollarSign, Radio, Eye, Clock } from 'lucide-react';
import Link from 'next/link';

export default function HostDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['host-dashboard'],
    queryFn: () => api.getHostDashboard(),
  });

  const host = data?.host;
  const stats = data?.stats;
  const activeSession = data?.active_session;
  const recentSessions = data?.recent_sessions || [];

  return (
    <DashboardLayout requiredRole="host">
      <div className="space-y-6">
        {/* Header with Go Live */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {host?.display_name || 'Host'}!
            </h1>
            <p className="text-gray-500">Here's your performance overview</p>
          </div>
          {activeSession ? (
            <Link href="/host/live">
              <Button variant="danger">
                <Radio className="w-4 h-4 mr-2 animate-pulse" />
                You're Live - Return to Stream
              </Button>
            </Link>
          ) : (
            <Link href="/host/live">
              <Button>
                <Radio className="w-4 h-4 mr-2" />
                Go Live
              </Button>
            </Link>
          )}
        </div>

        {/* Balance Card */}
        <Card className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-primary-100">Available Balance</p>
                <p className="text-4xl font-bold mt-2">
                  {isLoading ? '...' : formatCurrency(host?.available_balance || 0)}
                </p>
                <p className="text-primary-200 mt-2">
                  Lifetime: {formatCurrency(host?.lifetime_earnings || 0)}
                </p>
              </div>
              <Link href="/host/payouts">
                <Button
                  variant="outline"
                  className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                >
                  Request Payout
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Earnings Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Today's Earnings"
            value={isLoading ? '...' : formatCurrency(stats?.today_earnings || 0)}
            icon={DollarSign}
          />
          <StatCard
            title="This Week"
            value={isLoading ? '...' : formatCurrency(stats?.week_earnings || 0)}
            icon={DollarSign}
          />
          <StatCard
            title="This Month"
            value={isLoading ? '...' : formatCurrency(stats?.month_earnings || 0)}
            icon={DollarSign}
          />
        </div>

        {/* Performance Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StatCard
            title="Sessions This Month"
            value={isLoading ? '...' : stats?.month_sessions || 0}
            icon={Radio}
          />
          <StatCard
            title="Total Viewers This Month"
            value={isLoading ? '...' : stats?.month_viewers?.toLocaleString() || 0}
            icon={Eye}
          />
        </div>

        {/* Recent Sessions */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Sessions</CardTitle>
            <Link
              href="/host/sessions"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="animate-pulse space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded"></div>
                ))}
              </div>
            ) : recentSessions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No sessions yet.</p>
                <Link href="/host/live">
                  <Button className="mt-4">Start Your First Stream</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentSessions.map((session: any) => (
                  <Link
                    key={session.id}
                    href={`/host/sessions/${session.id}`}
                    className="block"
                  >
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{session.title}</p>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {formatDuration(session.duration_seconds)}
                          </span>
                          <span className="flex items-center">
                            <Eye className="w-4 h-4 mr-1" />
                            {session.peak_viewers} peak
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-green-600">
                          {formatCurrency(session.total_earnings)}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatDateTime(session.started_at)}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
