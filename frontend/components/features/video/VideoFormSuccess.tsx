'use client';

import { CheckCircle } from 'lucide-react';
import type { VideoJob } from '@/types';

interface Props {
  job: VideoJob;
  onReset: () => void;
}

export default function VideoFormSuccess({ job, onReset }: Props) {
  return (
    <div className="flex flex-col items-center gap-4 py-10 text-center">
      <CheckCircle className="w-12 h-12" style={{ color: 'var(--color-primary)' }} />
      <div className="space-y-1">
        <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Tu video está en cola
        </h2>
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          Job ID:{' '}
          <span className="font-mono text-xs" style={{ color: 'var(--color-text-primary)' }}>
            {job.id}
          </span>
        </p>
      </div>
      <button
        type="button"
        onClick={onReset}
        className="text-sm underline underline-offset-2"
        style={{ color: 'var(--color-primary)' }}
      >
        Crear otro job
      </button>
    </div>
  );
}
