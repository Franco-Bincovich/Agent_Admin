import { useCallback, useEffect, useState } from 'react';
import { getProyectoDetalle } from '@/services/planificacionService';
import type { ProyectoDetalleResponse } from '@/types';

interface UseProyectoDetalleResult {
  proyecto: ProyectoDetalleResponse | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useProyectoDetalle(proyectoId: string): UseProyectoDetalleResult {
  const [proyecto, setProyecto] = useState<ProyectoDetalleResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProyecto = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProyectoDetalle(proyectoId);
      setProyecto(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al cargar el proyecto');
    } finally {
      setIsLoading(false);
    }
  }, [proyectoId]);

  useEffect(() => {
    fetchProyecto();
  }, [fetchProyecto]);

  return { proyecto, isLoading, error, refresh: fetchProyecto };
}
