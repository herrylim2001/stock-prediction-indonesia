'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Radio } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { UserRole } from '@/types';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
  role: z.enum(['provider', 'client', 'host']),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      role: 'provider',
    },
  });

  const selectedRole = watch('role');

  const onSubmit = async (data: LoginForm) => {
    setError('');
    setLoading(true);

    try {
      const response = await api.login(data.email, data.password, data.role);
      login(response.user, response.token);
      router.push(`/${data.role}`);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const roleOptions: { value: UserRole; label: string; description: string }[] = [
    { value: 'provider', label: 'Provider', description: 'Platform owner' },
    { value: 'client', label: 'Client', description: 'Brand operator' },
    { value: 'host', label: 'Host', description: 'Content creator' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
            <Radio className="w-7 h-7 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          Sign in to StreamLive
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Or{' '}
          <Link href="/register" className="text-primary-600 hover:text-primary-500">
            create a new account
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm rounded-xl sm:px-10 border border-gray-200">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                I am a...
              </label>
              <div className="grid grid-cols-3 gap-3">
                {roleOptions.map((option) => (
                  <label
                    key={option.value}
                    className={`
                      relative flex flex-col items-center p-3 border rounded-lg cursor-pointer
                      transition-colors
                      ${
                        selectedRole === option.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      value={option.value}
                      {...register('role')}
                      className="sr-only"
                    />
                    <span className="text-sm font-medium text-gray-900">
                      {option.label}
                    </span>
                    <span className="text-xs text-gray-500">{option.description}</span>
                  </label>
                ))}
              </div>
            </div>

            <Input
              label="Email address"
              type="email"
              {...register('email')}
              error={errors.email?.message}
              placeholder="you@example.com"
            />

            <Input
              label="Password"
              type="password"
              {...register('password')}
              error={errors.password?.message}
              placeholder="Enter your password"
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-600">Remember me</span>
              </label>
              <Link
                href="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                Forgot password?
              </Link>
            </div>

            <Button type="submit" className="w-full" loading={loading}>
              Sign in
            </Button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">
              Demo Credentials
            </p>
            <div className="space-y-1 text-xs text-gray-600">
              <p><strong>Provider:</strong> admin@streamlive.com / password123</p>
              <p><strong>Client:</strong> client@brand.com / password123</p>
              <p><strong>Host:</strong> host@talent.com / password123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
