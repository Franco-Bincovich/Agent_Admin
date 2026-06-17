'use client';

import { useState } from 'react';
import GanttView     from './GanttView';
import PlanillaView  from './PlanillaView';
import PortfolioView from './PortfolioView';
import UnificadoView from './UnificadoView';
import type { Proyecto, ProyectoDetalleResponse } from '@/types';
import { getOffsetLabel } from '@/utils/ganttUtils';

type ActiveTab = 'gantt' | 'planilla' | 'portfolio' | 'unificado';
type Zoom = 'anual' | 'cuatrimestral';

interface Props {
  detalle: ProyectoDetalleResponse;
  activeTab: ActiveTab;
  onActualizada: () => void;
  proyectos: Proyecto[];
}

export default function VisualesContainer({ detalle, activeTab, onActualizada, proyectos }: Props) {
  const [zoom, setZoom] = useState<Zoom>('anual');
  const [offset, setOffset] = useState(0);

  return (
    <div>
      <div className="flex items-center gap-2 justify-end mb-2">
        {zoom === 'cuatrimestral' && (
          <div className="flex items-center gap-2">
            <button onClick={() => setOffset(o => o - 1)}
              style={{ padding: '4px 8px', borderRadius: 6, border: '1px solid var(--color-border)', cursor: 'pointer', color: 'var(--color-text-secondary)' }}>
              ←
            </button>
            <span style={{ fontSize: 12, color: 'var(--color-text-secondary)', minWidth: 120, textAlign: 'center' }}>
              {getOffsetLabel(offset)}
            </span>
            <button onClick={() => setOffset(o => o + 1)}
              style={{ padding: '4px 8px', borderRadius: 6, border: '1px solid var(--color-border)', cursor: 'pointer', color: 'var(--color-text-secondary)' }}>
              →
            </button>
          </div>
        )}
        {(['anual', 'cuatrimestral'] as const).map(z => (
          <button key={z} onClick={() => setZoom(z)}
            style={{
              padding: '4px 12px', borderRadius: 6, fontSize: 12,
              backgroundColor: zoom === z ? 'var(--color-primary)' : 'transparent',
              color: zoom === z ? '#fff' : 'var(--color-text-secondary)',
              border: `1px solid ${zoom === z ? 'var(--color-primary)' : 'var(--color-border)'}`,
              cursor: 'pointer',
            }}>
            {z === 'anual' ? 'Año' : 'Cuatrimestre'}
          </button>
        ))}
      </div>
      {activeTab === 'gantt'     && <GanttView    detalle={detalle} onActualizada={onActualizada} zoom={zoom} offset={offset} />}
      {activeTab === 'planilla'  && <PlanillaView  detalle={detalle} />}
      {activeTab === 'portfolio' && <PortfolioView proyectos={proyectos} zoom={zoom} offset={offset} />}
      {activeTab === 'unificado' && <UnificadoView proyectos={proyectos} zoom={zoom} offset={offset} />}
    </div>
  );
}
