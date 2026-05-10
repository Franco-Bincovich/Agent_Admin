'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { changePassword } from '@/services/profileService';
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

function validatePasswordActual(v: string) {
  if (!v) return 'La contraseña actual es obligatoria';
  return '';
}
function validatePasswordNueva(v: string) {
  if (!v) return 'La nueva contraseña es obligatoria';
  if (v.length < 8) return 'La contraseña debe tener al menos 8 caracteres';
  return '';
}
function validateConfirmar(v: string, nueva: string) {
  if (!v) return 'Confirmá la contraseña';
  if (v !== nueva) return 'Las contraseñas no coinciden';
  return '';
}

interface PasswordForm { passwordActual: string; passwordNueva: string; confirmarPassword: string }
type PasswordKey = keyof PasswordForm;
type PasswordErrors = Record<PasswordKey, string>;
type PasswordTouched = Record<PasswordKey, boolean>;

function validatePasswordForm(f: PasswordForm): PasswordErrors {
  return {
    passwordActual: validatePasswordActual(f.passwordActual),
    passwordNueva: validatePasswordNueva(f.passwordNueva),
    confirmarPassword: validateConfirmar(f.confirmarPassword, f.passwordNueva),
  };
}

const EMPTY: PasswordForm = { passwordActual: '', passwordNueva: '', confirmarPassword: '' };
const NO_ERRORS: PasswordErrors = { passwordActual: '', passwordNueva: '', confirmarPassword: '' };
const NO_TOUCHED: PasswordTouched = { passwordActual: false, passwordNueva: false, confirmarPassword: false };

export default function PasswordSection() {
  const [password, setPassword] = useState<PasswordForm>(EMPTY);
  const [errors, setErrors] = useState<PasswordErrors>(NO_ERRORS);
  const [touched, setTouched] = useState<PasswordTouched>(NO_TOUCHED);
  const [isSaving, setIsSaving] = useState(false);

  function handleChange(field: PasswordKey, value: string) {
    const next = { ...password, [field]: value };
    setPassword(next);
    if (touched[field]) {
      setErrors((prev) => ({ ...prev, [field]: validatePasswordForm(next)[field] }));
    }
    if (field === 'passwordNueva' && touched.confirmarPassword) {
      setErrors((prev) => ({
        ...prev,
        confirmarPassword: validateConfirmar(password.confirmarPassword, value),
      }));
    }
  }

  function handleBlur(field: PasswordKey) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors((prev) => ({ ...prev, [field]: validatePasswordForm(password)[field] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const allErrors = validatePasswordForm(password);
    setErrors(allErrors);
    setTouched({ passwordActual: true, passwordNueva: true, confirmarPassword: true });
    if (Object.values(allErrors).some(Boolean)) return;
    setIsSaving(true);
    try {
      await changePassword({
        password_actual: password.passwordActual,
        password_nueva: password.passwordNueva,
        confirmar_password: password.confirmarPassword,
      });
      setPassword(EMPTY);
      setTouched(NO_TOUCHED);
      toast.success('Contraseña actualizada correctamente.');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo cambiar la contraseña.');
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="rounded-xl border p-6 space-y-4" style={CARD_STYLE}>
      <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Cambiar contraseña
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-actual">Contraseña actual</label>
          <input id="p-pwd-actual" type="password" value={password.passwordActual}
            onChange={(e) => handleChange('passwordActual', e.target.value)}
            onBlur={() => handleBlur('passwordActual')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.passwordActual && errors.passwordActual && <p className="text-xs" style={ERROR_STYLE}>{errors.passwordActual}</p>}
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-nueva">Nueva contraseña</label>
          <input id="p-pwd-nueva" type="password" placeholder="Mínimo 8 caracteres" value={password.passwordNueva}
            onChange={(e) => handleChange('passwordNueva', e.target.value)}
            onBlur={() => handleBlur('passwordNueva')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.passwordNueva && errors.passwordNueva && <p className="text-xs" style={ERROR_STYLE}>{errors.passwordNueva}</p>}
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-confirmar">Confirmar contraseña</label>
          <input id="p-pwd-confirmar" type="password" value={password.confirmarPassword}
            onChange={(e) => handleChange('confirmarPassword', e.target.value)}
            onBlur={() => handleBlur('confirmarPassword')} className={FIELD_CLASS} style={FIELD_STYLE} />
          {touched.confirmarPassword && errors.confirmarPassword && <p className="text-xs" style={ERROR_STYLE}>{errors.confirmarPassword}</p>}
        </div>
        <Button type="submit" className="min-h-[44px]" disabled={isSaving}>
          {isSaving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Cambiando...</> : 'Cambiar contraseña'}
        </Button>
      </form>
    </section>
  );
}
