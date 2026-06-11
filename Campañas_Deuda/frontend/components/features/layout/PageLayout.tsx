import { cn } from '@/lib/utils'

interface PageLayoutProps {
  title: string
  description?: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
}

export function PageLayout({ title, description, action, children, className }: PageLayoutProps) {
  return (
    <div className={cn('flex flex-col gap-6 px-4 pt-16 pb-8 lg:px-8 lg:pt-8', className)}>
      {/* Header */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 lg:text-2xl">{title}</h1>
          {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
        </div>
        {action && <div className="mt-3 sm:mt-0 flex-shrink-0">{action}</div>}
      </div>

      {/* Content */}
      <div>{children}</div>
    </div>
  )
}
