import type { GenerationStatus, GenerationTemplate } from '@/types';

export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const STATUS_LABELS: Record<GenerationStatus, string> = {
  procesando: 'Procesando...',
  listo: 'Listo',
  error: 'Error',
};

export function formatStatus(status: GenerationStatus): string {
  return STATUS_LABELS[status];
}

const TEMPLATE_LABELS: Record<GenerationTemplate, string> = {
  ejecutivo_oscuro: 'Ejecutivo oscuro',
  profesional_claro: 'Profesional claro',
  corporativo_neutro: 'Corporativo neutro',
};

export function formatTemplate(template: GenerationTemplate): string {
  return TEMPLATE_LABELS[template];
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
}
