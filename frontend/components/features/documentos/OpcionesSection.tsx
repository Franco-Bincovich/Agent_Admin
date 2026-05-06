'use client';

import type { DocumentoOpciones } from '@/types';

const TOGGLES: [keyof DocumentoOpciones, string][] = [
  ['homogeneizar',  'Homogeneizar tono y estilo'],
  ['deduplicar',    'Eliminar información duplicada'],
  ['usar_imagenes', 'Incluir imágenes de los documentos'],
];

interface Props {
  opciones: DocumentoOpciones;
  onToggleOpcion: (key: keyof DocumentoOpciones) => void;
}

export default function OpcionesSection({ opciones, onToggleOpcion }: Props) {
  return (
    <section className="space-y-4">
      <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Opciones
      </h2>

      <div className="space-y-3">
        {TOGGLES.map(([key, label]) => (
          <label key={key} className="flex items-center gap-3 cursor-pointer select-none">
            <button
              type="button"
              role="switch"
              aria-checked={opciones[key]}
              onClick={() => onToggleOpcion(key)}
              className="relative w-10 h-6 rounded-full border-2 transition-colors flex-shrink-0"
              style={{
                backgroundColor: opciones[key] ? 'var(--color-primary)' : 'var(--color-border)',
                borderColor:     opciones[key] ? 'var(--color-primary)' : 'var(--color-border)',
              }}
            >
              <span
                className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
                style={{ transform: opciones[key] ? 'translateX(16px)' : 'translateX(0)' }}
              />
            </button>
            <span className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
              {label}
            </span>
          </label>
        ))}
      </div>

      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
        Output: <span className="font-medium">Word (.docx)</span>
      </p>
    </section>
  );
}
