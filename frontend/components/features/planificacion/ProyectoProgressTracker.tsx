'use client';

import { useEffect, useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { getProyecto } from '@/services/planificacionService';

interface Props {
  proyectoId: string;
}

const STEPS = [
  { label: 'Leyendo el archivo',        description: 'Procesando el archivo subido' },
  { label: 'Detectando estructura WBS', description: 'Identificando jerarquía de tareas' },
  { label: 'Extrayendo fechas y áreas', description: 'Normalizando fechas y responsables' },
  { label: 'Guardando el cronograma',   description: 'Persistiendo en base de datos' },
];

type StepState = 'done' | 'active' | 'pending';

function StepIcon({ state }: { state: StepState }) {
  if (state === 'done')   return <Check   className="w-3.5 h-3.5" style={{ color: 'var(--color-primary)' }} />;
  if (state === 'active') return <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: 'var(--color-primary)' }} />;
  return <span className="w-2 h-2 rounded-full block" style={{ backgroundColor: 'var(--color-border)' }} />;
}

export default function ProyectoProgressTracker({ proyectoId }: Props) {
  const [activeStep, setActiveStep] = useState(0);
  const [finalState, setFinalState] = useState<'procesando' | 'listo' | 'error'>('procesando');
  const [errorDetalle, setErrorDetalle] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const MAX_ATTEMPTS = 60;
    const BASE_INTERVAL = 3000;
    const MAX_INTERVAL = 15000;
    let step = 0;
    let attempts = 0;
    let currentInterval = BASE_INTERVAL;
    let timeoutId: ReturnType<typeof setTimeout>;

    const poll = async () => {
      if (attempts >= MAX_ATTEMPTS) {
        setFinalState('error');
        setErrorDetalle('Tiempo de espera agotado');
        return;
      }
      try {
        const proyecto = await getProyecto(proyectoId);
        if (proyecto.estado !== 'procesando') {
          setFinalState(proyecto.estado);
          if (proyecto.estado === 'error') setErrorDetalle(proyecto.error_detalle);
          if (proyecto.estado === 'listo') setTimeout(() => router.push(`/planificacion/${proyectoId}`), 1000);
          return;
        }
        step = Math.min(step + 1, STEPS.length - 1);
        setActiveStep(step);
      } catch { /* continúa en error de red */ }
      attempts += 1;
      currentInterval = Math.min(currentInterval * 1.5, MAX_INTERVAL);
      timeoutId = setTimeout(poll, currentInterval);
    };

    timeoutId = setTimeout(poll, BASE_INTERVAL);
    return () => clearTimeout(timeoutId);
  }, [proyectoId, router]);

  const getState = (i: number): StepState =>
    finalState === 'listo' ? 'done' : i < activeStep ? 'done' : i === activeStep ? 'active' : 'pending';

  const headline =
    finalState === 'listo' ? '¡Cronograma importado!' :
    finalState === 'error' ? 'Hubo un problema al importar.' :
    'Importando el cronograma...';

  return (
    <div className="space-y-5 p-4 sm:p-6 rounded-lg border" style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>{headline}</p>
      <div className="space-y-4">
        {STEPS.map((s, i) => {
          const state = getState(i);
          return (
            <div key={s.label} className="flex items-start gap-3">
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center border flex-shrink-0 mt-0.5 transition-colors"
                style={{
                  borderColor: state === 'pending' ? 'var(--color-border)' : 'var(--color-primary)',
                  backgroundColor: state === 'pending' ? 'transparent' : 'color-mix(in srgb, var(--color-primary) 10%, transparent)',
                }}
              >
                <StepIcon state={state} />
              </div>
              <div>
                <p className="text-sm font-medium" style={{ color: state === 'pending' ? 'var(--color-text-disabled)' : 'var(--color-text-primary)' }}>
                  {s.label}
                </p>
                <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>{s.description}</p>
              </div>
            </div>
          );
        })}
      </div>
      {finalState === 'error' && (
        <div className="space-y-3 pt-2">
          {errorDetalle && <p className="text-sm" style={{ color: 'var(--color-error)' }}>{errorDetalle}</p>}
          <button
            onClick={() => router.push('/planificacion')}
            className="text-sm px-4 py-2 rounded-md border"
            style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
          >
            Volver a proyectos
          </button>
        </div>
      )}
    </div>
  );
}
