'use client';

import { useRef } from 'react';
import { Image, X } from 'lucide-react';

interface Props {
  logo: File | null;
  logoPreview: string | null;
  onPick: (file: File) => void;
  onRemove: () => void;
}

export default function LogoPicker({ logo, logoPreview, onPick, onRemove }: Props) {
  const logoRef = useRef<HTMLInputElement>(null);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['png', 'jpg', 'jpeg'].includes(ext) || f.size > 2 * 1024 * 1024) return;
    onPick(f);
    e.target.value = '';
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
        Logo{' '}
        <span style={{ color: 'var(--color-text-disabled)' }}>(opcional · PNG, JPG, JPEG · máx 2MB)</span>
      </label>
      {logo ? (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-background)' }}>
          {logoPreview ? (
            <img src={logoPreview} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0 rounded" />
          ) : (
            <Image className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
          )}
          <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{logo.name}</span>
          <button type="button" onClick={onRemove} className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors" aria-label="Eliminar logo">
            <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
          </button>
        </div>
      ) : (
        <button type="button" onClick={() => logoRef.current?.click()} className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
          Subir logo
        </button>
      )}
      <input ref={logoRef} type="file" accept=".png,.jpg,.jpeg" className="hidden" onChange={handleChange} />
    </div>
  );
}
