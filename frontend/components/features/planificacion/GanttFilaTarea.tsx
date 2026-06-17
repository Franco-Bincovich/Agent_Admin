'use client';

import type { TareaResponse } from '@/types';
import { getBorderColor } from '@/utils/ganttUtils';

interface Props {
  tarea: TareaResponse;
  color: string;              // color de área ya resuelto
  hasBar: boolean;
  isResumen: boolean;
  startPct: number;           // Math.max(0, pct(startMs))
  widthPct: number;           // Math.max(0, Math.min(100, pct(endMs)) - Math.max(0, pct(startMs)))
  todayPct: number;
  collapsed: boolean;         // si este wbs está colapsado (para la flechita)
  onSelect: () => void;       // clic en fila no-resumen → abre panel
  onToggleCollapse: () => void; // clic en fila resumen → colapsa/expande
}

export default function GanttFilaTarea({
  tarea, color, hasBar, isResumen, startPct, widthPct, todayPct, collapsed,
  onSelect, onToggleCollapse,
}: Props) {
  return (
    <div
      className="flex border-b"
      onClick={!isResumen ? onSelect : undefined}
      title={!isResumen ? 'Ver acciones' : undefined}
      style={{
        borderColor: 'var(--color-border)',
        opacity: tarea.completada ? 0.4 : 1,
        cursor: isResumen ? 'default' : 'pointer',
      }}
    >
      <div
        className="w-64 flex-shrink-0 flex items-center gap-1.5 py-1.5 border-r text-xs"
        onClick={isResumen ? onToggleCollapse : undefined}
        style={{
          paddingLeft:  `${8 + tarea.nivel * 12}px`,
          paddingRight: '8px',
          borderColor:  'var(--color-border)',
          color: tarea.completada ? 'var(--color-text-disabled)' : 'var(--color-text-primary)',
          cursor: isResumen ? 'pointer' : undefined,
        }}
      >
        {isResumen && (
          <span style={{ marginRight: 4, fontSize: 10, color: 'var(--color-text-secondary)' }}>
            {collapsed ? '▶' : '▼'}
          </span>
        )}
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
        <span className={`truncate${isResumen ? ' font-medium' : ''}`}>{tarea.nombre}</span>
      </div>

      <div className="flex-1 relative min-w-96 h-8 overflow-hidden">
        {todayPct >= 0 && todayPct <= 100 && (
          <div style={{
            position: 'absolute',
            left: `${todayPct}%`,
            top: 0,
            width: 2,
            height: '100%',
            backgroundColor: '#EF4444',
            zIndex: 10,
            pointerEvents: 'none',
          }} />
        )}
        {hasBar && (
          <div
            className="absolute top-1/2 -translate-y-1/2 rounded"
            style={{
              left:            `${startPct}%`,
              width:           `${widthPct}%`,
              height:          isResumen ? '5px' : '12px',
              backgroundColor: isResumen ? 'var(--color-border)' : color,
              minWidth:        '2px',
              border:          isResumen ? 'none' : `2px solid ${getBorderColor(tarea.completada, tarea.completada_en, tarea.fecha_fin, tarea.reprogramada)}`,
            }}
          />
        )}
        {hasBar && !isResumen && (
          <span
            className="absolute top-1/2 -translate-y-1/2 select-none"
            style={{
              left: `calc(${startPct + widthPct}% + 4px)`,
              fontSize: 10,
              color: 'var(--color-text-secondary)',
              whiteSpace: 'nowrap',
              pointerEvents: 'none',
            }}
          >
            {tarea.progreso}%
          </span>
        )}
      </div>
    </div>
  );
}
