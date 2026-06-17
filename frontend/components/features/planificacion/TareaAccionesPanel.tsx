'use client';

import { useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { TareaResponse } from '@/types';
import { actualizarProgreso } from '@/services/planificacionService';

const PASOS = [0, 25, 50, 75, 100] as const;

interface Props {
  open: boolean;
  onClose: () => void;
  proyectoId: string;
  tarea: TareaResponse;
  onActualizada: () => void;
  onReprogramar: () => void;
}

export default function TareaAccionesPanel({ open, onClose, proyectoId, tarea, onActualizada, onReprogramar }: Props) {
  const [isSaving, setIsSaving] = useState(false);

  const handleProgreso = async (valor: number) => {
    if (valor === tarea.progreso || isSaving) return;
    setIsSaving(true);
    try {
      await actualizarProgreso(proyectoId, tarea.id, valor);
      toast.success('Progreso actualizado');
      onActualizada();
    } catch {
      toast.error('No se pudo actualizar el progreso');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-sm" showCloseButton={false} style={{ backgroundColor: 'var(--color-surface)' }}>
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--color-text-primary)' }}>Acciones de tarea</DialogTitle>
        </DialogHeader>

        <p className="text-sm truncate -mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          {tarea.wbs} · {tarea.nombre}
        </p>

        {/* Selector de progreso */}
        <div className="space-y-2">
          <p className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>Progreso</p>
          <div className="flex gap-2">
            {PASOS.map((paso) => {
              const activo = paso === tarea.progreso;
              return (
                <button
                  key={paso}
                  onClick={() => handleProgreso(paso)}
                  disabled={isSaving}
                  className="flex-1 flex items-center justify-center gap-1 rounded-lg border text-xs font-medium transition-colors"
                  style={{
                    minHeight: 40,
                    backgroundColor: activo ? 'var(--color-primary)' : 'transparent',
                    borderColor: activo ? 'var(--color-primary)' : 'var(--color-border)',
                    color: activo ? '#fff' : 'var(--color-text-primary)',
                    cursor: isSaving ? 'wait' : activo ? 'default' : 'pointer',
                    opacity: isSaving && !activo ? 0.5 : 1,
                  }}
                >
                  {paso === 100 && activo && <Check className="w-3 h-3" />}
                  {paso}%
                </button>
              );
            })}
          </div>
          {isSaving && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
              <Loader2 className="w-3 h-3 animate-spin" />
              Guardando…
            </div>
          )}
        </div>

        {/* Reprogramar */}
        <div className="space-y-2 pt-2 border-t" style={{ borderColor: 'var(--color-border)' }}>
          <Button type="button" variant="outline" className="w-full" onClick={onReprogramar}>
            Reprogramar tarea
          </Button>
          {tarea.reprogramada && tarea.fecha_inicio_original && tarea.fecha_fin_original && (
            <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
              Reprogramada · plan original {tarea.fecha_inicio_original} → {tarea.fecha_fin_original}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="pt-1">
          <Button type="button" variant="outline" className="w-full" onClick={onClose}>
            Cerrar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
