'use client';

import { useState } from 'react';
import { usePortfolioData } from '@/hooks/usePortfolioData';
import UnificadoLeyenda from './UnificadoLeyenda';
import type { AreaResponse, TareaResponse, Proyecto } from '@/types';
import { getQuarters, getQuarterWindow }             from '@/utils/ganttUtils';

const AREA_COLORS = ['#3B82F6','#10B981','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#F97316','#84CC16'];
const TODAY_PX_PCT = (rangeStart: number, rangeEnd: number) =>
  ((Date.now() - rangeStart) / (rangeEnd - rangeStart)) * 100;

const LABEL_W = 250;

function parseDate(s: string | null): number {
  return s ? new Date(s).getTime() : 0;
}

function getYears(start: number, end: number): number[] {
  const sy = new Date(start).getFullYear();
  const ey = new Date(end).getFullYear();
  return Array.from({ length: ey - sy + 1 }, (_, i) => sy + i);
}

interface AreaBlockProps {
  area: AreaResponse;
  tareas: TareaResponse[];
  color: string;
  pct: (ms: number) => number;
  todayPct: number;
  expanded: boolean;
  onToggle: () => void;
}

function AreaBlock({ area, tareas, color, pct, todayPct, expanded, onToggle }: AreaBlockProps) {
  const hoja    = tareas.filter(t => !t.es_resumen && t.fecha_inicio && t.fecha_fin);
  const ms0     = hoja.length ? Math.min(...hoja.map(t => parseDate(t.fecha_inicio))) : 0;
  const ms1     = hoja.length ? Math.max(...hoja.map(t => parseDate(t.fecha_fin))) : 0;
  const rowBase = { borderColor: 'var(--color-border)', minWidth: 600 };
  return (
    <div>
      <div className="flex items-center border-b" style={rowBase}>
        <div className="flex-shrink-0 flex items-center gap-2 px-4 py-2" style={{ width: LABEL_W }}>
          <button onClick={onToggle} className="text-xs flex-shrink-0 w-3" style={{ color: 'var(--color-text-disabled)' }}>
            {expanded ? '▾' : '▸'}
          </button>
          <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
          <span className="text-xs truncate" style={{ color: 'var(--color-text-primary)' }}>{area.nombre}</span>
        </div>
        <div className="flex-1 relative h-8 px-2" style={{ overflow: 'hidden' }}>
          {todayPct >= 0 && todayPct <= 100 && (
            <div style={{
              position: 'absolute', left: `${todayPct}%`,
              top: 0, width: 2, height: '100%',
              backgroundColor: '#EF4444', zIndex: 10, pointerEvents: 'none',
            }} />
          )}
          {ms0 > 0 && ms1 > 0 && (
            <div
              className="absolute top-1/2 -translate-y-1/2"
              style={{ left: `${pct(ms0)}%`, width: `${Math.max(pct(ms1) - pct(ms0), 0.5)}%`, height: 20, backgroundColor: color, borderRadius: 4 }}
            />
          )}
        </div>
      </div>
      {expanded && hoja.map(t => {
        const s = parseDate(t.fecha_inicio), e = parseDate(t.fecha_fin);
        return (
          <div key={t.id} className="flex items-center border-b" style={rowBase}>
            <div className="flex-shrink-0 text-xs truncate py-1" style={{ width: LABEL_W, paddingLeft: 44, color: 'var(--color-text-secondary)' }}>
              {t.nombre}
            </div>
            <div className="flex-1 relative h-6 px-2" style={{ overflow: 'hidden' }}>
              <div className="absolute top-1/2 -translate-y-1/2" style={{ left: `${pct(s)}%`, width: `${Math.max(pct(e) - pct(s), 0.5)}%`, height: 12, backgroundColor: color, opacity: 0.6, borderRadius: 2 }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface Props { proyectos: Proyecto[]; zoom: 'anual' | 'cuatrimestral'; offset: number }

export default function UnificadoView({ proyectos, zoom, offset }: Props) {
  const { detalles, isLoading } = usePortfolioData(proyectos);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const toggle = (id: string) => setExpanded(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });

  if (isLoading) return (
    <div className="space-y-2">
      {[0, 1, 2].map(i => <div key={i} className="h-10 rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />)}
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
    <div className="overflow-x-auto overflow-y-auto rounded-lg border" style={{ borderColor: 'var(--color-border)', maxHeight: '70vh' }}>
      {/* Header sticky */}
      <div className="flex sticky top-0 z-10" style={{ minWidth: 600, backgroundColor: 'var(--color-surface)' }}>
        <div className="flex-shrink-0 px-4 py-2 text-xs font-semibold border-r border-b" style={{ width: LABEL_W, color: 'var(--color-text-secondary)', borderColor: 'var(--color-border)' }}>
          PROYECTO · ÁREA
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
            <div className="absolute top-0 bottom-0" style={{ left: `${todayPct}%`, width: 2, backgroundColor: '#EF4444', opacity: 0.3 }} />
          )}
        </div>
      </div>
      {/* Project + area blocks */}
      {detalles.map((d, di) => {
        const projColor = AREA_COLORS[di % AREA_COLORS.length];
        return (
          <div key={d.id}>
            <div
              className="flex items-center border-b px-4 py-2"
              style={{ borderColor: 'var(--color-border)', minWidth: 600, backgroundColor: 'color-mix(in srgb, var(--color-surface) 95%, var(--color-border))' }}
            >
              <div className="w-2 h-2 rounded-full mr-2 flex-shrink-0" style={{ backgroundColor: projColor }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>{d.nombre}</span>
            </div>
            {d.areas.map((area, ai) => (
              <AreaBlock
                key={area.id}
                area={area}
                tareas={d.tareas.filter(t => t.area_id === area.id)}
                color={area.color ?? AREA_COLORS[ai % AREA_COLORS.length]}
                pct={pct}
                todayPct={todayPct}
                expanded={expanded.has(area.id)}
                onToggle={() => toggle(area.id)}
              />
            ))}
          </div>
        );
      })}
      <UnificadoLeyenda detalles={detalles} />
    </div>
  );
}
