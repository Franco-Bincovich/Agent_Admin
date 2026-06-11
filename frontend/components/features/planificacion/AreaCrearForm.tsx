'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { createArea } from '@/services/planificacionService';

interface Props {
  proyectoId: string;
  onCreada: () => void;
}

const INPUT_STYLE = {
  backgroundColor: 'var(--color-bg)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text-primary)',
};

export default function AreaCrearForm({ proyectoId, onCreada }: Props) {
  const [open,    setOpen]    = useState(false);
  const [nombre,  setNombre]  = useState('');
  const [capWbs,  setCapWbs]  = useState('');
  const [creando, setCreando] = useState(false);

  const handleCrear = async () => {
    if (!nombre.trim()) return;
    setCreando(true);
    try {
      await createArea(proyectoId, nombre.trim(), capWbs.trim() || null);
      setNombre('');
      setCapWbs('');
      setOpen(false);
      onCreada();
    } catch {
      toast.error('No se pudo crear el área. Intentá de nuevo.');
    } finally {
      setCreando(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="text-sm px-3 py-1.5 rounded-md border"
        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
      >
        + Agregar área
      </button>
    );
  }

  return (
    <div className="rounded-lg border p-4 space-y-3" style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}>
      <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Nueva área</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>Nombre *</label>
          <input
            type="text"
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            placeholder="Nombre del área"
            className="w-full px-3 py-1.5 rounded-md border text-sm outline-none"
            style={INPUT_STYLE}
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>WBS</label>
          <input
            type="text"
            value={capWbs}
            onChange={e => setCapWbs(e.target.value)}
            placeholder="Ej: 1.2"
            className="w-full px-3 py-1.5 rounded-md border text-sm outline-none"
            style={INPUT_STYLE}
          />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={handleCrear}
          disabled={creando || !nombre.trim()}
          className="text-sm px-4 py-1.5 rounded-md flex items-center gap-2"
          style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-bg)', opacity: (creando || !nombre.trim()) ? 0.7 : 1 }}
        >
          {creando && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
          Crear
        </button>
        <button
          onClick={() => { setOpen(false); setNombre(''); setCapWbs(''); }}
          className="text-sm px-4 py-1.5 rounded-md border"
          style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
