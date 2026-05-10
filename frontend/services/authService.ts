import { get, post } from '@/services/api';
import type { User, UserRole } from '@/types';

export async function login(username: string, password: string): Promise<void> {
  await post<{ ok: boolean }>('/api/v1/auth/login', { username, password });
}

export async function register(
  email: string,
  password: string,
  nombre: string,
  rol: UserRole,
): Promise<void> {
  await post<{ ok: boolean }>('/api/v1/auth/register', { email, password, nombre, rol });
}

export async function getMe(): Promise<User> {
  return get<User>('/api/v1/auth/me');
}

export async function logout(): Promise<void> {
  try {
    await post<{ message: string }>('/api/v1/auth/logout', {});
  } catch {
    // ignore errors — session state is reset regardless
  }
}
