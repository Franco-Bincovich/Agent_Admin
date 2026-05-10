'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { updateProfile } from '@/services/profileService';
import type { ApiError } from '@/types';

const FIELD_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] min-h-[44px]';
const FIELD_STYLE = {
  backgroundColor: 'var(--color-background)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text-primary)',
} as const;
const LABEL_STYLE = { color: 'var(--color-text-primary)' };
const ERROR_STYLE = { color: 'var(--color-error)' };
const CARD_STYLE = {
  backgroundColor: 'var(--color-surface)',
  borderColor: 'var(--color-border)',
} as const;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateNombre(v: string) {
  if (!v.trim()) return 'El nombre es obligatorio';
  if (v.trim().length < 2) return 'El nombre debe tener al menos 2 caracteres';
  return '';
}
function validateEmail(v: string) {
  if (!v.trim()) return 'El email es obligatorio';
  if (!EMAIL_RE.test(v)) return 'Ingresá un email válido';
  return '';
}
function validateUsername(v: string) {
  if (!v.trim()) return 'El username es obligatorio';
  if (v.trim().length < 3) return 'El username debe tener al menos 3 caracteres';
  if (!/^[a-zA-Z0-9_.-]+$/.test(v.trim())) return 'Solo letras, números, puntos, guiones y guiones bajos';
  return '';
}

interface PersonalForm { nombre: string; email: string; username: string }
type PersonalKey = keyof PersonalForm;
type PersonalErrors = Record<PersonalKey, string>;
type PersonalTouched = Record<PersonalKey, boolean>;

function validatePersonal(f: PersonalForm): PersonalErrors {
  return {
    nombre: validateNombre(f.nombre),
    email: validateEmail(f.email),
    username: validateUsername(f.username),
  };
}

const NO_ERRORS: PersonalErrors = { nombre: '', email: '', username: '' };
const NO_TOUCHED: PersonalTouched = { nombre: false, email: false, username: false };

interface Props {
  defaultValues: { nombre: string; email: string; username: string };
}

export default function PersonalSection({ defaultValues }: Props) {
  const [personal, setPersonal] = useState<PersonalForm>(defaultValues);
  const [errors, setErrors] = useState<PersonalErrors>(NO_ERRORS);
  const [touched, setTouched] = useState<PersonalTouched>(NO_TOUCHED);
  const [isSaving, setIsSaving] = useState(false);

  function handleChange(field: PersonalKey, value: string) {
    const next = { ...personal, [field]: value };
    setPersonal(next);
    if (touched[field]) {
      setErrors((prev) => ({ ...prev, [field]: validatePersonal(next)[field] }));
    }
  }

  function handleBlur(field: PersonalKey) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => ({ ...prev, [field]: validatePersonal(personal)[field] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const allErrors = validatePersonal(personal);
    setErrors(allErrors);
    setTouched({ nombre: true, email: true, username: true });
    if (Object.values(allErrors).some(Boolean)) return;
    setIsSaving(true);
    try {
      const updated = await updateProfile({
        nombre: personal.nombre.trim(),
        email: personal.email.trim(),
        username: personal.username.trim().toLowerCase(),
      });
      setPersonal({ nombre: updated.nombre, email: updated.email, username: updated.username ?? '' });
      toast.success('Perfil actualizado correctamente.');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo actualizar el perfil.');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="rounded-xl border p-6 space-y-4" style={CARD_STYLE}>
      <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Datos personales
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-nombre">Nombre</label>
          <input id="p-nombre" type="text" value={personal.nombre}
            onChange={(e) => handleChange('nombre', e.target.value)}
            onBlur={() => handleBlur('nombre')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.nombre && errors.nombre && <p className="text-xs" style={ERROR_STYLE}>{errors.nombre}</p>}
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-email">Email</label>
          <input id="p-email" type="email" value={personal.email}
            onChange={(e) => handleChange('email', e.target.value)}
            onBlur={() => handleBlur('email')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.email && errors.email && <p className="text-xs" style={ERROR_STYLE}>{errors.email}</p>}
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-username">Username</label>
          <input id="p-username" type="text" value={personal.username}
            onChange={(e) => handleChange('username', e.target.value)}
            onBlur={() => handleBlur('username')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.username && errors.username && <p className="text-xs" style={ERROR_STYLE}>{errors.username}</p>}
        </div>
        <Button type="submit" className="min-h-[44px]" disabled={isSaving}>
          {isSaving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Guardando...</> : 'Guardar cambios'}
        </Button>
      </form>
    </section>
  );
}
