'use client';

import { useRef, useState } from 'react';
import { Upload, X, Video } from 'lucide-react';

const ACCEPTED_EXT = ['mp4', 'mov', 'avi'];
const MAX_BYTES = 2 * 1024 * 1024 * 1024;

interface Props {
  file: File | null;
  onSelect: (file: File) => void;
  onRemove: () => void;
}

function formatBytes(bytes: number): string {
  if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
  if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
  return `${(bytes / 1e3).toFixed(0)} KB`;
}

export default function VideoUploadArea({ file, onSelect, onRemove }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function pickFile(f: File) {
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!ACCEPTED_EXT.includes(ext) || f.size > MAX_BYTES) return;
    onSelect(f);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) pickFile(f);
  }

  if (file) {
    return (
      <div
        className="flex items-center gap-3 px-4 py-3 rounded-lg border"
        style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
      >
        <Video className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--color-primary)' }} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
            {file.name}
          </p>
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            {formatBytes(file.size)}
          </p>
        </div>
        <button
          type="button"
          onClick={onRemove}
          className="flex-shrink-0 p-1 rounded hover:bg-red-500/10 transition-colors"
          aria-label="Quitar video"
        >
          <X className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
        </button>
      </div>
    );
  }

  return (
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
        backgroundColor: isDragging
          ? 'color-mix(in srgb, var(--color-primary) 5%, transparent)'
          : 'transparent',
      }}
    >
      <Upload className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--color-text-disabled)' }} />
      <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
        Arrastrá tu video acá o hacé clic para seleccionar
      </p>
      <p className="text-xs mt-1" style={{ color: 'var(--color-text-disabled)' }}>
        MP4, MOV, AVI · Máximo 2 GB
      </p>
      <input
        ref={inputRef}
        type="file"
        accept=".mp4,.mov,.avi"
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) pickFile(f); e.target.value = ''; }}
      />
    </div>
  );
}
