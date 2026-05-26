'use client';

import { useEffect, useRef, useState } from 'react';
import { Image, X } from 'lucide-react';
import type { BrandConfigValues } from '@/types';

const FUENTES = ['Barlow', 'Inter', 'Montserrat', 'Roboto'] as const;

const INPUT_CLASS =
  'flex-1 rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

const SELECT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] border-[var(--color-border)]';

interface Props {
  values: BrandConfigValues;
  onChange: (v: BrandConfigValues) => void;
}

export default function BrandConfigFields({ values, onChange }: Props) {
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const logoRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!values.logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(values.logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [values.logo]);

  function handleLogoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['png', 'svg'].includes(ext)) return;
    onChange({ ...values, logo: f });
    e.target.value = '';
  }

  return (
    <div
      className="space-y-4 p-4 rounded-lg border"
      style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}
    >
      <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Configuración de marca{' '}
        <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
      </h3>

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Logo{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(PNG, SVG)</span>
        </label>
        {values.logo ? (
          <div
            className="flex items-center gap-2 px-3 py-2 rounded-lg"
            style={{ backgroundColor: 'var(--color-background)' }}
          >
            {logoPreview
              ? <img src={logoPreview} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0 rounded" />
              : <Image className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
            }
            <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>
              {values.logo.name}
            </span>
            <button
              type="button"
              onClick={() => onChange({ ...values, logo: null })}
              className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors"
              aria-label="Quitar logo"
            >
              <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => logoRef.current?.click()}
            className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5"
            style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
          >
            Subir logo
          </button>
        )}
        <input ref={logoRef} type="file" accept=".png,.svg" className="hidden" onChange={handleLogoChange} />
      </div>

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
