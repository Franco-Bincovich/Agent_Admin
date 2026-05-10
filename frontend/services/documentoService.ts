import { get } from '@/services/api';
import type { Documento, ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function getMyDocumentos(): Promise<Documento[]> {
  return get<Documento[]>('/api/v1/documentos');
}

export async function getDocumento(id: string): Promise<Documento> {
  return get<Documento>(`/api/v1/documentos/${id}`);
}

export async function createDocumento(formData: FormData): Promise<Documento> {
  const response = await fetch(`${BASE_URL}/api/v1/documentos`, {
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

  return response.json() as Promise<Documento>;
}
