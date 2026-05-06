'use client';

import { useEffect, useRef, useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { getGeneration } from '@/services/generationService';
import type { Generation, GenerationStatus } from '@/types';

interface Props {
  status: GenerationStatus;
  generationId: string | null;
  onComplete: (generation: Generation) => void;
}

const STEPS = [
  { label: 'Extrayendo contenido',   description: 'Procesando los archivos subidos' },
  { label: 'Analizando con IA',      description: 'Claude está construyendo el outline' },
  { label: 'Generando presentación', description: 'Creando el archivo PPTX' },
  { label: 'Publicando en Gamma',    description: 'Subiendo y obteniendo el link' },
];

type StepState = 'done' | 'active' | 'pending';

function StepIcon({ state }: { state: StepState }) {
  if (state === 'done')   return <Check   className="w-3.5 h-3.5" style={{ color: 'var(--color-success)' }} />;
  if (state === 'active') return <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: 'var(--color-primary)' }} />;
  return <span className="w-2 h-2 rounded-full block" style={{ backgroundColor: 'var(--color-border)' }} />;
}

export default function ProgressTracker({ status, generationId, onComplete }: Props) {
  const [activeStep, setActiveStep] = useState(0);
  const onCompleteRef = useRef(onComplete);
  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    if (!generationId || status !== 'procesando') return;
    let step = 0;
    const id = setInterval(async () => {
      try {
        const gen = await getGeneration(generationId);
        if (gen.estado !== 'procesando') {
          clearInterval(id);
          onCompleteRef.current(gen);
          return;
        }
        step = Math.min(step + 1, STEPS.length - 1);
        setActiveStep(step);
      } catch { /* keep polling on network error */ }
    }, 3000);
    return () => clearInterval(id);
  }, [generationId, status]);

  const getState = (i: number): StepState =>
    status === 'listo' ? 'done' : i < activeStep ? 'done' : i === activeStep ? 'active' : 'pending';

  const headline =
    status === 'listo' ? '¡Presentación lista!' :
    status === 'error' ? 'Hubo un problema al generar.' :
    'Generando tu presentación...';

  return (
    <div className="space-y-5 p-6 rounded-lg border" style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>{headline}</p>
      <div className="space-y-4">
        {STEPS.map((step, i) => {
          const state = getState(i);
          return (
            <div key={step.label} className="flex items-start gap-3">
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center border flex-shrink-0 mt-0.5 transition-colors"
                style={{
                  borderColor: state === 'done' ? 'var(--color-success)' : state === 'active' ? 'var(--color-primary)' : 'var(--color-border)',
                  backgroundColor: state === 'pending' ? 'transparent' : state === 'done' ? 'color-mix(in srgb, var(--color-success) 10%, transparent)' : 'color-mix(in srgb, var(--color-primary) 10%, transparent)',
                }}
              >
                <StepIcon state={state} />
              </div>
              <div>
                <p className="text-sm font-medium" style={{ color: state === 'pending' ? 'var(--color-text-disabled)' : 'var(--color-text-primary)' }}>
                  {step.label}
                </p>
                <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>{step.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
