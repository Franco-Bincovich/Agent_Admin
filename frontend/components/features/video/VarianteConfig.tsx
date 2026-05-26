'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import type { EstiloEdicion, FormatoSalida, PosicionSubtitulos, ResolucionVideo } from '@/types';

export interface VarianteValues {
  estilo: EstiloEdicion | null;
  formato: FormatoSalida | null;
  posicion_subtitulos: PosicionSubtitulos | null;
  resolucion: ResolucionVideo | null;
}

interface Props {
  index: number;
  data: VarianteValues;
  onChange: (data: VarianteValues) => void;
  onRemove: () => void;
}

function OptionCard({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="px-3 py-2 rounded-lg border text-sm transition-colors"
      style={{
        borderColor: selected ? 'var(--color-primary)' : 'var(--color-border)',
        backgroundColor: selected
          ? 'color-mix(in srgb, var(--color-primary) 12%, transparent)'
          : 'transparent',
        color: selected ? 'var(--color-primary)' : 'var(--color-text-secondary)',
      }}
    >
      {label}
    </button>
  );
}

const ESTILOS: [EstiloEdicion, string][] = [
  ['dinamico', 'Dinámico'],
  ['corporativo', 'Corporativo'],
  ['minimalista', 'Minimalista'],
];

const FORMATOS: [FormatoSalida, string][] = [
  ['horizontal_16_9', '16:9'],
  ['vertical_9_16', '9:16'],
  ['cuadrado_1_1', '1:1'],
];

const POSICIONES: [PosicionSubtitulos, string][] = [
  ['abajo', 'Abajo'],
  ['centro', 'Centro'],
  ['arriba', 'Arriba'],
  ['sin_subtitulos', 'Sin subtítulos'],
];

const RESOLUCIONES: [ResolucionVideo, string][] = [
  ['hd_720p', '720p'],
  ['full_hd_1080p', '1080p'],
  ['ultra_hd_4k', '4K'],
];

export default function VarianteConfig({ index, data, onChange, onRemove }: Props) {
  const [isOpen, setIsOpen] = useState(true);
  const isComplete = data.estilo && data.formato && data.posicion_subtitulos && data.resolucion;

  return (
    <div className="rounded-lg border overflow-hidden" style={{ borderColor: 'var(--color-border)' }}>
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
        style={{ backgroundColor: 'var(--color-surface)' }}
        onClick={() => setIsOpen((o) => !o)}
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

      {isOpen && (
        <div
          className="px-4 pb-4 pt-3 space-y-4"
          style={{ borderTop: '1px solid var(--color-border)' }}
        >
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--color-text-disabled)' }}>
              Estilo
            </p>
            <div className="flex flex-wrap gap-2">
              {ESTILOS.map(([v, l]) => (
                <OptionCard key={v} label={l} selected={data.estilo === v} onClick={() => onChange({ ...data, estilo: v })} />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--color-text-disabled)' }}>
              Formato
            </p>
            <div className="flex flex-wrap gap-2">
              {FORMATOS.map(([v, l]) => (
                <OptionCard key={v} label={l} selected={data.formato === v} onClick={() => onChange({ ...data, formato: v })} />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--color-text-disabled)' }}>
              Subtítulos
            </p>
            <div className="flex flex-wrap gap-2">
              {POSICIONES.map(([v, l]) => (
                <OptionCard key={v} label={l} selected={data.posicion_subtitulos === v} onClick={() => onChange({ ...data, posicion_subtitulos: v })} />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--color-text-disabled)' }}>
              Resolución
            </p>
            <div className="flex flex-wrap gap-2">
              {RESOLUCIONES.map(([v, l]) => (
                <OptionCard key={v} label={l} selected={data.resolucion === v} onClick={() => onChange({ ...data, resolucion: v })} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
