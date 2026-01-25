'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { api } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Plus, Search, MoreVertical, CheckCircle, XCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Client } from '@/types';

const createClientSchema = z.object({
  company_name: z.string().min(1, 'Company name is required'),
  contact_name: z.string().min(1, 'Contact name is required'),
  contact_email: z.string().email('Invalid email'),
  contact_phone: z.string().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  revenue_share_percent: z.number().min(0).max(100).default(70),
});

type CreateClientForm = z.infer<typeof createClientSchema>;

export default function ClientsPage() {
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['clients', search],
    queryFn: () => api.getClients({ search }),
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateClientForm) => api.createClient(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      setIsModalOpen(false);
      reset();
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: string) => api.activateClient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });

  const suspendMutation = useMutation({
    mutationFn: (id: string) => api.suspendClient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateClientForm>({
    resolver: zodResolver(createClientSchema),
    defaultValues: {
      revenue_share_percent: 70,
    },
  });

  const onSubmit = (data: CreateClientForm) => {
    createMutation.mutate(data);
  };

  const clients: Client[] = data?.clients || [];

  return (
    <DashboardLayout requiredRole="provider">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
            <p className="text-gray-500">Manage your platform clients</p>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Client
          </Button>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search clients..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              </div>
            ) : clients.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No clients found. Add your first client to get started.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Company</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Revenue Share</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {clients.map((client) => (
                    <TableRow key={client.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium text-gray-900">{client.company_name}</p>
                          <p className="text-sm text-gray-500">{client.contact_email}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-gray-900">{client.contact_name}</p>
                          <p className="text-sm text-gray-500">{client.contact_phone || '-'}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{client.revenue_share_percent}%</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="status" status={client.status}>
                          {client.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-500">
                        {formatDate(client.created_at)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {client.status === 'pending' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => activateMutation.mutate(client.id)}
                              loading={activateMutation.isPending}
                            >
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            </Button>
                          )}
                          {client.status === 'active' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => suspendMutation.mutate(client.id)}
                              loading={suspendMutation.isPending}
                            >
                              <XCircle className="w-4 h-4 text-red-600" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create Client Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add New Client"
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Company Name"
            {...register('company_name')}
            error={errors.company_name?.message}
          />
          <Input
            label="Contact Name"
            {...register('contact_name')}
            error={errors.contact_name?.message}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Contact Email"
              type="email"
              {...register('contact_email')}
              error={errors.contact_email?.message}
            />
            <Input
              label="Contact Phone"
              {...register('contact_phone')}
            />
          </div>
          <Input
            label="Password"
            type="password"
            {...register('password')}
            error={errors.password?.message}
          />
          <Input
            label="Revenue Share (%)"
            type="number"
            {...register('revenue_share_percent', { valueAsNumber: true })}
            error={errors.revenue_share_percent?.message}
            helperText="Percentage of revenue the client keeps"
          />
          <div className="flex justify-end space-x-3 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={createMutation.isPending}>
              Create Client
            </Button>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
