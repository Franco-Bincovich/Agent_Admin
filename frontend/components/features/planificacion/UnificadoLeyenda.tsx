import type { ProyectoDetalleResponse } from '@/types';

const AREA_COLORS = ['#3B82F6','#10B981','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#F97316','#84CC16'];

interface Props { detalles: ProyectoDetalleResponse[] }

export default function UnificadoLeyenda({ detalles }: Props) {
  return (
    <div className="flex flex-wrap gap-3 px-4 py-3 border-t" style={{ borderColor: 'var(--color-border)' }}>
      {detalles.flatMap((d, di) =>
        d.areas.map((area, ai) => {
          const c = area.color ?? AREA_COLORS[ai % AREA_COLORS.length];
          return (
            <div key={`${di}-${ai}`} className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: c }} />
              <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                {d.nombre} · {area.nombre}
              </span>
            </div>
          );
        })
      )}
    </div>
  );
}
