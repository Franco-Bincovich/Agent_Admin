'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { TareaResponse } from '@/types';
import { reprogramarTarea } from '@/services/planificacionService';

const FIELD = 'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';
const FS = { backgroundColor: 'var(--color-background)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' } as const;
const LS = { color: 'var(--color-text-primary)' };

interface Props {
  open: boolean;
  onClose: () => void;
  proyectoId: string;
  tarea: TareaResponse;
  onReprogramada: () => void;
}

export default function ReprogramarTareaModal({ open, onClose, proyectoId, tarea, onReprogramada }: Props) {
  const [fechaInicio, setFechaInicio] = useState(tarea.fecha_inicio ?? '');
  const [fechaFin, setFechaFin] = useState(tarea.fecha_fin ?? '');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const canConfirm = fechaInicio !== '' && fechaFin !== '' && fechaFin >= fechaInicio;

  const handleSubmit = async () => {
    if (!canConfirm) return;
    setIsSubmitting(true);
    try {
      await reprogramarTarea(proyectoId, tarea.id, fechaInicio, fechaFin);
      toast.success('Tarea reprogramada');
      onReprogramada();
      onClose();
    } catch {
      toast.error('No se pudo reprogramar la tarea');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-md" showCloseButton={false} style={{ backgroundColor: 'var(--color-surface)' }}>
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--color-text-primary)' }}>Reprogramar tarea</DialogTitle>
        </DialogHeader>

        <p className="text-sm truncate" style={{ color: 'var(--color-text-secondary)' }}>
          {tarea.wbs} · {tarea.nombre}
        </p>

        {tarea.reprogramada && tarea.fecha_inicio_original && tarea.fecha_fin_original && (
          <div
            className="rounded-lg border px-3 py-2 text-xs"
            style={{
              borderColor: 'var(--color-border)',
              color: 'var(--color-text-secondary)',
              backgroundColor: 'color-mix(in srgb, var(--color-primary) 6%, transparent)',
            }}
          >
            Plan original: {tarea.fecha_inicio_original} → {tarea.fecha_fin_original}
          </div>
        )}

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LS}>
              Nueva fecha de inicio <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              className={FIELD}
              style={FS}
            />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LS}>
              Nueva fecha de fin <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              className={FIELD}
              style={FS}
            />
          </div>
        </div>

        <div className="flex gap-3 mt-2">
          <Button type="button" variant="outline" className="flex-1" disabled={isSubmitting} onClick={onClose}>
            Cancelar
          </Button>
          <Button
            type="button"
            className="flex-1 min-h-[44px]"
            onClick={handleSubmit}
            disabled={!canConfirm || isSubmitting}
          >
            {isSubmitting
              ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Reprogramando…</>
              : 'Confirmar'
            }
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
