'use client';

import type { BrandConfigValues } from '@/types';

const INPUT_CLASS =
  'flex-1 rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

interface Props {
  values: BrandConfigValues;
  onChange: (v: BrandConfigValues) => void;
}

export default function BrandColorsPanel({ values, onChange }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Color primario
        </label>
        <div className="flex items-center gap-2">
          <input
            type="color"
            value={values.colorPrimario || '#000000'}
            onChange={(e) => onChange({ ...values, colorPrimario: e.target.value })}
            className="h-9 w-9 rounded-lg cursor-pointer border flex-shrink-0"
            style={{ borderColor: 'var(--color-border)' }}
          />
          <input
            type="text"
            value={values.colorPrimario}
            onChange={(e) => onChange({ ...values, colorPrimario: e.target.value })}
            placeholder="#1E40AF"
            maxLength={7}
            className={INPUT_CLASS}
          />
        </div>
      </div>
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Color secundario
        </label>
        <div className="flex items-center gap-2">
          <input
            type="color"
            value={values.colorSecundario || '#000000'}
            onChange={(e) => onChange({ ...values, colorSecundario: e.target.value })}
            className="h-9 w-9 rounded-lg cursor-pointer border flex-shrink-0"
            style={{ borderColor: 'var(--color-border)' }}
          />
          <input
            type="text"
            value={values.colorSecundario}
            onChange={(e) => onChange({ ...values, colorSecundario: e.target.value })}
            placeholder="#4FC3F7"
            maxLength={7}
            className={INPUT_CLASS}
          />
        </div>
      </div>
    </div>
  );
}
