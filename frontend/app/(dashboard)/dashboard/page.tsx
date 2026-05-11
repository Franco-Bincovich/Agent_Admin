'use client';

import { BarChart3, CheckCircle2, XCircle, CalendarDays } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { useAuth } from '@/hooks/useAuth';
import { useActivity } from '@/hooks/useActivity';
import { formatDate, truncateText } from '@/utils/formatters';
import type { ActivityItem } from '@/types';

interface MetricCardProps {
  label: string;
  value: number;
  icon: React.ElementType;
  color: string;
}

function MetricCard({ label, value, icon: Icon, color }: MetricCardProps) {
  return (
    <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <CardContent className="flex items-center gap-4 p-5">
        <div
          className="rounded-lg p-2.5 flex-shrink-0"
          style={{ backgroundColor: 'color-mix(in srgb, var(--color-primary) 10%, transparent)' }}
        >
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        <div>
          <p className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>{value}</p>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

const STATUS_BADGE: Record<string, { label: string; className: string }> = {
  procesando: { label: 'Procesando...', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  listo:      { label: 'Listo',         className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  error:      { label: 'Error',         className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

const TYPE_BADGE: Record<ActivityItem['tipo'], { label: string; className: string }> = {
  presentacion: { label: 'Presentación', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  documento:    { label: 'Documento',    className: 'bg-green-500/20 text-green-400 border-green-500/30' },
};

export default function DashboardPage() {
  const { user } = useAuth();
  const isAdmin = user?.rol === 'administrador';
  const { activity } = useActivity();

  const now = new Date();
  const metrics = {
    total:   activity.length,
    listas:  activity.filter((a) => a.estado === 'listo').length,
    errores: activity.filter((a) => a.estado === 'error').length,
    mes:     activity.filter((a) => {
      const d = new Date(a.creado_en);
      return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    }).length,
  };
  const recent = activity;

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

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => <MetricCard key={card.label} {...card} />)}
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Actividad reciente
        </h2>
        <div className="rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
          <Table>
            <TableHeader>
              <TableRow style={{ borderColor: 'var(--color-border)' }}>
                {['Tipo', 'Objetivo', 'Template', 'Estado', 'Fecha'].map((h) => (
                  <TableHead key={h} style={{ color: 'var(--color-text-secondary)' }}>{h}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {recent.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-10" style={{ color: 'var(--color-text-disabled)' }}>
                    No hay actividad reciente todavía.
                  </TableCell>
                </TableRow>
              ) : (
                recent.slice(0, 5).map((item) => {
                  const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
                  const typeBadge = TYPE_BADGE[item.tipo];
                  const label = item.objetivo ?? item.titulo ?? '';
                  return (
                    <TableRow key={item.id} style={{ borderColor: 'var(--color-border)' }}>
                      <TableCell>
                        <Badge variant="outline" className={typeBadge.className}>{typeBadge.label}</Badge>
                      </TableCell>
                      <TableCell style={{ color: 'var(--color-text-primary)' }}>
                        {truncateText(label, 50)}
                      </TableCell>
                      <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                        —
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
                      </TableCell>
                      <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                        {formatDate(item.creado_en)}
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
