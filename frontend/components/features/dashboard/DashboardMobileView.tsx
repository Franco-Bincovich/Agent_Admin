import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { formatDate, truncateText } from '@/utils/formatters';
import { STATUS_BADGE, TEMPLATE_LABELS, TYPE_BADGE } from '@/components/features/history/historyConstants';
import type { ActivityItem } from '@/types';

interface DashboardMobileViewProps {
  recent: ActivityItem[];
}

export function DashboardMobileView({ recent }: DashboardMobileViewProps) {
  return (
    <div className="lg:hidden space-y-3">
      {recent.length === 0 ? (
        <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
          <CardContent className="py-8 text-center text-sm" style={{ color: 'var(--color-text-disabled)' }}>
            No hay actividad reciente todavía.
          </CardContent>
        </Card>
      ) : (
        recent.map((item) => {
          const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
          const typeBadge = TYPE_BADGE[item.tipo];
          const label = item.objetivo ?? item.titulo ?? '';
          return (
            <Card
              key={item.id}
              style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
            >
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className={typeBadge.className}>{typeBadge.label}</Badge>
                  <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                    {formatDate(item.creado_en)}
                  </span>
                </div>
                <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {truncateText(label, 60)}
                </p>
                <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
              </CardContent>
            </Card>
          );
        })
      )}
    </div>
  );
}
