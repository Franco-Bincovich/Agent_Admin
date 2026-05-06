'use client';

import { useRef, useState } from 'react';
import { Upload, X, FileText } from 'lucide-react';

const ACCEPTED_EXT = ['pdf', 'docx', 'txt', 'xlsx'];
const MAX_FILES = 10;

interface Props {
  files: File[];
  onAdd: (files: File[]) => void;
  onRemove: (index: number) => void;
}

export default function FileUploadArea({ files, onAdd, onRemove }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function filterFiles(list: FileList | null): File[] {
    if (!list) return [];
    return Array.from(list)
      .filter((f) => ACCEPTED_EXT.includes(f.name.split('.').pop()?.toLowerCase() ?? ''))
      .slice(0, MAX_FILES - files.length);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const valid = filterFiles(e.dataTransfer.files);
    if (valid.length) onAdd(valid);
  }

  return (
    <div className="space-y-3">
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
          borderColor: isDragging ? 'var(--color-primary)' : 'var(--color-border)',
          backgroundColor: isDragging ? 'color-mix(in srgb, var(--color-primary) 5%, transparent)' : 'transparent',
        }}
      >
        <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--color-text-disabled)' }} />
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Arrastrá archivos acá o hacé clic para seleccionar
        </p>
        <p className="text-xs mt-1" style={{ color: 'var(--color-text-disabled)' }}>
          PDF, DOCX, TXT, XLSX · Máximo {MAX_FILES} archivos
        </p>
        <input
          ref={inputRef} type="file" multiple accept=".pdf,.docx,.txt,.xlsx"
          className="hidden"
          onChange={(e) => { const v = filterFiles(e.target.files); if (v.length) onAdd(v); }}
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-1.5">
          {files.map((file, i) => (
            <li
              key={`${file.name}-${i}`}
              className="flex items-center gap-2 px-3 py-2 rounded-lg"
              style={{ backgroundColor: 'var(--color-surface)' }}
            >
              <FileText className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
              <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{file.name}</span>
              <button
                type="button"
                onClick={() => onRemove(i)}
                className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors"
                aria-label={`Eliminar ${file.name}`}
              >
                <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
