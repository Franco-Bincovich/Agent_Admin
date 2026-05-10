'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { createUser } from '@/services/userService';
import type { User, ApiError } from '@/types';

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

const EMPTY: FormState = { nombre: '', email: '', username: '', password: '', rol: 'usuario' };
const NO_ERRORS: FormErrors = { nombre: '', email: '', username: '', password: '' };
const ALL_TOUCHED: Record<TextKey, boolean> = { nombre: true, email: true, username: true, password: true };
const NONE_TOUCHED: Record<TextKey, boolean> = { nombre: false, email: false, username: false, password: false };
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(f: FormState): FormErrors {
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

interface Params {
  onClose: () => void;
  onCreated: (user: User) => void;
}

export function useCreateUserForm({ onClose, onCreated }: Params) {
  const [form, setForm]       = useState<FormState>(EMPTY);
  const [errors, setErrors]   = useState<FormErrors>(NO_ERRORS);
  const [touched, setTouched] = useState<Record<TextKey, boolean>>(NONE_TOUCHED);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(field: keyof FormState, value: string) {
    const next = { ...form, [field]: value } as FormState;
    setForm(next);
    if (field !== 'rol' && touched[field as TextKey]) {
      setErrors((prev) => ({ ...prev, [field]: validate(next)[field as TextKey] }));
    }
  }

  function handleBlur(field: TextKey) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => ({ ...prev, [field]: validate(form)[field] }));
  }

  function reset() {
    setForm(EMPTY);
    setErrors(NO_ERRORS);
    setTouched(NONE_TOUCHED);
    setIsSubmitting(false);
  }

  function handleClose() {
    if (isSubmitting) return;
    reset();
    onClose();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const allErrors = validate(form);
    setErrors(allErrors);
    setTouched(ALL_TOUCHED);
    if (Object.values(allErrors).some(Boolean)) return;
    setIsSubmitting(true);
    try {
      const newUser = await createUser({
        nombre:   form.nombre.trim(),
        email:    form.email.trim(),
        username: form.username.trim().toLowerCase(),
        password: form.password,
        rol:      form.rol,
      });
      toast.success(`Usuario ${newUser.nombre} creado exitosamente`);
      onCreated(newUser);
      reset();
      onClose();
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo crear el usuario.');
      setIsSubmitting(false);
    }
  }

  return { form, errors, touched, isSubmitting, handleChange, handleBlur, handleClose, handleSubmit };
}
