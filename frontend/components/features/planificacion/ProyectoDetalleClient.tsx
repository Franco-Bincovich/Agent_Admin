'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useProyectoDetalle } from '@/hooks/useProyectoDetalle';
import type { Proyecto } from '@/types';
import ProyectoProgressTracker from './ProyectoProgressTracker';
import ProyectoRevisionView from './ProyectoRevisionView';
import ProyectoTabs from './ProyectoTabs';
import VisualesContainer from './VisualesContainer';

interface Props {
  proyectoId: string;
  proyectos: Proyecto[];
}

type ActiveTab = 'revision' | 'gantt' | 'planilla' | 'portfolio' | 'unificado';

export default function ProyectoDetalleClient({ proyectoId, proyectos }: Props) {
  const { proyecto, isLoading, error, refresh } = useProyectoDetalle(proyectoId);
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<ActiveTab>('revision');

  if (isLoading) {
    return <div className="h-8 w-64 rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />;
  }

  if (error) {
    return (
      <div className="space-y-3">
        <p className="text-sm" style={{ color: 'var(--color-error)' }}>{error}</p>
        <button onClick={refresh} className="text-sm px-4 py-2 rounded-md border" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
          Reintentar
        </button>
      </div>
    );
  }

  if (!proyecto) return null;

  if (proyecto.estado === 'procesando') {
    return <ProyectoProgressTracker proyectoId={proyectoId} />;
  }

  if (proyecto.estado === 'listo') {
    return (
      <div className="space-y-4">
        <ProyectoTabs activeTab={activeTab} onChange={setActiveTab} />
        {activeTab === 'revision'
          ? <ProyectoRevisionView detalle={proyecto} onVerVisuales={() => setActiveTab('gantt')} onAreaCreada={refresh} onTareaActualizada={refresh} />
          : <VisualesContainer detalle={proyecto} activeTab={activeTab} onActualizada={refresh} proyectos={proyectos} />
        }
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm" style={{ color: 'var(--color-error)' }}>
        {proyecto.error_detalle ?? 'Error al importar el cronograma.'}
      </p>
      <button
        onClick={() => router.push('/planificacion')}
        className="text-sm px-4 py-2 rounded-md border"
        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
      >
        Volver
      </button>
    </div>
  );
}
