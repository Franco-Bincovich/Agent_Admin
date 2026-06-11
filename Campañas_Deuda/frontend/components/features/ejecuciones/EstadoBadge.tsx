import { CheckCircle2, Clock, Loader2, XCircle } from 'lucide-react'
import type { EstadoEjecucion } from '@/types'
import { Badge } from '@/components/ui/Badge'

const ESTADO_CONFIG: Record<
  EstadoEjecucion,
  {
    label: string
    variant: 'success' | 'warning' | 'info' | 'error'
    Icon: React.ElementType
    animate?: boolean
  }
> = {
  listo: { label: 'Listo', variant: 'success', Icon: CheckCircle2 },
  corriendo: { label: 'Analizando...', variant: 'info', Icon: Loader2, animate: true },
  pendiente: { label: 'Pendiente', variant: 'warning', Icon: Clock },
  error: { label: 'Error', variant: 'error', Icon: XCircle },
}

interface EstadoBadgeProps {
  estado: EstadoEjecucion
}

export function EstadoBadge({ estado }: EstadoBadgeProps) {
  const { label, variant, Icon, animate } = ESTADO_CONFIG[estado]
  return (
    <Badge variant={variant} className="whitespace-nowrap">
      <Icon className={`h-3 w-3 ${animate ? 'animate-spin' : ''}`} aria-hidden />
      {label}
    </Badge>
  )
}
