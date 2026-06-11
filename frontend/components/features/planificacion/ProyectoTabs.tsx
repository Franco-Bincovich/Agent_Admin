'use client';

interface Props {
  activeTab: 'revision' | 'gantt' | 'planilla' | 'portfolio' | 'unificado';
  onChange: (tab: Props['activeTab']) => void;
}

type Tab = Props['activeTab'];

const TABS: { id: Tab; label: string }[] = [
  { id: 'revision',  label: 'Revisión'  },
  { id: 'gantt',     label: 'Gantt'     },
  { id: 'planilla',  label: 'Planilla'  },
  { id: 'portfolio', label: 'Portfolio' },
  { id: 'unificado', label: 'Unificado' },
];

export default function ProyectoTabs({ activeTab, onChange }: Props) {
  return (
    <div className="border-b" style={{ borderColor: 'var(--color-border)' }}>
      <div className="flex gap-1 overflow-x-auto pb-px">
        {TABS.map(({ id, label }) => {
          const active = id === activeTab;
          return (
            <button
              key={id}
              onClick={() => onChange(id)}
              className="px-4 py-2 text-sm rounded-t-md border flex-shrink-0 transition-colors"
              style={{
                borderColor:     active ? 'var(--color-primary)' : 'var(--color-border)',
                backgroundColor: active ? 'color-mix(in srgb, var(--color-primary) 12%, transparent)' : 'transparent',
                color:           active ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              }}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
