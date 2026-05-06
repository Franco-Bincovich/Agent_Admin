'use client';

import { useEffect, useRef, useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import { getDocumento } from '@/services/documentoService';
import type { Documento, DocumentoEstado } from '@/types';

interface Props {
  documentoId: string;
  onComplete: (documento: Documento) => void;
}

const STEPS = [
  { label: 'Extrayendo contenido',  description: 'Procesando los archivos subidos' },
  { label: 'Analizando con IA',     description: 'Claude está analizando el contenido' },
  { label: 'Generando documento',   description: 'Construyendo el archivo Word' },
];

type StepState = 'done' | 'active' | 'pending';

function StepIcon({ state }: { state: StepState }) {
  if (state === 'done')   return <Check   className="w-3.5 h-3.5" style={{ color: 'var(--color-success)' }} />;
  if (state === 'active') return <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: 'var(--color-primary)' }} />;
  return <span className="w-2 h-2 rounded-full block" style={{ backgroundColor: 'var(--color-border)' }} />;
}

export default function DocumentoProgressTracker({ documentoId, onComplete }: Props) {
  const [activeStep, setActiveStep] = useState(0);
  const onCompleteRef = useRef(onComplete);
  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    let step = 0;
    const id = setInterval(async () => {
      try {
        const doc = await getDocumento(documentoId);
        if (doc.estado !== 'procesando') {
          clearInterval(id);
          onCompleteRef.current(doc);
          return;
        }
        step = Math.min(step + 1, STEPS.length - 1);
        setActiveStep(step);
      } catch { /* keep polling on network error */ }
    }, 3000);
    return () => clearInterval(id);
  }, [documentoId]);

  const getState = (i: number): StepState =>
    i < activeStep ? 'done' : i === activeStep ? 'active' : 'pending';

  return (
    <div className="space-y-5">
      <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Generando tu documento...
      </p>
      <div className="space-y-4">
        {STEPS.map((step, i) => {
          const state = getState(i);
          return (
            <div key={step.label} className="flex items-start gap-3">
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center border flex-shrink-0 mt-0.5 transition-colors"
                style={{
                  borderColor:
                    state === 'done'   ? 'var(--color-success)' :
                    state === 'active' ? 'var(--color-primary)' :
                    'var(--color-border)',
                  backgroundColor:
                    state === 'pending' ? 'transparent' :
                    state === 'done'    ? 'color-mix(in srgb, var(--color-success) 10%, transparent)' :
                    'color-mix(in srgb, var(--color-primary) 10%, transparent)',
                }}
              >
                <StepIcon state={state} />
              </div>
              <div>
                <p
                  className="text-sm font-medium"
                  style={{ color: state === 'pending' ? 'var(--color-text-disabled)' : 'var(--color-text-primary)' }}
                >
                  {step.label}
                </p>
                <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
