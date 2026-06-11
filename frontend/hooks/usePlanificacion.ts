'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { getProyectos } from '@/services/planificacionService';
import type { Proyecto, ApiError } from '@/types';

export function usePlanificacion() {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchTrigger, setFetchTrigger] = useState(0);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout>;
    let attempts = 0;
    let interval = 3000;

    const poll = async () => {
      if (cancelled) return;
      try {
        const data = await getProyectos();
        if (cancelled) return;
        setProyectos(data);
        if (!data.some((p) => p.estado === 'procesando') || attempts >= 60) return;
      } catch {}
      attempts += 1;
      interval = Math.min(interval * 1.5, 15000);
      timeoutId = setTimeout(poll, interval);
    };

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getProyectos();
        if (cancelled) return;
        setProyectos(data);
        if (data.some((p) => p.estado === 'procesando')) {
          timeoutId = setTimeout(poll, interval);
        }
      } catch (err) {
        if (cancelled) return;
        const msg =
          (err as ApiError)?.message ?? 'No pudimos cargar los proyectos. Intentá de nuevo.';
        setError(msg);
        toast.error(msg);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [fetchTrigger]);

  const refresh = useCallback(() => setFetchTrigger((t) => t + 1), []);

  return { proyectos, isLoading, error, refresh };
}
