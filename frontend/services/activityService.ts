import type { ActivityItem, ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function getMyActivity(): Promise<ActivityItem[]> {
  const response = await fetch(`${BASE_URL}/api/v1/activity`, {
    method: 'GET',
    credentials: 'include',
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw (await response.json()) as ApiError;
  }

  if (!response.ok) {
    throw (await response.json()) as ApiError;
  }

  return response.json() as Promise<ActivityItem[]>;
}
