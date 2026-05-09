'use client';

import { useEffect, useRef, useState } from 'react';
import { FileText, Image, X } from 'lucide-react';

const LOGO_ACCEPT = '.png,.jpg,.jpeg';
const LOGO_EXTS   = ['png', 'jpg', 'jpeg'];
const LOGO_MAX_MB = 2;
const LOGO_MAX_BYTES = LOGO_MAX_MB * 1024 * 1024;

interface Props {
  plantilla: File | null;
  onSetPlantilla: (file: File | null) => void;
  titulo: string;
  onTituloChange: (value: string) => void;
  logo: File | null;
  onSetLogo: (file: File | null) => void;
}

export default function PlantillaTituloFields({
  plantilla, onSetPlantilla, titulo, onTituloChange, logo, onSetLogo,
}: Props) {
  const plantillaRef = useRef<HTMLInputElement>(null);
  const logoRef      = useRef<HTMLInputElement>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [logo]);

  function handlePlantillaChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f || f.name.split('.').pop()?.toLowerCase() !== 'docx') return;
    onSetPlantilla(f);
    e.target.value = '';
  }

  function handleLogoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!LOGO_EXTS.includes(ext) || f.size > LOGO_MAX_BYTES) return;
    onSetLogo(f);
    e.target.value = '';
  }

  return (
    <>
      <div className="space-y-2">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Plantilla{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional · solo DOCX)</span>
        </label>
        {plantilla ? (
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-background)' }}>
            <FileText className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
            <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{plantilla.name}</span>
            <button type="button" onClick={() => onSetPlantilla(null)} className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors" aria-label="Eliminar plantilla">
              <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => plantillaRef.current?.click()} className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
            Subir plantilla DOCX
          </button>
        )}
        <input ref={plantillaRef} type="file" accept=".docx" className="hidden" onChange={handlePlantillaChange} />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Logo{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional · PNG, JPG, JPEG · máx {LOGO_MAX_MB}MB)</span>
        </label>
        {logo ? (
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-background)' }}>
            {logoPreview ? (
              <img src={logoPreview} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0 rounded" />
            ) : (
              <Image className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
            )}
            <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{logo.name}</span>
            <button type="button" onClick={() => onSetLogo(null)} className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors" aria-label="Eliminar logo">
              <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => logoRef.current?.click()} className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
            Subir logo
          </button>
        )}
        <input ref={logoRef} type="file" accept={LOGO_ACCEPT} className="hidden" onChange={handleLogoChange} />
      </div>

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Título del documento <span style={{ color: 'var(--color-error)' }}>*</span>
        </label>
        <input
          type="text"
          value={titulo}
          onChange={(e) => onTituloChange(e.target.value)}
          placeholder="Ej: Informe de resultados Q1 2025"
          className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          style={{ backgroundColor: 'var(--color-background)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
        />
        {titulo.length > 0 && titulo.trim().length < 3 && (
          <p className="text-xs" style={{ color: 'var(--color-error)' }}>
            El título debe tener al menos 3 caracteres.
          </p>
        )}
      </div>
    </>
  );
}
