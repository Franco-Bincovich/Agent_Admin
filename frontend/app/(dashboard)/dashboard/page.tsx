'use client';

import { BarChart3, CheckCircle2, XCircle, CalendarDays } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useActivity } from '@/hooks/useActivity';
import { useDashboardMetrics } from '@/hooks/useDashboardMetrics';
import { MetricCard } from '@/components/features/dashboard/MetricCard';
import { DashboardMobileView } from '@/components/features/dashboard/DashboardMobileView';
import { DashboardDesktopView } from '@/components/features/dashboard/DashboardDesktopView';
import type { MetricCardProps } from '@/components/features/dashboard/MetricCard';

export default function DashboardPage() {
  const { user } = useAuth();
  const isAdmin = user?.rol === 'administrador';
  const { activity } = useActivity();
  const metrics = useDashboardMetrics(activity);

  const cards: MetricCardProps[] = [
    { label: isAdmin ? 'Total de actividad' : 'Mi actividad', value: metrics.total,   icon: BarChart3,    color: 'var(--color-primary)' },
    { label: 'Completadas',  value: metrics.listas,  icon: CheckCircle2, color: 'var(--color-success)' },
    { label: 'Con errores',  value: metrics.errores, icon: XCircle,      color: 'var(--color-error)' },
    { label: 'Este mes',     value: metrics.mes,     icon: CalendarDays, color: 'var(--color-accent)' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Dashboard
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Bienvenido, {user?.nombre}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => <MetricCard key={card.label} {...card} />)}
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Actividad reciente
        </h2>

        <DashboardMobileView recent={metrics.recent} />
        <DashboardDesktopView recent={metrics.recent} />
      </div>
    </div>
  );
}
