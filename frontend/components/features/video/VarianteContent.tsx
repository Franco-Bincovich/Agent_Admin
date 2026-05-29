'use client';

import type { EstiloEdicion, FormatoSalida, PosicionSubtitulos, ResolucionVideo } from '@/types';
import type { VarianteValues } from './VarianteConfig';

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

interface Props {
  data: VarianteValues;
  onChange: (data: VarianteValues) => void;
}

export default function VarianteContent({ data, onChange }: Props) {
  return (
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
  );
}
