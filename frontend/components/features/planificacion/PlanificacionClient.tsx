'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { usePlanificacion } from '@/hooks/usePlanificacion';
import ProyectoCard from './ProyectoCard';
import NuevoProyectoModal from './NuevoProyectoModal';

function SkeletonCard() {
  return (
    <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <CardContent className="p-4 space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-4 w-full rounded animate-pulse"
            style={{ backgroundColor: 'var(--color-border)' }}
          />
        ))}
      </CardContent>
    </Card>
  );
}

export default function PlanificacionClient() {
  const { proyectos, isLoading, error, refresh } = usePlanificacion();
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Proyectos
        </h2>
        <button
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium min-h-[40px] transition-colors"
          style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-background)' }}
        >
          <Plus className="w-4 h-4" />
          Nuevo proyecto
        </button>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <SkeletonCard /><SkeletonCard /><SkeletonCard />
        </div>
      )}

      {!isLoading && error && (
        <div className="flex flex-col items-center gap-3 py-12 text-center">
          <p className="text-sm" style={{ color: 'var(--color-error)' }}>{error}</p>
          <button
            onClick={refresh}
            className="text-sm font-medium underline"
            style={{ color: 'var(--color-primary)' }}
          >
            Reintentar
          </button>
        </div>
      )}

      {!isLoading && !error && proyectos.length === 0 && (
        <div className="flex flex-col items-center gap-3 py-12 text-center">
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
            No tenés proyectos todavía
          </p>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Importá un cronograma para empezar.
          </p>
        </div>
      )}

      {!isLoading && !error && proyectos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {proyectos.map((p) => (
            <ProyectoCard key={p.id} proyecto={p} onDeleted={refresh} />
          ))}
        </div>
      )}
    </div>

    <NuevoProyectoModal
      open={modalOpen}
      onClose={() => setModalOpen(false)}
      onCreated={() => { setModalOpen(false); refresh(); }}
    />
    </>
  );
}
