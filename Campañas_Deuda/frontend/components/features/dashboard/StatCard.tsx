import { cn } from '@/lib/utils'

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  trend?: string
  accentColor?: 'primary' | 'accent' | 'success' | 'info'
  className?: string
}

const accentMap = {
  primary: 'bg-primary/10 text-primary',
  accent: 'bg-accent/10 text-accent',
  success: 'bg-green-100 text-green-600',
  info: 'bg-blue-100 text-blue-600',
}

export function StatCard({
  label,
  value,
  icon,
  trend,
  accentColor = 'primary',
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-card-border bg-surface p-5 flex items-start gap-4',
        className
      )}
    >
      <div
        className={cn(
          'flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl',
          accentMap[accentColor]
        )}
        aria-hidden
      >
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-sm text-gray-500 truncate">{label}</p>
        <p className="mt-0.5 text-2xl font-bold text-gray-900">{value}</p>
        {trend && <p className="mt-1 text-xs text-gray-400">{trend}</p>}
      </div>
    </div>
  )
}
