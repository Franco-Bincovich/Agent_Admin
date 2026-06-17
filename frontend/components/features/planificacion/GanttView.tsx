'use client';

import { useState } from 'react';
import type { ProyectoDetalleResponse, TareaResponse } from '@/types';
import { getQuarters, getQuarterWindow, isHiddenByCollapsed } from '@/utils/ganttUtils';
import GanttFilaTarea from './GanttFilaTarea';
import TareaAccionesPanel from './TareaAccionesPanel';
import ReprogramarTareaModal from './ReprogramarTareaModal';

interface Props {
  detalle: ProyectoDetalleResponse;
  onActualizada: () => void;
  zoom: 'anual' | 'cuatrimestral';
  offset: number;
}

function parseDate(s: string | null): number {
  return s ? new Date(s).getTime() : 0;
}

function axisYears(startMs: number, endMs: number): number[] {
  const from = new Date(startMs).getFullYear();
  const to   = new Date(endMs).getFullYear();
  const out: number[] = [];
  for (let y = from; y <= to; y++) out.push(y);
  return out;
}

export default function GanttView({ detalle, onActualizada, zoom, offset }: Props) {
  const [tareaSel, setTareaSel] = useState<TareaResponse | null>(null);
  const [reprogramando, setReprogramando] = useState<TareaResponse | null>(null);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  const areaColor: Record<string, string> = {};
  for (const a of detalle.areas) {
    if (a.color) areaColor[a.id] = a.color;
  }

  const dates = detalle.tareas
    .flatMap(t => [parseDate(t.fecha_inicio), parseDate(t.fecha_fin)])
    .filter(d => d > 0);

  const dataStart  = dates.length ? Math.min(...dates) : 0;
  const dataEnd    = dates.length ? Math.max(...dates) : 1;
  const win        = zoom === 'cuatrimestral' ? getQuarterWindow(offset) : null;
  const rangeStart = win?.start ?? dataStart;
  const rangeEnd   = win?.end   ?? dataEnd;
  const rangeMs    = (rangeEnd - rangeStart) || 1;

  const pct      = (ms: number) => ((ms - rangeStart) / rangeMs) * 100;
  const years    = axisYears(rangeStart, rangeEnd);
  const quarters = getQuarters(rangeStart, rangeEnd);
  const todayPct = ((Date.now() - rangeStart) / (rangeEnd - rangeStart)) * 100;

  return (
    <div className="rounded-lg border overflow-hidden" style={{ borderColor: 'var(--color-border)' }}>
      {/* Eje temporal */}
      <div
        className="flex border-b"
        style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}
      >
        <div
          className="w-64 flex-shrink-0 px-3 py-1.5 text-xs font-medium border-r"
          style={{ color: 'var(--color-text-secondary)', borderColor: 'var(--color-border)' }}
        >
          Tarea
        </div>
        <div className="flex-1 relative h-7 overflow-hidden min-w-96">
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
          {zoom === 'anual'
            ? years.map(y => {
                const left = pct(new Date(`${y}-01-01`).getTime());
                return left >= 0 && left <= 100 ? (
                  <span key={y} className="absolute top-1 text-xs select-none"
                    style={{ left: `${left}%`, transform: 'translateX(-50%)', color: 'var(--color-text-disabled)' }}>
                    {y}
                  </span>
                ) : null;
              })
            : quarters.map(q => (
                <span key={q.label} className="absolute top-1 text-xs select-none"
                  style={{ left: `${q.pct}%`, transform: 'translateX(-50%)', color: 'var(--color-text-disabled)' }}>
                  {q.label}
                </span>
              ))
          }
        </div>
      </div>

      {/* Filas de tareas */}
      <div className="overflow-x-auto">
        {detalle.tareas.filter(t => !isHiddenByCollapsed(t.wbs, collapsed)).map(tarea => {
          const color     = tarea.area_id ? (areaColor[tarea.area_id] ?? 'var(--color-primary)') : 'var(--color-primary)';
          const startMs   = parseDate(tarea.fecha_inicio);
          const endMs     = parseDate(tarea.fecha_fin);
          const hasBar    = startMs > 0 && endMs > 0;
          const isResumen = tarea.es_resumen;
          const startPct  = Math.max(0, pct(startMs));
          const widthPct  = Math.max(0, Math.min(100, pct(endMs)) - startPct);

          return (
            <GanttFilaTarea
              key={tarea.id}
              tarea={tarea}
              color={color}
              hasBar={hasBar}
              isResumen={isResumen}
              startPct={startPct}
              widthPct={widthPct}
              todayPct={todayPct}
              collapsed={collapsed.has(tarea.wbs)}
              onSelect={() => setTareaSel(tarea)}
              onToggleCollapse={() => setCollapsed(prev => {
                const next = new Set(prev);
                next.has(tarea.wbs) ? next.delete(tarea.wbs) : next.add(tarea.wbs);
                return next;
              })}
            />
          );
        })}
      </div>
      {tareaSel && (
        <TareaAccionesPanel
          open={!!tareaSel}
          onClose={() => setTareaSel(null)}
          proyectoId={detalle.id}
          tarea={tareaSel}
          onActualizada={onActualizada}
          onReprogramar={() => { setReprogramando(tareaSel); setTareaSel(null); }}
        />
      )}
      {reprogramando && (
        <ReprogramarTareaModal
          open={!!reprogramando}
          onClose={() => setReprogramando(null)}
          proyectoId={detalle.id}
          tarea={reprogramando}
          onReprogramada={onActualizada}
        />
      )}
    </div>
  );
}
