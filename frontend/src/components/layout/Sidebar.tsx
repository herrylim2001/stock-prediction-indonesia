'use client';

import { cn } from '@/lib/utils';
import { useAuthStore, useUIStore } from '@/lib/store';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Building2,
  Gift,
  DollarSign,
  BarChart3,
  Settings,
  Video,
  Wallet,
  User,
  Radio,
  CreditCard,
  Menu,
  X,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const providerNav: NavItem[] = [
  { label: 'Dashboard', href: '/provider', icon: <LayoutDashboard className="w-5 h-5" /> },
  { label: 'Clients', href: '/provider/clients', icon: <Building2 className="w-5 h-5" /> },
  { label: 'Gift Catalog', href: '/provider/gifts', icon: <Gift className="w-5 h-5" /> },
  { label: 'Revenue', href: '/provider/revenue', icon: <DollarSign className="w-5 h-5" /> },
  { label: 'Analytics', href: '/provider/analytics', icon: <BarChart3 className="w-5 h-5" /> },
  { label: 'Settings', href: '/provider/settings', icon: <Settings className="w-5 h-5" /> },
];

const clientNav: NavItem[] = [
  { label: 'Dashboard', href: '/client', icon: <LayoutDashboard className="w-5 h-5" /> },
  { label: 'Hosts', href: '/client/hosts', icon: <Users className="w-5 h-5" /> },
  { label: 'Live Sessions', href: '/client/sessions', icon: <Video className="w-5 h-5" /> },
  { label: 'Payouts', href: '/client/payouts', icon: <Wallet className="w-5 h-5" /> },
  { label: 'Gifts', href: '/client/gifts', icon: <Gift className="w-5 h-5" /> },
  { label: 'Analytics', href: '/client/analytics', icon: <BarChart3 className="w-5 h-5" /> },
  { label: 'Settings', href: '/client/settings', icon: <Settings className="w-5 h-5" /> },
];

const hostNav: NavItem[] = [
  { label: 'Dashboard', href: '/host', icon: <LayoutDashboard className="w-5 h-5" /> },
  { label: 'Go Live', href: '/host/live', icon: <Radio className="w-5 h-5" /> },
  { label: 'My Sessions', href: '/host/sessions', icon: <Video className="w-5 h-5" /> },
  { label: 'Earnings', href: '/host/earnings', icon: <DollarSign className="w-5 h-5" /> },
  { label: 'Payouts', href: '/host/payouts', icon: <CreditCard className="w-5 h-5" /> },
  { label: 'Profile', href: '/host/profile', icon: <User className="w-5 h-5" /> },
];

export function Sidebar() {
  const { user } = useAuthStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const pathname = usePathname();

  const navItems = user?.role === 'provider' ? providerNav : user?.role === 'client' ? clientNav : hostNav;

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-30 h-full w-64 bg-white border-r border-gray-200',
          'transform transition-transform duration-200 ease-in-out',
          'lg:translate-x-0 lg:static',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Radio className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900">StreamLive</span>
          </Link>
          <button
            className="lg:hidden p-1 rounded-lg hover:bg-gray-100"
            onClick={toggleSidebar}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-colors',
                pathname === item.href
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.name || user?.display_name || user?.email}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
