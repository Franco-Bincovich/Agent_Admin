'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { createUser } from '@/services/userService';
import type { ApiError } from '@/types';
import {
  validate, EMPTY, NO_ERRORS, ALL_TOUCHED, NONE_TOUCHED,
} from './createUserFormTypes';
import type { FormState, TextKey, FormErrors, CreateRol, Params } from './createUserFormTypes';

export type { CreateRol, FormState, TextKey, FormErrors, Params };

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
