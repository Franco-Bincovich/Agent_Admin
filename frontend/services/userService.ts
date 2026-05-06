import { get, patch } from '@/services/api';
import type { User } from '@/types';

export async function getUsers(): Promise<User[]> {
  return get<User[]>('/api/v1/users');
}

export async function toggleUserActive(userId: string, activo: boolean): Promise<User> {
  return patch<User>(`/api/v1/users/${userId}/active`, { activo });
}
