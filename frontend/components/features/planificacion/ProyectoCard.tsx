'use client';

import { useRouter } from 'next/navigation';
import { Loader2, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import type { Proyecto, ProyectoEstado } from '@/types';
import { deleteProyecto } from '@/services/planificacionService';

interface Props { proyecto: Proyecto; onDeleted: () => void; }

const ESTADO_MAP: Record<ProyectoEstado, { label: string; color: string }> = {
  procesando: { label: 'Procesando', color: 'var(--color-accent)'  },
  listo:      { label: 'Listo',      color: 'var(--color-success)' },
  error:      { label: 'Error',      color: 'var(--color-error)'   },
};

const fmtDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';

export default function ProyectoCard({ proyecto, onDeleted }: Props) {
  const router = useRouter();
  const { label, color } = ESTADO_MAP[proyecto.estado];

  async function handleDelete(e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm(`¿Eliminar proyecto "${proyecto.nombre}"? Esta acción no se puede deshacer.`)) return;
    try {
      await deleteProyecto(proyecto.id);
      onDeleted();
    } catch {
      toast.error('Error al eliminar el proyecto');
    }
  }

  return (
    <Card
      onClick={() => router.push(`/planificacion/${proyecto.id}`)}
      className="cursor-pointer transition-shadow hover:shadow-md"
      style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <span className="font-medium text-sm leading-snug" style={{ color: 'var(--color-text-primary)' }}>
            {proyecto.nombre}
          </span>
          <div className="flex items-center gap-1 shrink-0">
            <span
              className="text-xs px-2 py-0.5 rounded-full border"
              style={{ backgroundColor: `color-mix(in srgb, ${color} 15%, transparent)`, color, borderColor: color }}
            >
              {label}
            </span>
            <button
              onClick={handleDelete}
              className="p-1 rounded hover:bg-red-50"
              aria-label="Eliminar proyecto"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
            </button>
          </div>
        </div>
        {proyecto.expediente && (
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
            Exp. {proyecto.expediente}
          </p>
        )}
      </CardHeader>

      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          {proyecto.prioridad && (
            <Badge variant="outline" className="text-xs capitalize">{proyecto.prioridad}</Badge>
          )}
          <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            {fmtDate(proyecto.fecha_inicio)} → {fmtDate(proyecto.fecha_fin)}
          </span>
        </div>
        {proyecto.estado === 'procesando' && (
          <div className="flex items-center gap-1.5" style={{ color: 'var(--color-accent)' }}>
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span className="text-xs font-medium">Procesando cronograma…</span>
          </div>
        )}
        {proyecto.estado === 'error' && proyecto.error_detalle && (
          <p className="text-xs" style={{ color: 'var(--color-error)' }}>{proyecto.error_detalle}</p>
        )}
      </CardContent>
    </Card>
  );
}
