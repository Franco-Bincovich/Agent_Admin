import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { formatDate, truncateText } from '@/utils/formatters';
import { ItemActions } from './ItemActions';
import { SkeletonCard, SkeletonRow } from './HistorySkeletons';
import { EmptyState } from './HistoryEmptyState';
import { STATUS_BADGE, TYPE_BADGE } from './historyConstants';
import type { ActivityItem } from '@/types';

interface HistoryMobileViewProps {
  activity: ActivityItem[];
  isLoading: boolean;
}

export function HistoryMobileView({ activity, isLoading }: HistoryMobileViewProps) {
  return (
    <div className="lg:hidden space-y-3">
      {isLoading ? (
        Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
      ) : activity.length === 0 ? (
        <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
          <CardContent className="py-12">
            <EmptyState />
          </CardContent>
        </Card>
      ) : (
        activity.map((item) => {
          const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
          const typeBadge = TYPE_BADGE[item.tipo];
          const label = item.titulo?.trim() || item.objetivo || '';
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
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
                  {item.tipo === 'presentacion' && item.slides_count != null && (
                    <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                      {item.slides_count} slides
                    </span>
                  )}
                </div>
                <ItemActions item={item} align="stretch" />
              </CardContent>
            </Card>
          );
        })
      )}
    </div>
  );
}
