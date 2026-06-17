'use client';

import type { ProyectoDetalleResponse } from '@/types';

interface Props {
  detalle: ProyectoDetalleResponse;
}

function duracionDias(inicio: string | null, fin: string | null): string {
  if (!inicio || !fin) return '—';
  const diff = new Date(fin).getTime() - new Date(inicio).getTime();
  return `${Math.round(diff / 86_400_000)} d`;
}

export default function PlanillaView({ detalle }: Props) {
  return (
    <div className="rounded-lg border overflow-hidden" style={{ borderColor: 'var(--color-border)' }}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm" style={{ backgroundColor: 'var(--color-surface)' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface)' }}>
              <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '80px' }}>WBS</th>
              <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)' }}>Nombre</th>
              <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '100px' }}>Inicio</th>
              <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '100px' }}>Fin</th>
              <th className="text-left px-3 py-2 font-medium" style={{ color: 'var(--color-text-secondary)', width: '80px' }}>Duración</th>
            </tr>
          </thead>
          <tbody>
            {detalle.tareas.map(tarea => {
              const isResumen  = tarea.es_resumen;
              const textColor  = tarea.completada
                ? 'var(--color-text-disabled)'
                : isResumen
                ? 'var(--color-text-primary)'
                : 'var(--color-text-secondary)';
              const decoration = tarea.completada ? 'line-through' : 'none';

              return (
                <tr
                  key={tarea.id}
                  style={{ borderBottom: '1px solid var(--color-border)' }}
                >
                  <td className="px-3 py-2" style={{ color: 'var(--color-text-secondary)', textDecoration: decoration }}>
                    {tarea.wbs}
                  </td>
                  <td
                    className="px-3 py-2"
                    style={{
                      paddingLeft:    `${12 + tarea.nivel * 12}px`,
                      color:          textColor,
                      fontWeight:     isResumen ? 700 : 400,
                      textDecoration: decoration,
                    }}
                  >
                    {tarea.nombre}
                  </td>
                  <td className="px-3 py-2" style={{ color: textColor, textDecoration: decoration }}>{tarea.fecha_inicio ?? '—'}</td>
                  <td className="px-3 py-2" style={{ color: textColor, textDecoration: decoration }}>{tarea.fecha_fin ?? '—'}</td>
                  <td className="px-3 py-2" style={{ color: 'var(--color-text-disabled)' }}>
                    {duracionDias(tarea.fecha_inicio, tarea.fecha_fin)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
