import type { User } from '@/types';

export type CreateRol = 'administrador' | 'usuario';

export interface FormState {
  nombre: string;
  email: string;
  username: string;
  password: string;
  rol: CreateRol;
}

export type TextKey = Exclude<keyof FormState, 'rol'>;
export type FormErrors = Record<TextKey, string>;

export const EMPTY: FormState = { nombre: '', email: '', username: '', password: '', rol: 'usuario' };
export const NO_ERRORS: FormErrors = { nombre: '', email: '', username: '', password: '' };
export const ALL_TOUCHED: Record<TextKey, boolean> = { nombre: true, email: true, username: true, password: true };
export const NONE_TOUCHED: Record<TextKey, boolean> = { nombre: false, email: false, username: false, password: false };
export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validate(f: FormState): FormErrors {
  return {
    nombre: !f.nombre.trim()
      ? 'El nombre es obligatorio'
      : f.nombre.trim().length < 2
      ? 'El nombre debe tener al menos 2 caracteres'
      : '',
    email: !f.email.trim()
      ? 'El email es obligatorio'
      : !EMAIL_RE.test(f.email)
      ? 'Ingresá un email válido'
      : '',
    username: !f.username.trim()
      ? 'El username es obligatorio'
      : f.username.trim().length < 3
      ? 'El username debe tener al menos 3 caracteres'
      : !/^[a-zA-Z0-9_.-]+$/.test(f.username.trim())
      ? 'Solo letras, números, puntos, guiones y guiones bajos'
      : '',
    password: !f.password
      ? 'La contraseña es obligatoria'
      : f.password.length < 8
      ? 'La contraseña debe tener al menos 8 caracteres'
      : '',
  };
}

export interface Params {
  onClose: () => void;
  onCreated: (user: User) => void;
}
