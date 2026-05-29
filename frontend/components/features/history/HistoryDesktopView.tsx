import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { formatDate, truncateText } from '@/utils/formatters';
import { ItemActions } from './ItemActions';
import { SkeletonRow } from './HistorySkeletons';
import { EmptyState } from './HistoryEmptyState';
import { STATUS_BADGE, TEMPLATE_LABELS, TYPE_BADGE } from './historyConstants';
import type { ActivityItem } from '@/types';

interface HistoryDesktopViewProps {
  activity: ActivityItem[];
  isLoading: boolean;
}

export function HistoryDesktopView({ activity, isLoading }: HistoryDesktopViewProps) {
  return (
    <div className="hidden lg:block rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
      <Table>
        <TableHeader>
          <TableRow style={{ borderColor: 'var(--color-border)' }}>
            <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Tipo</TableHead>
            <TableHead className="w-[30%]"      style={{ color: 'var(--color-text-secondary)' }}>Objetivo</TableHead>
            <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Template</TableHead>
            <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Estado</TableHead>
            <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Slides</TableHead>
            <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Fecha</TableHead>
            <TableHead className="text-right"   style={{ color: 'var(--color-text-secondary)' }}>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
          ) : activity.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="py-16">
                <EmptyState />
              </TableCell>
            </TableRow>
          ) : (
            activity.map((item) => {
              const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
              const typeBadge = TYPE_BADGE[item.tipo];
              const label = item.titulo?.trim() || item.objetivo || '';
              return (
                <TableRow key={item.id} style={{ borderColor: 'var(--color-border)' }}>
                  <TableCell>
                    <Badge variant="outline" className={typeBadge.className}>{typeBadge.label}</Badge>
                  </TableCell>
                  <TableCell style={{ color: 'var(--color-text-primary)' }}>
                    {truncateText(label, 45)}
                  </TableCell>
                  <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                    {TEMPLATE_LABELS[item.parametros?.template ?? ''] ?? '—'}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
                  </TableCell>
                  <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                    {item.tipo === 'presentacion' ? (item.slides_count ?? '—') : '—'}
                  </TableCell>
                  <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                    {formatDate(item.creado_en)}
                  </TableCell>
                  <TableCell className="text-right">
                    <ItemActions item={item} align="end" />
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
