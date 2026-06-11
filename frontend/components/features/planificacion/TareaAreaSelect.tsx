'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { asignarArea } from '@/services/planificacionService';
import type { AreaResponse, TareaResponse } from '@/types';

interface Props {
  tarea: TareaResponse;
  areas: AreaResponse[];
  proyectoId: string;
  onActualizada: () => void;
}

export default function TareaAreaSelect({ tarea, areas, proyectoId, onActualizada }: Props) {
  const [saving, setSaving] = useState(false);

  const handleChange = async (areaId: string) => {
    setSaving(true);
    try {
      await asignarArea(proyectoId, tarea.id, areaId || null);
      onActualizada();
    } catch {
      toast.error('No se pudo asignar el área.');
    } finally {
      setSaving(false);
    }
  };

  const current = tarea.area_id ?? '';

  return (
    <select
      value={current}
      onChange={e => handleChange(e.target.value)}
      disabled={saving}
      style={{
        fontSize: 12,
        padding: '3px 6px',
        borderRadius: 6,
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
        color: 'var(--color-text-primary)',
        cursor: saving ? 'wait' : 'pointer',
        outline: 'none',
        maxWidth: 140,
      }}
    >
      <option value="">Sin área</option>
      {areas.map(a => (
        <option key={a.id} value={a.id}>{a.nombre}</option>
      ))}
    </select>
  );
}
