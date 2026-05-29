import { Card, CardContent } from '@/components/ui/card';

interface MetricCardProps {
  label: string;
  value: number;
  icon: React.ElementType;
  color: string;
}

export function MetricCard({ label, value, icon: Icon, color }: MetricCardProps) {
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

export type { MetricCardProps };
