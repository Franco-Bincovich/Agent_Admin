import { get } from '@/services/api';
import type { Generation, ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function getMyGenerations(): Promise<Generation[]> {
  return get<Generation[]>('/api/v1/generations');
}

export async function getGeneration(id: string): Promise<Generation> {
  return get<Generation>(`/api/v1/generations/${id}`);
}

export async function createGeneration(formData: FormData): Promise<Generation> {
  const response = await fetch(`${BASE_URL}/api/v1/generations`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
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

  return response.json() as Promise<Generation>;
}
