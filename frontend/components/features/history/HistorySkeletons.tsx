import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableRow } from '@/components/ui/table';

export function SkeletonRow() {
  return (
    <TableRow>
      {Array.from({ length: 7 }).map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 w-full rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        </TableCell>
      ))}
    </TableRow>
  );
}

export function SkeletonCard() {
  return (
    <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <CardContent className="p-4 space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-4 w-full rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        ))}
      </CardContent>
    </Card>
  );
}
