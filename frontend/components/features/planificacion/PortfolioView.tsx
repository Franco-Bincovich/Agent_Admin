'use client';

import { usePortfolioData } from '@/hooks/usePortfolioData';
import type { Proyecto } from '@/types';
import { getQuarters, getQuarterWindow } from '@/utils/ganttUtils';

const AREA_COLORS = ['#3B82F6','#10B981','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#F97316','#84CC16'];
const TODAY_PX_PCT = (rangeStart: number, rangeEnd: number) =>
  ((Date.now() - rangeStart) / (rangeEnd - rangeStart)) * 100;

const LABEL_W = 200;

function parseDate(s: string | null): number {
  return s ? new Date(s).getTime() : 0;
}

function getYears(start: number, end: number): number[] {
  const sy = new Date(start).getFullYear();
  const ey = new Date(end).getFullYear();
  return Array.from({ length: ey - sy + 1 }, (_, i) => sy + i);
}

interface Props { proyectos: Proyecto[]; zoom: 'anual' | 'cuatrimestral'; offset: number }

export default function PortfolioView({ proyectos, zoom, offset }: Props) {
  const { detalles, isLoading } = usePortfolioData(proyectos);

  if (isLoading) return (
    <div className="space-y-2">
      {[0, 1, 2].map(i => (
        <div key={i} className="h-10 rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
      ))}
    </div>
  );

  if (detalles.length === 0) return (
    <p className="text-sm py-8 text-center" style={{ color: 'var(--color-text-secondary)' }}>
      No hay proyectos listos todavía.
    </p>
  );

  const allMs      = detalles.flatMap(d => [parseDate(d.fecha_inicio), parseDate(d.fecha_fin)]).filter(ms => ms > 0);
  const dataStart  = Math.min(...allMs);
  const dataEnd    = Math.max(...allMs);
  const win        = zoom === 'cuatrimestral' ? getQuarterWindow(offset) : null;
  const rangeStart = win?.start ?? dataStart;
  const rangeEnd   = win?.end   ?? dataEnd;
  const rangeMs    = rangeEnd - rangeStart || 1;
  const pct        = (ms: number) => ((ms - rangeStart) / rangeMs) * 100;
  const years      = getYears(rangeStart, rangeEnd);
  const quarters   = getQuarters(rangeStart, rangeEnd);
  const todayPct   = TODAY_PX_PCT(rangeStart, rangeEnd);

  return (
    <div className="overflow-x-auto rounded-lg border" style={{ borderColor: 'var(--color-border)' }}>
      {/* Header sticky */}
      <div className="flex sticky top-0 z-10" style={{ minWidth: 600, backgroundColor: 'var(--color-surface)' }}>
        <div
          className="flex-shrink-0 px-4 py-2 text-xs font-semibold border-r border-b"
          style={{ width: LABEL_W, color: 'var(--color-text-secondary)', borderColor: 'var(--color-border)' }}
        >
          PROYECTO
        </div>
        <div className="flex-1 relative h-8 border-b" style={{ borderColor: 'var(--color-border)', overflow: 'hidden' }}>
          {zoom === 'anual'
            ? years.map(yr => {
                const leftPct = pct(new Date(yr, 0, 1).getTime());
                if (leftPct < 0 || leftPct > 100) return null;
                return (
                  <span key={yr} className="absolute text-xs"
                    style={{ left: `${leftPct}%`, top: 6, transform: 'translateX(-50%)', color: 'var(--color-text-disabled)' }}>
                    {yr}
                  </span>
                );
              })
            : quarters.map(q => (
                <span key={q.label} className="absolute text-xs"
                  style={{ left: `${q.pct}%`, top: 6, transform: 'translateX(-50%)', color: 'var(--color-text-disabled)' }}>
                  {q.label}
                </span>
              ))
          }
          {todayPct >= 0 && todayPct <= 100 && (
            <div
              className="absolute top-0 bottom-0"
              style={{ left: `${todayPct}%`, width: 2, backgroundColor: '#EF4444', opacity: 0.8 }}
            />
          )}
        </div>
      </div>
      {/* Project rows */}
      {detalles.map((d, idx) => {
        const color    = AREA_COLORS[idx % AREA_COLORS.length];
        const startMs  = parseDate(d.fecha_inicio);
        const endMs    = parseDate(d.fecha_fin);
        const hoja     = d.tareas.filter(t => !t.es_resumen);
        const progress = hoja.length > 0 ? hoja.filter(t => t.completada).length / hoja.length : 0;
        const barLeft  = `${pct(startMs)}%`;
        const barSpan  = pct(endMs) - pct(startMs);
        return (
          <div
            key={d.id}
            className="flex items-stretch border-b last:border-b-0"
            style={{ borderColor: 'var(--color-border)', minWidth: 600 }}
          >
            <div
              className="flex-shrink-0 px-4 py-3 border-r flex items-start gap-2"
              style={{ width: LABEL_W, borderColor: 'var(--color-border)' }}
            >
              <div className="w-2 h-2 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: color }} />
              <div>
                <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>{d.nombre}</p>
                {d.expediente && (
                  <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{d.expediente}</p>
                )}
              </div>
            </div>
            <div className="flex-1 relative px-2" style={{ minHeight: 52, overflow: 'hidden' }}>
              {todayPct >= 0 && todayPct <= 100 && (
                <div style={{
                  position: 'absolute', left: `${todayPct}%`,
                  top: 0, width: 2, height: '100%',
                  backgroundColor: '#EF4444', zIndex: 10, pointerEvents: 'none',
                }} />
              )}
              <div
                className="absolute"
                style={{ left: barLeft, width: `${Math.max(barSpan, 0.5)}%`, top: 12, height: 28, backgroundColor: color, opacity: 0.15, borderRadius: 6 }}
              />
              <div
                className="absolute"
                style={{ left: barLeft, width: `${Math.max(barSpan * progress, progress > 0 ? 0.5 : 0)}%`, top: 36, height: 4, backgroundColor: color, borderRadius: 6 }}
              />
            </div>
          </div>
        );
      })}
      {/* Legend */}
      <div className="flex flex-wrap gap-3 px-4 py-3 border-t" style={{ borderColor: 'var(--color-border)' }}>
        {detalles.map((d, idx) => (
          <div key={d.id} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: AREA_COLORS[idx % AREA_COLORS.length] }} />
            <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
              {d.nombre}{d.expediente ? ` · ${d.expediente}` : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
