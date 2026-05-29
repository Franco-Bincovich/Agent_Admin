'use client';

import { useEffect, useState } from 'react';
import type { BrandConfigValues } from '@/types';
import LogoUploader from './LogoUploader';
import BrandColorsPanel from './BrandColorsPanel';

const FUENTES = ['Barlow', 'Inter', 'Montserrat', 'Roboto'] as const;

const SELECT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] border-[var(--color-border)]';

interface Props {
  values: BrandConfigValues;
  onChange: (v: BrandConfigValues) => void;
}

export default function BrandConfigFields({ values, onChange }: Props) {
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!values.logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(values.logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [values.logo]);

  return (
    <div
      className="space-y-4 p-4 rounded-lg border"
      style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}
    >
      <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Configuración de marca{' '}
        <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
      </h3>

      <LogoUploader
        value={values.logo}
        onChange={(logo) => onChange({ ...values, logo })}
        preview={logoPreview}
      />

      <BrandColorsPanel
        values={values}
        onChange={onChange}
      />

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Fuente tipográfica
        </label>
        <select
          value={values.fuente}
          onChange={(e) => onChange({ ...values, fuente: e.target.value })}
          className={SELECT_CLASS}
        >
          <option value="">Sin especificar</option>
          {FUENTES.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>
    </div>
  );
}
