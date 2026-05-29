import type { ActivityItem } from '@/types';

interface DashboardMetrics {
  total: number;
  listas: number;
  errores: number;
  mes: number;
  recent: ActivityItem[];
}

export function useDashboardMetrics(activity: ActivityItem[]): DashboardMetrics {
  const now = new Date();

  const metrics = {
    total: activity.length,
    listas: activity.filter((a) => a.estado === 'listo').length,
    errores: activity.filter((a) => a.estado === 'error').length,
    mes: activity.filter((a) => {
      const d = new Date(a.creado_en);
      return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    }).length,
    recent: activity.slice(0, 5),
  };

  return metrics;
}
