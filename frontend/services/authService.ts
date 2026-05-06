import { get, post } from '@/services/api';
import type { TokenResponse, User, UserRole } from '@/types';

export async function login(email: string, password: string): Promise<TokenResponse> {
  return post<TokenResponse>('/api/v1/auth/login', { email, password });
}

export async function register(
  email: string,
  password: string,
  nombre: string,
  rol: UserRole,
): Promise<TokenResponse> {
  return post<TokenResponse>('/api/v1/auth/register', { email, password, nombre, rol });
}

export async function getMe(): Promise<User> {
  return get<User>('/api/v1/auth/me');
}

export function logout(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
