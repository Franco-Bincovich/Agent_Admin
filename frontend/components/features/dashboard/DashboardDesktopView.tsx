import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { formatDate, truncateText } from '@/utils/formatters';
import { STATUS_BADGE, TEMPLATE_LABELS, TYPE_BADGE } from '@/components/features/history/historyConstants';
import type { ActivityItem } from '@/types';

interface DashboardDesktopViewProps {
  recent: ActivityItem[];
}

export function DashboardDesktopView({ recent }: DashboardDesktopViewProps) {
  return (
    <div className="hidden lg:block rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
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
            recent.map((item) => {
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
                    {TEMPLATE_LABELS[item.parametros?.template ?? ''] ?? '—'}
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
  );
}
