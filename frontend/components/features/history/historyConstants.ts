import type { ActivityItem } from '@/types';

export const STATUS_BADGE: Record<string, { label: string; className: string }> = {
  procesando: { label: 'Procesando...', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  listo:      { label: 'Listo',         className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  error:      { label: 'Error',         className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

export const TEMPLATE_LABELS: Record<string, string> = {
  ejecutivo_oscuro: 'Ejecutivo oscuro',
  profesional_claro: 'Profesional claro',
  corporativo_neutro: 'Corporativo neutro',
};

export const TYPE_BADGE: Record<ActivityItem['tipo'], { label: string; className: string }> = {
  presentacion: { label: 'Presentación', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  documento:    { label: 'Documento',    className: 'bg-green-500/20 text-green-400 border-green-500/30' },
};

export function sanitizeFilename(name: string): string {
  return name
    .normalize('NFD')
    .replace(new RegExp('[\\u0300-\\u036f]', 'g'), '')
    .replace(/\s+/g, '_')
    .replace(/[^a-zA-Z0-9._-]/g, '');
}
