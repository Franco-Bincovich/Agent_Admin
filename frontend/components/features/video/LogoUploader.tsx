'use client';

import { useRef } from 'react';
import { Image, X } from 'lucide-react';

interface Props {
  value: File | null;
  onChange: (f: File | null) => void;
  preview: string | null;
}

export default function LogoUploader({ value, onChange, preview }: Props) {
  const logoRef = useRef<HTMLInputElement>(null);

  function handleLogoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['png', 'svg'].includes(ext)) return;
    onChange(f);
    e.target.value = '';
  }

  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
        Logo{' '}
        <span style={{ color: 'var(--color-text-disabled)' }}>(PNG, SVG)</span>
      </label>
      {value ? (
        <div
          className="flex items-center gap-2 px-3 py-2 rounded-lg"
          style={{ backgroundColor: 'var(--color-background)' }}
        >
          {preview
            ? <img src={preview} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0 rounded" />
            : <Image className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
          }
          <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>
            {value.name}
          </span>
          <button
            type="button"
            onClick={() => onChange(null)}
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
  );
}
