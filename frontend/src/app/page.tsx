'use client';

import { useAuthStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Radio, ArrowRight, Users, Building2, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function Home() {
  const { isAuthenticated, user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated && user) {
      router.push(`/${user.role}`);
    }
  }, [isAuthenticated, user, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <Radio className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">StreamLive</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Whitelabel Live Streaming Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Launch your own branded live streaming service. Manage hosts, track earnings,
          and monetize with virtual gifts - all under your brand.
        </p>
        <div className="flex items-center justify-center space-x-4">
          <Link href="/register">
            <Button size="lg">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">
              View Demo
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Built for Scale
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <Building2 className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Multi-tenant Platform
            </h3>
            <p className="text-gray-600">
              Onboard multiple brands with isolated environments. Each client gets
              their own branded experience.
            </p>
          </div>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Host Management
            </h3>
            <p className="text-gray-600">
              Complete tools for managing hosts, tracking performance, and
              processing payouts automatically.
            </p>
          </div>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Real-time Monetization
            </h3>
            <p className="text-gray-600">
              Virtual gifts, automatic revenue splitting, and transparent
              earnings tracking for all parties.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="container mx-auto px-4 text-center text-gray-500">
          <p>&copy; 2024 StreamLive. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
