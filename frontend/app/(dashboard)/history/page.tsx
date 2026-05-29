'use client';

import { useActivity } from '@/hooks/useActivity';
import { HistoryMobileView } from '@/components/features/history/HistoryMobileView';
import { HistoryDesktopView } from '@/components/features/history/HistoryDesktopView';

export default function HistoryPage() {
  const { activity, isLoading } = useActivity();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Historial
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Todas tus presentaciones y documentos generados
        </p>
      </div>

      <HistoryMobileView activity={activity} isLoading={isLoading} />
      <HistoryDesktopView activity={activity} isLoading={isLoading} />
    </div>
  );
}
