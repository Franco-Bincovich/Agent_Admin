'use client'

import { useState } from 'react'
import Link from 'next/link'
import { RefreshCw } from 'lucide-react'
import { PageLayout } from '@/components/features/layout/PageLayout'
import { EjecucionCard } from '@/components/features/ejecuciones/EjecucionCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { ErrorState } from '@/components/ui/ErrorState'
import { EjecucionSkeleton } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { mockEjecuciones } from '@/lib/mockData'

// Cambiar para previsualizar distintos estados durante desarrollo:
// 'loading' | 'empty' | 'error' | 'data'
type MockState = 'data' | 'loading' | 'empty' | 'error'
const MOCK_STATE: MockState = 'data'

export default function EjecucionesPage() {
  const [state] = useState<MockState>(MOCK_STATE)
  // TODO Sesión 15: reemplazar por hook useEjecuciones() que llame a GET /api/executions

  return (
    <PageLayout
      title="Ejecuciones"
      description="Historial de corridas de análisis de cartera"
      action={
        <Link href="/dashboard/nueva-campana">
          <Button>+ Nueva campaña</Button>
        </Link>
      }
    >
      <div className="flex flex-col gap-3 max-w-3xl">
        {state === 'loading' && (
          <>
            {[1, 2, 3].map((i) => (
              <EjecucionSkeleton key={i} />
            ))}
          </>
        )}

        {state === 'empty' && (
          <EmptyState
            title="Todavía no hay corridas"
            description="Cargá una cartera y configurá las dimensiones para iniciar tu primer análisis."
            action={
              <Link href="/dashboard/nueva-campana">
                <Button>Crear primera campaña</Button>
              </Link>
            }
          />
        )}

        {state === 'error' && (
          <ErrorState
            title="No pudimos cargar las ejecuciones"
            description="Hubo un problema al conectar con el servidor. Verificá tu conexión."
            onRetry={() => window.location.reload()}
          />
        )}

        {state === 'data' && (
          <>
            <div className="flex items-center justify-between mb-1">
              <p className="text-sm text-gray-500">{mockEjecuciones.length} corridas en total</p>
              <button
                onClick={() => window.location.reload()}
                className="flex items-center gap-1.5 text-xs text-secondary hover:underline min-h-[44px] px-2"
                aria-label="Actualizar lista"
              >
                <RefreshCw className="h-3 w-3" aria-hidden />
                Actualizar
              </button>
            </div>
            {mockEjecuciones.map((ejc) => (
              <EjecucionCard key={ejc.id} ejecucion={ejc} />
            ))}
          </>
        )}
      </div>
    </PageLayout>
  )
}
