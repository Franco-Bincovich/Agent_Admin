'use client';

import { ChevronDown, ChevronUp, X } from 'lucide-react';
import type { VarianteValues } from './VarianteConfig';

interface Props {
  index: number;
  data: VarianteValues;
  isOpen: boolean;
  onToggle: () => void;
  onRemove: () => void;
}

export default function VarianteHeader({ index, data, isOpen, onToggle, onRemove }: Props) {
  const isComplete = data.estilo && data.formato && data.posicion_subtitulos && data.resolucion;

  return (
    <div
      className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
      style={{ backgroundColor: 'var(--color-surface)' }}
      onClick={onToggle}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Variante {index + 1}
        </span>
        {!isComplete && (
          <span
            className="text-xs px-1.5 py-0.5 rounded"
            style={{
              backgroundColor: 'color-mix(in srgb, #F59E0B 15%, transparent)',
              color: '#F59E0B',
            }}
          >
            Incompleta
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onRemove(); }}
          className="p-1 rounded hover:bg-red-500/10 transition-colors"
          aria-label="Eliminar variante"
        >
          <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
        </button>
        {isOpen
          ? <ChevronUp className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          : <ChevronDown className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
        }
      </div>
    </div>
  );
}
