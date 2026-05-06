'use client';

import { useRef } from 'react';
import { FileText, X } from 'lucide-react';

interface Props {
  plantilla: File | null;
  onSetPlantilla: (file: File | null) => void;
  titulo: string;
  onTituloChange: (value: string) => void;
}

export default function PlantillaTituloFields({
  plantilla, onSetPlantilla, titulo, onTituloChange,
}: Props) {
  const ref = useRef<HTMLInputElement>(null);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f || f.name.split('.').pop()?.toLowerCase() !== 'docx') return;
    onSetPlantilla(f);
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
          <button type="button" onClick={() => ref.current?.click()} className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
            Subir plantilla DOCX
          </button>
        )}
        <input ref={ref} type="file" accept=".docx" className="hidden" onChange={handleChange} />
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
