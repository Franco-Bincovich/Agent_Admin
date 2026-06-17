export interface QuarterMark {
  label: string;
  pct: number;
}

export function getQuarters(rangeStart: number, rangeEnd: number): QuarterMark[] {
  const quarters: QuarterMark[] = [];
  const d = new Date(rangeStart);
  d.setDate(1);
  d.setMonth(Math.floor(d.getMonth() / 4) * 4);
  while (d.getTime() < rangeEnd) {
    const q = Math.floor(d.getMonth() / 4) + 1;
    quarters.push({
      label: `Q${q} ${d.getFullYear()}`,
      pct: ((d.getTime() - rangeStart) / (rangeEnd - rangeStart)) * 100,
    });
    d.setMonth(d.getMonth() + 4);
  }
  return quarters;
}

export function getQuarterWindow(offset: number): { start: number; end: number } {
  const now     = new Date();
  const q       = Math.floor(now.getMonth() / 4) + offset;
  const year    = now.getFullYear() + Math.floor(q / 3);
  const qInYear = ((q % 3) + 3) % 3;
  const start   = new Date(year, qInYear * 4, 1).getTime();
  const end     = new Date(year, (qInYear + 2) * 4, 1).getTime();
  return { start, end };
}

export function getBorderColor(
  completada: boolean,
  completada_en: string | null,
  fecha_fin: string | null,
  reprogramada: boolean,
): string {
  if (reprogramada) return '#B45309';
  if (!fecha_fin) return '#00FF00';
  const fin = new Date(fecha_fin).getTime();
  const hoy = Date.now();
  const diasRestantes = (fin - hoy) / (1000 * 60 * 60 * 24);
  if (completada) {
    const completadaEn = completada_en ? new Date(completada_en).getTime() : hoy;
    const diasAnticipacion = (fin - completadaEn) / (1000 * 60 * 60 * 24);
    if (diasAnticipacion <= 0) return '#FF0000';
    if (diasAnticipacion <= 45) return '#FFD700';
    return '#00FF00';
  }
  if (diasRestantes < 0) return '#FF0000';
  if (diasRestantes <= 45) return '#FFD700';
  return '#00FF00';
}

export function isHiddenByCollapsed(wbs: string, collapsed: Set<string>): boolean {
  for (const cWbs of collapsed) {
    if (wbs !== cWbs && wbs.startsWith(cWbs + '.')) return true;
  }
  return false;
}

export function getOffsetLabel(offset: number): string {
  const now     = new Date();
  const q       = Math.floor(now.getMonth() / 4) + offset;
  const year    = now.getFullYear() + Math.floor(q / 3);
  const qInYear = ((q % 3) + 3) % 3;
  const qNum    = qInYear + 1;
  return `Q${qNum} ${year} – Q${qNum < 3 ? qNum + 1 : 1} ${qNum < 3 ? year : year + 1}`;
}
