'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { getMyGenerations } from '@/services/generationService';
import type { Generation, ApiError } from '@/types';

export function useGenerations() {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGenerations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getMyGenerations();
      setGenerations(data);
    } catch (err) {
      const apiError = err as ApiError;
      const message =
        apiError?.message ?? 'No pudimos cargar tus generaciones. Intentá de nuevo.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGenerations();
  }, [fetchGenerations]);

  return {
    generations,
    isLoading,
    error,
    fetchGenerations,
    refresh: fetchGenerations,
  };
}
