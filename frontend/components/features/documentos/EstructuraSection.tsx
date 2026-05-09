'use client';

import type { DocumentoSeccion } from '@/types';

const SECCIONES: DocumentoSeccion[] = [
  'Resumen ejecutivo',
  'Introducción',
  'Contexto',
  'Objetivos',
  'Desarrollo',
  'Conclusiones',
  'Recomendaciones',
];

interface Props {
  secciones: DocumentoSeccion[];
  onToggleSeccion: (s: DocumentoSeccion) => void;
  indicaciones: string;
  onIndicacionesChange: (value: string) => void;
}

export default function EstructuraSection({
  secciones, onToggleSeccion, indicaciones, onIndicacionesChange,
}: Props) {
  return (
    <section className="space-y-4">
      <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Estructura{' '}
        <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
      </h2>

      <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
        Si no seleccionás ninguna sección, el documento se generará con: Introducción, Antecedentes y Contexto, Desarrollo, Conclusiones y Próximos Pasos.
      </p>

      <div className="flex flex-wrap gap-2">
        {SECCIONES.map((s) => {
          const selected = secciones.includes(s);
          return (
            <button
              key={s}
              type="button"
              onClick={() => onToggleSeccion(s)}
              className="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors"
              style={{
                backgroundColor: selected
                  ? 'color-mix(in srgb, var(--color-primary) 15%, transparent)'
                  : 'var(--color-surface)',
                borderColor: selected ? 'var(--color-primary)' : 'var(--color-border)',
                color:       selected ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              }}
            >
              {s}
            </button>
          );
        })}
      </div>

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Indicaciones adicionales{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
        </label>
        <textarea
          value={indicaciones}
          onChange={(e) => onIndicacionesChange(e.target.value.slice(0, 1000))}
          placeholder="Instrucciones especiales, tono deseado, secciones a priorizar..."
          rows={3}
          maxLength={1000}
          className="w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          style={{
            backgroundColor: 'var(--color-background)',
            borderColor:     'var(--color-border)',
            color:           'var(--color-text-primary)',
          }}
        />
        <p className="text-xs text-right" style={{ color: 'var(--color-text-disabled)' }}>
          {indicaciones.length}/1000
        </p>
      </div>
    </section>
  );
}
