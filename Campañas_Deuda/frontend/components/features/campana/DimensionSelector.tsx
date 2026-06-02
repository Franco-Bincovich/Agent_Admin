import { cn } from '@/lib/utils'

interface Option {
  value: string
  label: string
}

interface DimensionSelectorProps {
  id: string
  label: string
  description?: string
  options: Option[]
  value: string
  onChange: (value: string) => void
  required?: boolean
}

export function DimensionSelector({
  id,
  label,
  description,
  options,
  value,
  onChange,
  required,
}: DimensionSelectorProps) {
  return (
    <fieldset className="flex flex-col gap-3">
      <legend className="text-sm font-semibold text-gray-800">
        {label}
        {required && (
          <span className="ml-1 text-red-500" aria-label="obligatorio">
            *
          </span>
        )}
      </legend>
      {description && <p className="text-xs text-gray-500 -mt-1">{description}</p>}

      <div className="flex flex-wrap gap-2" role="radiogroup" aria-labelledby={`${id}-legend`}>
        {options.map((opt) => {
          const checked = value === opt.value
          return (
            <label
              key={opt.value}
              className={cn(
                'flex cursor-pointer items-center gap-2 rounded-lg border px-4 py-2.5',
                'text-sm font-medium transition-all select-none min-h-[44px]',
                checked
                  ? 'border-secondary bg-secondary/10 text-secondary'
                  : 'border-card-border bg-surface text-gray-700 hover:border-secondary/50 hover:bg-background'
              )}
            >
              <input
                type="radio"
                name={id}
                value={opt.value}
                checked={checked}
                onChange={() => onChange(opt.value)}
                className="sr-only"
                required={required && !value}
              />
              {opt.label}
            </label>
          )
        })}
      </div>
    </fieldset>
  )
}
