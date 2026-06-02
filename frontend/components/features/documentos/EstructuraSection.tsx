'use client';

import { useState } from 'react';
import { GripVertical, X } from 'lucide-react';
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
import type { SeccionItem } from '@/types';

const SECCIONES_PREDEFINIDAS = [
  'Introducción', 'Contexto',
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

interface EstructuraSectionProps {
  secciones: SeccionItem[]
  setSecciones: (secciones: SeccionItem[]) => void
  indicaciones: string
  setIndicaciones: (v: string) => void
  isDisabled?: boolean
}

export default function EstructuraSection({
  secciones,
  setSecciones,
  indicaciones,
  setIndicaciones,
  isDisabled = false,
}: EstructuraSectionProps) {
  const [inputNombre, setInputNombre]           = useState('');
  const [inputDescripcion, setInputDescripcion] = useState('');

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const nombresEnLista = new Set(secciones.map((s) => s.nombre.toLowerCase()));

  function addSeccion(nombre: string, desc?: string) {
    const trimmed = nombre.trim();
    if (!trimmed || nombresEnLista.has(trimmed.toLowerCase())) return;
    setSecciones([
      ...secciones,
      { id: crypto.randomUUID(), nombre: trimmed, descripcion: desc?.trim() || undefined },
    ]);
  }

  function removeSeccion(id: string) {
    setSecciones(secciones.filter((s) => s.id !== id));
  }

  function handleAddCustom() {
    addSeccion(inputNombre, inputDescripcion);
    setInputNombre('');
    setInputDescripcion('');
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = secciones.findIndex((s) => s.id === active.id);
    const newIndex = secciones.findIndex((s) => s.id === over.id);
    setSecciones(arrayMove(secciones, oldIndex, newIndex));
  }

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
        {SECCIONES_PREDEFINIDAS.map((s) => {
          const alreadyAdded = nombresEnLista.has(s.toLowerCase());
          const disabled = isDisabled || alreadyAdded;
          return (
            <button
              key={s}
              type="button"
              onClick={() => addSeccion(s)}
              disabled={disabled}
              className="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

      {!isDisabled && (
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputNombre}
              onChange={(e) => setInputNombre(e.target.value.slice(0, 100))}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddCustom(); } }}
              placeholder="Nombre de sección personalizada"
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
      )}

      {secciones.length > 0 && (
        <div className="space-y-2">
          {isDisabled ? (
            <div className="space-y-2">
              {secciones.map((s) => (
                <div
                  key={s.id}
                  className="flex items-start gap-2 p-2.5 rounded-lg border opacity-70"
                  style={{
                    backgroundColor: 'var(--color-surface)',
                    borderColor: 'var(--color-border)',
                  }}
                >
                  <GripVertical
                    className="w-4 h-4 mt-0.5 shrink-0"
                    style={{ color: 'var(--color-text-disabled)' }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                      {s.nombre}
                    </p>
                    {s.descripcion && (
                      <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-disabled)' }}>
                        {s.descripcion}
                      </p>
                    )}
                  </div>
                  <X className="w-4 h-4 mt-0.5 shrink-0" style={{ color: 'var(--color-text-disabled)' }} />
                </div>
              ))}
            </div>
          ) : (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={secciones.map((s) => s.id)} strategy={verticalListSortingStrategy}>
                <div className="space-y-2">
                  {secciones.map((s) => (
                    <SortableItem key={s.id} item={s} onRemove={removeSeccion} />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}
        </div>
      )}

      {isDisabled && (
        <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
          Las secciones están fijadas por la estructura seleccionada.
          Para modificarlas, quitá la estructura del selector.
        </p>
      )}

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Indicaciones adicionales{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
        </label>
        <textarea
          value={indicaciones}
          onChange={(e) => setIndicaciones(e.target.value.slice(0, 1000))}
          placeholder="Instrucciones especiales, tono deseado, secciones a priorizar..."
          rows={3}
          maxLength={1000}
          className="w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          style={{
            backgroundColor: 'var(--color-background)',
            borderColor: 'var(--color-border)',
            color: 'var(--color-text-primary)',
          }}
        />
        <p className="text-xs text-right" style={{ color: 'var(--color-text-disabled)' }}>
          {indicaciones.length}/1000
        </p>
      </div>
    </section>
  );
}
