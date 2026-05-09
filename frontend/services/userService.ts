import { get, patch, post } from '@/services/api';
import type { User } from '@/types';

export interface CreateUserPayload {
  nombre: string;
  email: string;
  username: string;
  password: string;
  rol: 'administrador' | 'usuario';
}

export async function getUsers(): Promise<User[]> {
  return get<User[]>('/api/v1/users');
}

export async function createUser(payload: CreateUserPayload): Promise<User> {
  return post<User>('/api/v1/users', payload);
}

export async function toggleUserActive(userId: string, activo: boolean): Promise<User> {
  return patch<User>(`/api/v1/users/${userId}/active`, { activo });
}
