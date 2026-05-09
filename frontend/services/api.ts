import type { ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

function clearSession(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers as Record<string, string> | undefined),
    },
  });

  if (response.status === 401) {
    clearSession();
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw (await response.json()) as ApiError;
  }

  if (!response.ok) {
    throw (await response.json()) as ApiError;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function get<T>(endpoint: string, options?: RequestInit): Promise<T> {
  return request<T>(endpoint, { ...options, method: 'GET' });
}

export function post<T>(endpoint: string, body: unknown, options?: RequestInit): Promise<T> {
  return request<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
}

export function patch<T>(endpoint: string, body: unknown, options?: RequestInit): Promise<T> {
  return request<T>(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) });
}

export function put<T>(endpoint: string, body: unknown, options?: RequestInit): Promise<T> {
  return request<T>(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
}

export function del<T>(endpoint: string, options?: RequestInit): Promise<T> {
  return request<T>(endpoint, { ...options, method: 'DELETE' });
}
