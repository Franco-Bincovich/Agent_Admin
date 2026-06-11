'use client';

import { useState, useEffect, useMemo } from 'react';
import { getProyectoDetalle } from '@/services/planificacionService';
import type { Proyecto, ProyectoDetalleResponse } from '@/types';

export const AREA_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
  '#8B5CF6', '#06B6D4', '#F97316', '#84CC16',
];

export function usePortfolioData(proyectos: Proyecto[]) {
  const [detalles, setDetalles] = useState<ProyectoDetalleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listos = useMemo(
    () => proyectos.filter(p => p.estado === 'listo' && p.fecha_inicio && p.fecha_fin),
    [proyectos],
  );
  const listosKey = useMemo(() => listos.map(p => p.id).sort().join(','), [listos]);

  useEffect(() => {
    if (listos.length === 0) {
      setDetalles([]);
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    Promise.all(listos.map(p => getProyectoDetalle(p.id)))
      .then(results => {
        if (!cancelled) { setDetalles(results); setIsLoading(false); }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Error al cargar proyectos');
          setIsLoading(false);
        }
      });
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listosKey]);

  return { detalles, isLoading, error };
}
