import Link from 'next/link'
import { BarChart3, Clock, FileText, TrendingUp } from 'lucide-react'
import { PageLayout } from '@/components/features/layout/PageLayout'
import { StatCard } from '@/components/features/dashboard/StatCard'
import { EjecucionCard } from '@/components/features/ejecuciones/EjecucionCard'
import { Button } from '@/components/ui/Button'
import { mockDashboardStats, mockEjecuciones } from '@/lib/mockData'

export default function DashboardPage() {
  const recientes = mockEjecuciones.slice(0, 3)

  return (
    <PageLayout
      title="Inicio"
      description="Resumen de actividad del sistema"
      action={
        <Link href="/dashboard/nueva-campana">
          <Button>+ Nueva campaña</Button>
        </Link>
      }
    >
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        <StatCard
          label="Corridas este mes"
          value={mockDashboardStats.ejecucionesEsteMes}
          icon={<BarChart3 className="h-5 w-5" />}
          accentColor="primary"
        />
        <StatCard
          label="Carteras analizadas"
          value={mockDashboardStats.carterasAnalizadas}
          icon={<FileText className="h-5 w-5" />}
          accentColor="info"
        />
        <StatCard
          label="Informes generados"
          value={mockDashboardStats.informesGenerados}
          icon={<TrendingUp className="h-5 w-5" />}
          accentColor="success"
        />
        <StatCard
          label="Última corrida"
          value={mockDashboardStats.ultimaCorreidaHace}
          icon={<Clock className="h-5 w-5" />}
          accentColor="accent"
        />
      </div>

      {/* Ejecuciones recientes */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">Corridas recientes</h2>
          <Link href="/dashboard/ejecuciones" className="text-sm text-secondary hover:underline">
            Ver todas
          </Link>
        </div>
        <div className="flex flex-col gap-3">
          {recientes.map((ejc) => (
            <EjecucionCard key={ejc.id} ejecucion={ejc} />
          ))}
        </div>
      </div>
    </PageLayout>
  )
}
