import ProyectoDetalleWrapper from '@/components/features/planificacion/ProyectoDetalleWrapper';

export default async function ProyectoDetallePage({
  params
}: {
  params: Promise<{ proyecto_id: string }>
}) {
  const { proyecto_id } = await params
  return (
    <div className="space-y-6">
      <ProyectoDetalleWrapper proyectoId={proyecto_id} />
    </div>
  )
}
