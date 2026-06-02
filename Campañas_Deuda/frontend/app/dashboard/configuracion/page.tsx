import { PageLayout } from '@/components/features/layout/PageLayout'

/** Página placeholder — se implementa en sesiones futuras. */
export default function ConfiguracionPage() {
  return (
    <PageLayout title="Configuración" description="Ajustes del sistema">
      <div className="rounded-xl border border-card-border bg-surface p-12 text-center max-w-md">
        <p className="text-sm font-medium text-gray-700">Próximamente</p>
        <p className="mt-1 text-sm text-gray-500">
          La configuración de usuarios y destinatarios se habilita en sesiones futuras.
        </p>
      </div>
    </PageLayout>
  )
}
