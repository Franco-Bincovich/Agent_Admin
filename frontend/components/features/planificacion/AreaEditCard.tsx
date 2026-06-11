'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { updateArea } from '@/services/planificacionService';
import type { AreaResponse } from '@/types';

interface Props {
  area: AreaResponse;
  proyectoId: string;
}

interface AreaFields {
  nombre: string;
  responsable_nombre: string;
  responsable_telefono: string;
  responsable_email: string;
  disponibilidad_horas: string;
  cantidad_empleados: string;
}

const FIELDS: { key: keyof Omit<AreaFields, 'nombre'>; label: string; type: string }[] = [
  { key: 'responsable_nombre',   label: 'Responsable',       type: 'text'   },
  { key: 'responsable_telefono', label: 'Teléfono',          type: 'text'   },
  { key: 'responsable_email',    label: 'Mail',              type: 'email'  },
  { key: 'disponibilidad_horas', label: 'Horas disponibles', type: 'number' },
  { key: 'cantidad_empleados',   label: 'Empleados',         type: 'number' },
];

const INPUT_STYLE = {
  backgroundColor: 'var(--color-bg)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text-primary)',
};

export default function AreaEditCard({ area, proyectoId }: Props) {
  const [fields, setFields] = useState<AreaFields>({
    nombre:               area.nombre,
    responsable_nombre:   area.responsable_nombre   ?? '',
    responsable_telefono: area.responsable_telefono ?? '',
    responsable_email:    area.responsable_email    ?? '',
    disponibilidad_horas: area.disponibilidad_horas?.toString() ?? '',
    cantidad_empleados:   area.cantidad_empleados?.toString()   ?? '',
  });
  const [guardando,    setGuardando]    = useState(false);
  const [guardado,     setGuardado]     = useState(false);
  const [nombreError,  setNombreError]  = useState(false);

  const handleGuardar = async () => {
    if (!fields.nombre.trim()) {
      setNombreError(true);
      return;
    }
    setNombreError(false);
    setGuardando(true);
    setGuardado(false);
    try {
      const campos: Partial<AreaResponse> = {};
      if (fields.nombre.trim() !== area.nombre)  campos.nombre               = fields.nombre.trim();
      if (fields.responsable_nombre)             campos.responsable_nombre   = fields.responsable_nombre;
      if (fields.responsable_telefono)           campos.responsable_telefono = fields.responsable_telefono;
      if (fields.responsable_email)              campos.responsable_email    = fields.responsable_email;
      if (fields.disponibilidad_horas !== '')    campos.disponibilidad_horas = Number(fields.disponibilidad_horas);
      if (fields.cantidad_empleados   !== '')    campos.cantidad_empleados   = Number(fields.cantidad_empleados);
      await updateArea(proyectoId, area.id, campos);
      setGuardado(true);
      setTimeout(() => setGuardado(false), 2000);
    } catch {
      toast.error('No se pudo guardar el área. Intentá de nuevo.');
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="rounded-lg border p-4 space-y-4" style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}>
      <div className="flex items-center gap-2">
        {area.color && (
          <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: area.color }} />
        )}
        <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--color-text-secondary)' }}>Área</p>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>Nombre del área *</label>
        <input
          type="text"
          value={fields.nombre}
          onChange={e => { setFields(f => ({ ...f, nombre: e.target.value })); setNombreError(false); }}
          className="w-full px-3 py-1.5 rounded-md border text-sm outline-none"
          style={{ ...INPUT_STYLE, borderColor: nombreError ? 'var(--color-error)' : 'var(--color-border)' }}
        />
        {nombreError && (
          <p className="text-xs" style={{ color: 'var(--color-error)' }}>El nombre no puede quedar vacío.</p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {FIELDS.map(({ key, label, type }) => (
          <div key={key} className="space-y-1">
            <label className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>{label}</label>
            <input
              type={type}
              value={fields[key]}
              min={type === 'number' ? 0 : undefined}
              onChange={e => setFields(f => ({ ...f, [key]: e.target.value }))}
              className="w-full px-3 py-1.5 rounded-md border text-sm outline-none"
              style={INPUT_STYLE}
            />
          </div>
        ))}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleGuardar}
          disabled={guardando}
          className="text-sm px-4 py-1.5 rounded-md flex items-center gap-2"
          style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-bg)', opacity: guardando ? 0.7 : 1 }}
        >
          {guardando && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
          Guardar
        </button>
        {guardado && <span className="text-xs" style={{ color: 'var(--color-success)' }}>Guardado ✓</span>}
      </div>
    </div>
  );
}
