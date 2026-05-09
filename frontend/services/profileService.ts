import { get, put } from '@/services/api';
import type { Profile } from '@/types';

export interface UpdateProfilePayload {
  nombre?: string;
  email?: string;
  username?: string;
}

export interface ChangePasswordPayload {
  password_actual: string;
  password_nueva: string;
  confirmar_password: string;
}

export interface MessageResponse {
  message: string;
}

export async function getProfile(): Promise<Profile> {
  return get<Profile>('/api/v1/profile');
}

export async function updateProfile(payload: UpdateProfilePayload): Promise<Profile> {
  return put<Profile>('/api/v1/profile', payload);
}

export async function changePassword(payload: ChangePasswordPayload): Promise<MessageResponse> {
  return put<MessageResponse>('/api/v1/profile/password', payload);
}
