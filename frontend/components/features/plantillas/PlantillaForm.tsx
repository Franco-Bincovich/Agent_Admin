'use client';

import { useState } from 'react';
import { GripVertical, Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type {
  CreateTemplatePayload,
  DocumentTemplate,
  SeccionItem,
  UpdateTemplatePayload,
} from '@/types';

const SECCIONES_PREDEFINIDAS = [
  'Resumen ejecutivo', 'Introducción', 'Contexto',
  'Objetivos', 'Desarrollo', 'Conclusiones', 'Recomendaciones',
];

const FIELD_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';
const FIELD_STYLE = {
  backgroundColor: 'var(--color-background)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text-primary)',
} as const;

function SortableItem({ item, onRemove }: { item: SeccionItem; onRemove: (id: string) => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: item.id });

  return (
    <div
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
      className="flex items-start gap-2 p-2.5 rounded-lg border"
    >
      <button
        type="button"
        className="mt-0.5 cursor-grab active:cursor-grabbing shrink-0"
        style={{ color: 'var(--color-text-disabled)' }}
        {...attributes}
        {...listeners}
        aria-label="Arrastrar para reordenar"
      >
        <GripVertical className="w-4 h-4" />
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          {item.nombre}
        </p>
        {item.descripcion && (
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-disabled)' }}>
            {item.descripcion}
          </p>
        )}
      </div>
      <button
        type="button"
        onClick={() => onRemove(item.id)}
        className="mt-0.5 shrink-0"
        style={{ color: 'var(--color-text-disabled)' }}
        aria-label={`Eliminar ${item.nombre}`}
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

interface Props {
  initialData: DocumentTemplate | null;
  onSave: (data: CreateTemplatePayload | UpdateTemplatePayload) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export default function PlantillaForm({ initialData, onSave, onCancel, isLoading }: Props) {
  const [nombre, setNombre]               = useState(initialData?.nombre ?? '');
  const [secciones, setSecciones]         = useState<SeccionItem[]>(initialData?.secciones ?? []);
  const [inputNombre, setInputNombre]     = useState('');
  const [inputDescripcion, setInputDescripcion] = useState('');
  const [isDefault, setIsDefault]         = useState(initialData?.is_default ?? false);

  const isEdit   = initialData !== null;
  const canSubmit = nombre.trim().length > 0 && secciones.length > 0;

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const nombresEnLista = new Set(secciones.map((s) => s.nombre.toLowerCase()));

  function addSeccion(nombreSeccion: string, desc?: string) {
    const trimmed = nombreSeccion.trim();
    if (!trimmed || nombresEnLista.has(trimmed.toLowerCase())) return;
    setSecciones((prev) => [
      ...prev,
      { id: Date.now().toString(), nombre: trimmed, descripcion: desc?.trim() || undefined },
    ]);
  }

  function removeSeccion(id: string) {
    setSecciones((prev) => prev.filter((s) => s.id !== id));
  }

  function handleAddCustom() {
    addSeccion(inputNombre, inputDescripcion);
    setInputNombre('');
    setInputDescripcion('');
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    setSecciones((prev) => {
      const oldIndex = prev.findIndex((s) => s.id === active.id);
      const newIndex = prev.findIndex((s) => s.id === over.id);
      return arrayMove(prev, oldIndex, newIndex);
    });
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
          Agregar secciones <span style={{ color: 'var(--color-error)' }}>*</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {SECCIONES_PREDEFINIDAS.map((s) => {
            const alreadyAdded = nombresEnLista.has(s.toLowerCase());
            return (
              <button
                key={s}
                type="button"
                onClick={() => addSeccion(s)}
                disabled={alreadyAdded}
                className="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: alreadyAdded
                    ? 'color-mix(in srgb, var(--color-primary) 15%, transparent)'
                    : 'var(--color-surface)',
                  borderColor: alreadyAdded ? 'var(--color-primary)' : 'var(--color-border)',
                  color: alreadyAdded ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                }}
              >
                {s}
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Sección personalizada
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={inputNombre}
            onChange={(e) => setInputNombre(e.target.value.slice(0, 100))}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddCustom(); } }}
            placeholder="Nombre de sección"
            maxLength={100}
            className={FIELD_CLASS}
            style={FIELD_STYLE}
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAddCustom}
            disabled={!inputNombre.trim()}
            className="shrink-0"
          >
            Agregar
          </Button>
        </div>
        <input
          type="text"
          value={inputDescripcion}
          onChange={(e) => setInputDescripcion(e.target.value.slice(0, 500))}
          placeholder="Descripción opcional"
          maxLength={500}
          className={FIELD_CLASS}
          style={FIELD_STYLE}
        />
      </div>

      {secciones.length > 0 ? (
        <div className="space-y-2">
          <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Secciones ({secciones.length})
          </p>
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={secciones.map((s) => s.id)} strategy={verticalListSortingStrategy}>
              <div className="space-y-2">
                {secciones.map((s) => (
                  <SortableItem key={s.id} item={s} onRemove={removeSeccion} />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </div>
      ) : (
        <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
          Agregá al menos una sección.
        </p>
      )}

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
