'use client';

import { Check, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { Proyecto, ProyectoPrioridad } from '@/types';
import { useNuevoProyectoForm } from '@/hooks/useNuevoProyectoForm';

const STEPS = ['Datos', 'Cronograma', 'Áreas', 'Confirmar'];
const FIELD = 'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';
const FS = { backgroundColor: 'var(--color-background)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' } as const;
const LS = { color: 'var(--color-text-primary)' };
interface Props { open: boolean; onClose: () => void; onCreated: (proyecto: Proyecto) => void; }

export default function NuevoProyectoModal({ open, onClose, onCreated }: Props) {
  const { step, form, setForm, isSubmitting, canNext, handleNext, handleBack, handleClose, handleSubmit } =
    useNuevoProyectoForm({ onClose, onCreated });

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) handleClose(); }}>
      <DialogContent className="sm:max-w-lg" showCloseButton={false} style={{ backgroundColor: 'var(--color-surface)' }}>
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--color-text-primary)' }}>Nuevo proyecto</DialogTitle>
        </DialogHeader>

        {/* Stepper */}
        <div className="flex items-start my-4">
          {STEPS.map((label, i) => {
            const n = i + 1;
            const isActive = n === step;
            const isDone = n < step;
            return (
              <div key={n} className="flex items-center flex-1 min-w-0">
                <div className="flex flex-col items-center flex-shrink-0">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold"
                    style={{
                      backgroundColor: isDone ? 'color-mix(in srgb, var(--color-primary) 15%, transparent)' : isActive ? 'var(--color-primary)' : 'transparent',
                      border: `1px solid ${isDone || isActive ? 'var(--color-primary)' : 'var(--color-border)'}`,
                      color: isActive ? '#fff' : isDone ? 'var(--color-primary)' : 'var(--color-text-disabled)',
                    }}
                  >
                    {isDone ? <Check className="w-3 h-3" /> : n}
                  </div>
                  <span className="text-xs mt-1 text-center leading-tight" style={{ color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-disabled)' }}>
                    {label}
                  </span>
                </div>
                {n < STEPS.length && (
                  <div className="flex-1 h-px mx-1 mb-5" style={{ backgroundColor: 'var(--color-border)' }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Paso 1 — Datos del proyecto */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium" style={LS}>
                Nombre <span style={{ color: 'var(--color-error)' }}>*</span>
              </label>
              <input maxLength={200} value={form.nombre} placeholder="Ej: Licitación Puente Sur 2026"
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                className={FIELD} style={FS} />
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium" style={LS}>
                Expediente <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
              </label>
              <input maxLength={100} value={form.expediente} placeholder="Ej: EXP-2026-00123"
                onChange={(e) => setForm((f) => ({ ...f, expediente: e.target.value }))}
                className={FIELD} style={FS} />
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium" style={LS}>Prioridad</label>
              <select value={form.prioridad} className={FIELD} style={FS}
                onChange={(e) => setForm((f) => ({ ...f, prioridad: e.target.value as ProyectoPrioridad }))}>
                <option value="alta">Alta</option>
                <option value="media">Media</option>
                <option value="baja">Baja</option>
              </select>
            </div>
          </div>
        )}

        {/* Paso 2 — Cargar cronograma */}
        {step === 2 && (
          <div className="space-y-3">
            <label className="block text-sm font-medium" style={LS}>
              Archivo del cronograma <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <label
              className="flex items-center justify-center w-full h-24 rounded-lg border-2 border-dashed cursor-pointer transition-colors hover:border-[var(--color-primary)]"
              style={{ borderColor: form.archivo ? 'var(--color-primary)' : 'var(--color-border)' }}
            >
              <span className="text-sm px-4 text-center" style={{ color: 'var(--color-text-secondary)' }}>
                {form.archivo ? form.archivo.name : 'Hacé clic para seleccionar (.xml, .mpp)'}
              </span>
              <input type="file" accept=".xml,.mpp" className="hidden"
                onChange={(e) => setForm((f) => ({ ...f, archivo: e.target.files?.[0] ?? null }))} />
            </label>
          </div>
        )}

        {/* Paso 3 — Datos de áreas */}
        {step === 3 && (
          <div className="rounded-lg border p-4" style={{ backgroundColor: 'color-mix(in srgb, var(--color-primary) 8%, transparent)', borderColor: 'var(--color-border)' }}>
            <p className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
              Las áreas se detectarán automáticamente del cronograma. Podrás completar responsables y contactos una vez creado el proyecto.
            </p>
          </div>
        )}

        {/* Paso 4 — Confirmar */}
        {step === 4 && (
          <div className="rounded-lg border p-4 space-y-3" style={{ borderColor: 'var(--color-border)' }}>
            {([['Nombre', form.nombre], ['Expediente', form.expediente || '—'], ['Prioridad', form.prioridad], ['Archivo', form.archivo?.name ?? '—']] as [string, string][]).map(([label, value]) => (
              <div key={label} className="flex justify-between gap-4 text-sm">
                <span style={{ color: 'var(--color-text-secondary)' }}>{label}</span>
                <span className="font-medium text-right" style={{ color: 'var(--color-text-primary)' }}>{value}</span>
              </div>
            ))}
          </div>
        )}

        {/* Navegación */}
        <div className="flex gap-3 mt-2">
          <Button type="button" variant="outline" className="flex-1" disabled={isSubmitting}
            onClick={step === 1 ? handleClose : handleBack}>
            {step === 1 ? 'Cancelar' : 'Atrás'}
          </Button>
          {step < 4 ? (
            <Button type="button" className="flex-1" onClick={handleNext} disabled={!canNext()}>
              Continuar
            </Button>
          ) : (
            <Button type="button" className="flex-1 min-h-[44px]" onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Creando…</> : 'Crear proyecto'}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
