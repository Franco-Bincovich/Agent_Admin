'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { getMyActivity } from '@/services/activityService';
import type { ActivityItem, ApiError } from '@/types';

export function useActivity() {
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivity = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getMyActivity();
      setActivity(data);
    } catch (err) {
      const apiError = err as ApiError;
      const message = apiError?.message ?? 'No pudimos cargar tu actividad. Intentá de nuevo.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  return { activity, isLoading, error, refresh: fetchActivity };
}
