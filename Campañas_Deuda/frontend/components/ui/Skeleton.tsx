import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return <div aria-hidden className={cn('animate-pulse rounded-md bg-gray-200', className)} />
}

/** Fila de skeleton para tablas/listas de ejecuciones. */
export function EjecucionSkeleton() {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-card-border bg-surface p-4">
      <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
      <div className="flex flex-1 flex-col gap-2">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-3 w-1/2" />
      </div>
      <Skeleton className="h-6 w-20 rounded-full" />
    </div>
  )
}

/** Skeleton para tarjetas del dashboard. */
export function StatCardSkeleton() {
  return (
    <div className="rounded-xl border border-card-border bg-surface p-5">
      <Skeleton className="h-4 w-24 mb-3" />
      <Skeleton className="h-8 w-16" />
    </div>
  )
}
