'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import type { ProyectoDetalleResponse } from '@/types';
import { getQuarters, getQuarterWindow, getBorderColor, isHiddenByCollapsed } from '@/utils/ganttUtils';

interface Props {
  detalle: ProyectoDetalleResponse;
  onMarcar: (tareaId: string, completada: boolean) => Promise<void>;
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

export default function GanttView({ detalle, onMarcar, zoom, offset }: Props) {
  const [marcandoId, setMarcandoId] = useState<string | null>(null);
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
          const loading   = marcandoId === tarea.id;

          return (
            <div
              key={tarea.id}
              className="flex border-b"
              onClick={!isResumen ? async () => {
                setMarcandoId(tarea.id);
                try { await onMarcar(tarea.id, !tarea.completada); }
                catch { toast.error('Error al actualizar la tarea'); }
                finally { setMarcandoId(null); }
              } : undefined}
              title={!isResumen ? (tarea.completada ? 'Marcar como pendiente' : 'Marcar como completada') : undefined}
              style={{
                borderColor: 'var(--color-border)',
                opacity: loading ? 0.6 : tarea.completada ? 0.4 : 1,
                cursor: isResumen ? 'default' : loading ? 'wait' : 'pointer',
              }}
            >
              <div
                className="w-64 flex-shrink-0 flex items-center gap-1.5 py-1.5 border-r text-xs"
                onClick={isResumen ? () => setCollapsed(prev => {
                  const next = new Set(prev);
                  next.has(tarea.wbs) ? next.delete(tarea.wbs) : next.add(tarea.wbs);
                  return next;
                }) : undefined}
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
                    {collapsed.has(tarea.wbs) ? '▶' : '▼'}
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
                      left:            `${Math.max(0, pct(startMs))}%`,
                      width:           `${Math.max(0, Math.min(100, pct(endMs)) - Math.max(0, pct(startMs)))}%`,
                      height:          isResumen ? '5px' : '12px',
                      backgroundColor: isResumen ? 'var(--color-border)' : color,
                      minWidth:        '2px',
                      border:          isResumen ? 'none' : `2px solid ${getBorderColor(tarea.completada, tarea.completada_en, tarea.fecha_fin)}`,
                    }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
