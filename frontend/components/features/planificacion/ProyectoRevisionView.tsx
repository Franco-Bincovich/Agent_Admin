'use client';

import { AlertTriangle } from 'lucide-react';
import type { ProyectoDetalleResponse, TareaResponse } from '@/types';
import AreaCrearForm from './AreaCrearForm';
import AreaEditCard from './AreaEditCard';
import TareaAreaSelect from './TareaAreaSelect';

interface Props {
  detalle: ProyectoDetalleResponse;
  onVerVisuales: () => void;
  onAreaCreada: () => void;
  onTareaActualizada: () => void;
}

const CONFIANZA_COLOR: Record<TareaResponse['confianza'], string> = {
  alta:  'var(--color-success)',
  media: 'var(--color-primary)',
  baja:  '#f59e0b',
};

const CONFIANZA_LABEL: Record<TareaResponse['confianza'], string> = {
  alta:  'Alta',
  media: 'Media',
  baja:  'Baja',
};

const ORIGEN_LABEL: Record<string, string> = { excel: 'Excel', mpp: 'MPP', pdf: 'PDF' };
const PRIORIDAD_LABEL: Record<string, string> = { alta: 'Alta', media: 'Media', baja: 'Baja' };

export default function ProyectoRevisionView({ detalle, onVerVisuales, onAreaCreada, onTareaActualizada }: Props) {
  const tareas = detalle.tareas.filter(t => !t.es_resumen);
  const tieneEstimadas = tareas.some(t => t.confianza !== 'alta' || t.fecha_estimada);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <div className="flex items-center gap-3 flex-wrap">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {detalle.nombre}
          </h2>
          {detalle.origen && (
            <span className="text-xs px-2 py-0.5 rounded-full border" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
              {ORIGEN_LABEL[detalle.origen] ?? detalle.origen}
            </span>
          )}
          {detalle.prioridad && (
            <span className="text-xs px-2 py-0.5 rounded-full border" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
              Prioridad {PRIORIDAD_LABEL[detalle.prioridad] ?? detalle.prioridad}
            </span>
          )}
        </div>
        {detalle.expediente && (
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Expediente: {detalle.expediente}</p>
        )}
      </div>

      {tieneEstimadas && (
        <div className="flex items-start gap-2 p-3 rounded-lg border" style={{ borderColor: '#f59e0b', backgroundColor: 'color-mix(in srgb, #f59e0b 8%, transparent)' }}>
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: '#f59e0b' }} />
          <p className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
            Algunas fechas fueron estimadas de la posición de las barras. Revisá las filas marcadas antes de continuar.
          </p>
        </div>
      )}

      <div className="rounded-lg border overflow-hidden" style={{ borderColor: 'var(--color-border)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ backgroundColor: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)' }}>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '80px' }}>WBS</th>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)' }}>Nombre</th>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '100px' }}>Inicio</th>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '100px' }}>Fin</th>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)' }}>Área</th>
                <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '90px' }}>Confianza</th>
              </tr>
            </thead>
            <tbody>
              {tareas.map((tarea) => (
                <tr
                  key={tarea.id}
                  style={{
                    borderBottom: '1px solid var(--color-border)',
                    backgroundColor: tarea.confianza === 'baja'
                      ? 'color-mix(in srgb, #f59e0b 8%, transparent)'
                      : 'transparent',
                  }}
                >
                  <td className="px-3 py-2" style={{ color: 'var(--color-text-secondary)' }}>{tarea.wbs}</td>
                  <td className="px-3 py-2" style={{ paddingLeft: `${12 + tarea.nivel * 12}px`, color: 'var(--color-text-primary)' }}>
                    {tarea.nombre}
                  </td>
                  <td className="px-3 py-2">
                    <span className="flex items-center gap-1" style={{ color: tarea.fecha_estimada ? 'var(--color-text-secondary)' : 'var(--color-text-primary)' }}>
                      {tarea.fecha_estimada && <AlertTriangle className="w-3 h-3 flex-shrink-0" style={{ color: '#f59e0b' }} />}
                      {tarea.fecha_inicio ?? '—'}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <span className="flex items-center gap-1" style={{ color: tarea.fecha_estimada ? 'var(--color-text-secondary)' : 'var(--color-text-primary)' }}>
                      {tarea.fecha_estimada && <AlertTriangle className="w-3 h-3 flex-shrink-0" style={{ color: '#f59e0b' }} />}
                      {tarea.fecha_fin ?? '—'}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <TareaAreaSelect tarea={tarea} areas={detalle.areas} proyectoId={detalle.id} onActualizada={onTareaActualizada} />
                  </td>
                  <td className="px-3 py-2">
                    <span className="text-xs font-medium" style={{ color: CONFIANZA_COLOR[tarea.confianza] }}>
                      {CONFIANZA_LABEL[tarea.confianza]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>Áreas detectadas</p>
        {detalle.areas.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {detalle.areas.map(area => (
              <AreaEditCard key={area.id} area={area} proyectoId={detalle.id} />
            ))}
          </div>
        )}
        <AreaCrearForm proyectoId={detalle.id} onCreada={onAreaCreada} />
      </div>

      <div className="flex justify-end">
        <button
          onClick={onVerVisuales}
          className="text-sm px-4 py-2 rounded-md"
          style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-bg)' }}
        >
          Ver visuales
        </button>
      </div>
    </div>
  );
}
