import Link from 'next/link'
import { ArrowLeft, Download, FileText, Mail, Clock } from 'lucide-react'
import { PageLayout } from '@/components/features/layout/PageLayout'
import { EstadoBadge } from '@/components/features/ejecuciones/EstadoBadge'
import { Button } from '@/components/ui/Button'
import { mockEjecuciones, mockDestinatarios } from '@/lib/mockData'
import { CARTERA_LABELS, DUREZA_LABELS } from '@/types'
import { formatFecha } from '@/lib/utils'

interface PageProps {
  params: { id: string }
}

export default function EjecucionDetailPage({ params }: PageProps) {
  // TODO Sesión 15: reemplazar por fetch al GET /api/executions/{id}
  const ejc = mockEjecuciones.find((e) => e.id === params.id) ?? mockEjecuciones[0]

  const titulo = `${CARTERA_LABELS[ejc.cartera]} · ${DUREZA_LABELS[ejc.dureza]} · ${
    ejc.periodo === 'todas' ? 'Todos los períodos' : ejc.periodo
  }`

  return (
    <PageLayout
      title="Detalle de corrida"
      action={
        <Link href="/dashboard/ejecuciones">
          <Button variant="secondary" className="gap-2">
            <ArrowLeft className="h-4 w-4" aria-hidden />
            Volver
          </Button>
        </Link>
      }
    >
      <div className="flex flex-col gap-6 max-w-2xl">
        {/* Estado y título */}
        <div className="rounded-xl border border-card-border bg-surface p-6 flex flex-col gap-4">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <h2 className="text-base font-semibold text-gray-900">{titulo}</h2>
            <EstadoBadge estado={ejc.estado} />
          </div>

          {ejc.errorMessage && (
            <p className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {ejc.errorMessage}
            </p>
          )}

          {/* Timeline */}
          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2 text-sm">
            <div>
              <dt className="text-gray-500 flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" aria-hidden /> Creada
              </dt>
              <dd className="mt-0.5 font-medium text-gray-900">{formatFecha(ejc.createdAt)}</dd>
            </div>
            {ejc.startedAt && (
              <div>
                <dt className="text-gray-500">Inicio del análisis</dt>
                <dd className="mt-0.5 font-medium text-gray-900">{formatFecha(ejc.startedAt)}</dd>
              </div>
            )}
            {ejc.finishedAt && (
              <div>
                <dt className="text-gray-500">Finalizada</dt>
                <dd className="mt-0.5 font-medium text-gray-900">{formatFecha(ejc.finishedAt)}</dd>
              </div>
            )}
          </dl>
        </div>

        {/* Informe generado */}
        <div className="rounded-xl border border-card-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <FileText className="h-4 w-4 text-secondary" aria-hidden />
            Informe ejecutivo
          </h3>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              disabled={ejc.estado !== 'listo'}
              title={
                ejc.estado !== 'listo'
                  ? 'El informe estará disponible cuando finalice la corrida'
                  : undefined
              }
            >
              <Download className="h-4 w-4" aria-hidden />
              Descargar Word (.docx)
            </Button>
            <Button
              variant="secondary"
              disabled={ejc.estado !== 'listo'}
              title={
                ejc.estado !== 'listo'
                  ? 'El informe estará disponible cuando finalice la corrida'
                  : undefined
              }
            >
              <Download className="h-4 w-4" aria-hidden />
              Descargar PDF
            </Button>
          </div>
          {ejc.estado !== 'listo' && (
            <p className="mt-3 text-xs text-gray-500">
              Los archivos estarán disponibles cuando el análisis finalice correctamente.
            </p>
          )}
        </div>

        {/* Destinatarios */}
        <div className="rounded-xl border border-card-border bg-surface p-6">
          <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Mail className="h-4 w-4 text-secondary" aria-hidden />
            Destinatarios (CC)
          </h3>
          <ul className="flex flex-col gap-2">
            {(ejc.destinatariosCc ?? mockDestinatarios).map((email) => (
              <li key={email} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="h-2 w-2 rounded-full bg-secondary flex-shrink-0" aria-hidden />
                {email}
              </li>
            ))}
          </ul>
          {/* TODO Sesión 20: botón "Enviar informe por email" con selección de destinatarios */}
          <Button
            className="mt-4"
            disabled={ejc.estado !== 'listo'}
            title={ejc.estado !== 'listo' ? 'Disponible cuando finalice el análisis' : undefined}
          >
            Enviar informe por email
          </Button>
        </div>
      </div>
    </PageLayout>
  )
}
