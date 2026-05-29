'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type {
  CreateTemplatePayload,
  DocumentoSeccion,
  DocumentTemplate,
  UpdateTemplatePayload,
} from '@/types';

const SECCIONES: DocumentoSeccion[] = [
  'Resumen ejecutivo',
  'Introducción',
  'Contexto',
  'Objetivos',
  'Desarrollo',
  'Conclusiones',
  'Recomendaciones',
];

const FIELD_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';
const FIELD_STYLE = {
  backgroundColor: 'var(--color-background)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text-primary)',
} as const;

interface Props {
  initialData: DocumentTemplate | null;
  onSave: (data: CreateTemplatePayload | UpdateTemplatePayload) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export default function PlantillaForm({ initialData, onSave, onCancel, isLoading }: Props) {
  const [nombre, setNombre] = useState(initialData?.nombre ?? '');
  const [secciones, setSecciones] = useState<DocumentoSeccion[]>(initialData?.secciones ?? []);
  const [isDefault, setIsDefault] = useState(initialData?.is_default ?? false);

  const isEdit = initialData !== null;
  const canSubmit = nombre.trim().length > 0 && secciones.length > 0;

  function toggleSeccion(s: DocumentoSeccion) {
    setSecciones((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s],
    );
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    const payload = isEdit
      ? ({ nombre: nombre.trim(), secciones, is_default: isDefault } satisfies UpdateTemplatePayload)
      : ({ nombre: nombre.trim(), secciones } satisfies CreateTemplatePayload);
    onSave(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div className="space-y-1.5">
        <label
          className="block text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
          htmlFor="pf-nombre"
        >
          Nombre <span style={{ color: 'var(--color-error)' }}>*</span>
        </label>
        <input
          id="pf-nombre"
          type="text"
          value={nombre}
          onChange={(e) => setNombre(e.target.value.slice(0, 100))}
          placeholder="Ej: Informe mensual"
          maxLength={100}
          required
          className={FIELD_CLASS}
          style={FIELD_STYLE}
        />
        <p className="text-xs text-right" style={{ color: 'var(--color-text-disabled)' }}>
          {nombre.length}/100
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Secciones <span style={{ color: 'var(--color-error)' }}>*</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {SECCIONES.map((s) => {
            const selected = secciones.includes(s);
            return (
              <button
                key={s}
                type="button"
                onClick={() => toggleSeccion(s)}
                className="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors"
                style={{
                  backgroundColor: selected
                    ? 'color-mix(in srgb, var(--color-primary) 15%, transparent)'
                    : 'var(--color-surface)',
                  borderColor: selected ? 'var(--color-primary)' : 'var(--color-border)',
                  color: selected ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                }}
              >
                {s}
              </button>
            );
          })}
        </div>
        {secciones.length === 0 && (
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Seleccioná al menos una sección.
          </p>
        )}
      </div>

      {isEdit && (
        <div className="flex items-center gap-2">
          <input
            id="pf-default"
            type="checkbox"
            checked={isDefault}
            onChange={(e) => setIsDefault(e.target.checked)}
            className="rounded"
          />
          <label
            htmlFor="pf-default"
            className="text-sm cursor-pointer"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Marcar como estructura por defecto
          </label>
        </div>
      )}

      <div className="flex gap-3 pt-1">
        <Button
          type="button"
          variant="outline"
          className="flex-1"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          className="flex-1 min-h-[44px]"
          disabled={isLoading || !canSubmit}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Guardando...
            </>
          ) : isEdit ? (
            'Guardar cambios'
          ) : (
            'Crear estructura'
          )}
        </Button>
      </div>
    </form>
  );
}
