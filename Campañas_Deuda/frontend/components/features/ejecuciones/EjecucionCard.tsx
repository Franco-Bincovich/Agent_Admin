import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import type { Ejecucion } from '@/types'
import { CARTERA_LABELS, DUREZA_LABELS } from '@/types'
import { EstadoBadge } from './EstadoBadge'
import { formatFecha } from '@/lib/utils'

interface EjecucionCardProps {
  ejecucion: Ejecucion
}

export function EjecucionCard({ ejecucion }: EjecucionCardProps) {
  const { id, cartera, dureza, periodo, estado, createdAt, errorMessage } = ejecucion

  const titulo = `${CARTERA_LABELS[cartera]} · ${DUREZA_LABELS[dureza]} · ${periodo === 'todas' ? 'Todos los períodos' : periodo}`

  return (
    <Link
      href={`/dashboard/ejecuciones/${id}`}
      className="group flex items-center gap-4 rounded-xl border border-card-border bg-surface p-4 transition-all hover:border-secondary/40 hover:shadow-sm"
      aria-label={`Ver detalle de ejecución: ${titulo}`}
    >
      {/* Indicador de estado */}
      <div
        className={`h-10 w-1 flex-shrink-0 rounded-full ${
          estado === 'listo'
            ? 'bg-green-400'
            : estado === 'corriendo'
              ? 'bg-blue-400'
              : estado === 'pendiente'
                ? 'bg-yellow-400'
                : 'bg-red-400'
        }`}
        aria-hidden
      />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{titulo}</p>
        {errorMessage ? (
          <p className="mt-0.5 text-xs text-red-600 truncate">{errorMessage}</p>
        ) : (
          <p className="mt-0.5 text-xs text-gray-500">{formatFecha(createdAt)}</p>
        )}
      </div>

      <div className="flex items-center gap-3 flex-shrink-0">
        <EstadoBadge estado={estado} />
        <ChevronRight
          className="h-4 w-4 text-gray-400 group-hover:text-secondary transition-colors"
          aria-hidden
        />
      </div>
    </Link>
  )
}
