'use client';

import { useRef, useState } from 'react';
import { Upload, X, FileText, TriangleAlert } from 'lucide-react';
import PlantillaTituloFields from './PlantillaTituloFields';

const MAX_ARCHIVOS  = 10;
const MAX_MB        = 50;
const MAX_BYTES     = MAX_MB * 1024 * 1024;
const FUENTE_ACCEPT = '.pdf,.docx,.xlsx';
const FUENTE_EXT    = ['pdf', 'docx', 'xlsx'];

function ext(f: File) {
  return f.name.split('.').pop()?.toLowerCase() ?? '';
}

interface Props {
  archivos: File[];
  onAdd: (files: File[]) => void;
  onRemove: (index: number) => void;
  plantilla: File | null;
  onSetPlantilla: (file: File | null) => void;
  logo: File | null;
  onSetLogo: (file: File | null) => void;
  titulo: string;
  onTituloChange: (value: string) => void;
}

export default function FuenteUploadSection({
  archivos, onAdd, onRemove,
  plantilla, onSetPlantilla,
  logo, onSetLogo,
  titulo, onTituloChange,
}: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function filterFuente(list: FileList | null): File[] {
    if (!list) return [];
    return Array.from(list)
      .filter((f) => FUENTE_EXT.includes(ext(f)) && f.size <= MAX_BYTES)
      .slice(0, MAX_ARCHIVOS - archivos.length);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const valid = filterFuente(e.dataTransfer.files);
    if (valid.length) onAdd(valid);
  }

  return (
    <section className="space-y-4">
      <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Documentos fuente <span style={{ color: 'var(--color-error)' }}>*</span>
      </h2>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className="rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors"
        style={{
          borderColor:     isDragging ? 'var(--color-primary)' : 'var(--color-border)',
          backgroundColor: isDragging ? 'color-mix(in srgb, var(--color-primary) 5%, transparent)' : 'transparent',
        }}
      >
        <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--color-text-disabled)' }} />
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Arrastrá archivos acá o hacé clic para seleccionar
        </p>
        <p className="text-xs mt-1" style={{ color: 'var(--color-text-disabled)' }}>
          PDF, DOCX, XLSX · Máximo {MAX_ARCHIVOS} archivos · {MAX_MB} MB por archivo
        </p>
        <input
          ref={inputRef} type="file" multiple accept={FUENTE_ACCEPT} className="hidden"
          onChange={(e) => { const v = filterFuente(e.target.files); if (v.length) onAdd(v); e.target.value = ''; }}
        />
      </div>

      {archivos.length > 5 && (
        <div className="flex items-start gap-2 rounded-lg px-3 py-2.5 text-sm" style={{ backgroundColor: 'color-mix(in srgb, #f59e0b 12%, transparent)', color: '#b45309' }}>
          <TriangleAlert className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>Tenés {archivos.length} archivos. Más de 5 puede aumentar el tiempo de procesamiento.</span>
        </div>
      )}

      {archivos.length > 0 && (
        <ul className="space-y-1.5">
          {archivos.map((file, i) => (
            <li key={`${file.name}-${i}`} className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-background)' }}>
              <FileText className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
              <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{file.name}</span>
              <button type="button" onClick={() => onRemove(i)} className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors" aria-label={`Eliminar ${file.name}`}>
                <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
              </button>
            </li>
          ))}
        </ul>
      )}

      <PlantillaTituloFields
        plantilla={plantilla}
        onSetPlantilla={onSetPlantilla}
        logo={logo}
        onSetLogo={onSetLogo}
        titulo={titulo}
        onTituloChange={onTituloChange}
      />
    </section>
  );
}
