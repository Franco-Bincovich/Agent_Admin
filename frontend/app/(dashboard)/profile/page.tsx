'use client';

import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { getProfile, updateProfile, changePassword } from '@/services/profileService';
import type { Profile, ApiError } from '@/types';

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

const EMPTY_PERSONAL: PersonalForm = { nombre: '', email: '', username: '' };
const NO_PERSONAL_ERRORS: PersonalErrors = { nombre: '', email: '', username: '' };
const NO_PERSONAL_TOUCHED: PersonalTouched = { nombre: false, email: false, username: false };

const EMPTY_PASSWORD: PasswordForm = { passwordActual: '', passwordNueva: '', confirmarPassword: '' };
const NO_PASSWORD_ERRORS: PasswordErrors = { passwordActual: '', passwordNueva: '', confirmarPassword: '' };
const NO_PASSWORD_TOUCHED: PasswordTouched = { passwordActual: false, passwordNueva: false, confirmarPassword: false };

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [_profile, setProfile] = useState<Profile | null>(null);

  const [personal, setPersonal] = useState<PersonalForm>(EMPTY_PERSONAL);
  const [personalErrors, setPersonalErrors] = useState<PersonalErrors>(NO_PERSONAL_ERRORS);
  const [personalTouched, setPersonalTouched] = useState<PersonalTouched>(NO_PERSONAL_TOUCHED);
  const [isSavingPersonal, setIsSavingPersonal] = useState(false);

  const [password, setPassword] = useState<PasswordForm>(EMPTY_PASSWORD);
  const [passwordErrors, setPasswordErrors] = useState<PasswordErrors>(NO_PASSWORD_ERRORS);
  const [passwordTouched, setPasswordTouched] = useState<PasswordTouched>(NO_PASSWORD_TOUCHED);
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await getProfile();
        setProfile(data);
        setPersonal({ nombre: data.nombre, email: data.email, username: data.username ?? '' });
      } catch (err) {
        const apiErr = err as ApiError;
        toast.error(apiErr?.message ?? 'No se pudo cargar el perfil.');
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  function handlePersonalChange(field: PersonalKey, value: string) {
    const next = { ...personal, [field]: value };
    setPersonal(next);
    if (personalTouched[field]) {
      setPersonalErrors((prev) => ({ ...prev, [field]: validatePersonal(next)[field] }));
    }
  }

  function handlePersonalBlur(field: PersonalKey) {
    setPersonalTouched((prev) => ({ ...prev, [field]: true }));
    setPersonalErrors((prev) => ({ ...prev, [field]: validatePersonal(personal)[field] }));
  }

  async function handleSavePersonal(e: React.FormEvent) {
    e.preventDefault();
    const allErrors = validatePersonal(personal);
    setPersonalErrors(allErrors);
    setPersonalTouched({ nombre: true, email: true, username: true });
    if (Object.values(allErrors).some(Boolean)) return;

    setIsSavingPersonal(true);
    try {
      const updated = await updateProfile({
        nombre: personal.nombre.trim(),
        email: personal.email.trim(),
        username: personal.username.trim().toLowerCase(),
      });
      setProfile(updated);
      setPersonal({ nombre: updated.nombre, email: updated.email, username: updated.username ?? '' });
      toast.success('Perfil actualizado correctamente.');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo actualizar el perfil.');
    } finally {
      setIsSavingPersonal(false);
    }
  }

  function handlePasswordChange(field: PasswordKey, value: string) {
    const next = { ...password, [field]: value };
    setPassword(next);
    if (passwordTouched[field]) {
      setPasswordErrors((prev) => ({ ...prev, [field]: validatePasswordForm(next)[field] }));
    }
    if (field === 'passwordNueva' && passwordTouched.confirmarPassword) {
      setPasswordErrors((prev) => ({
        ...prev,
        confirmarPassword: validateConfirmar(password.confirmarPassword, value),
      }));
    }
  }

  function handlePasswordBlur(field: PasswordKey) {
    setPasswordTouched((prev) => ({ ...prev, [field]: true }));
    setPasswordErrors((prev) => ({ ...prev, [field]: validatePasswordForm(password)[field] }));
  }

  async function handleSavePassword(e: React.FormEvent) {
    e.preventDefault();
    const allErrors = validatePasswordForm(password);
    setPasswordErrors(allErrors);
    setPasswordTouched({ passwordActual: true, passwordNueva: true, confirmarPassword: true });
    if (Object.values(allErrors).some(Boolean)) return;

    setIsSavingPassword(true);
    try {
      await changePassword({
        password_actual: password.passwordActual,
        password_nueva: password.passwordNueva,
        confirmar_password: password.confirmarPassword,
      });
      setPassword(EMPTY_PASSWORD);
      setPasswordTouched(NO_PASSWORD_TOUCHED);
      toast.success('Contraseña actualizada correctamente.');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo cambiar la contraseña.');
    } finally {
      setIsSavingPassword(false);
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-xl">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Perfil
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
            Administrá tu cuenta
          </p>
        </div>
        {[0, 1].map((i) => (
          <div key={i} className="rounded-xl border p-6 space-y-4 animate-pulse" style={CARD_STYLE}>
            <div className="h-5 w-40 rounded" style={{ backgroundColor: 'var(--color-border)' }} />
            <div className="space-y-3">
              {[0, 1, 2].map((j) => (
                <div key={j} className="space-y-1.5">
                  <div className="h-4 w-24 rounded" style={{ backgroundColor: 'var(--color-border)' }} />
                  <div className="h-10 rounded-lg" style={{ backgroundColor: 'var(--color-border)' }} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Perfil
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Administrá tu cuenta
        </p>
      </div>

      <section className="rounded-xl border p-6 space-y-4" style={CARD_STYLE}>
        <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Datos personales
        </h2>
        <form onSubmit={handleSavePersonal} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-nombre">
              Nombre
            </label>
            <input
              id="p-nombre"
              type="text"
              value={personal.nombre}
              onChange={(e) => handlePersonalChange('nombre', e.target.value)}
              onBlur={() => handlePersonalBlur('nombre')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {personalTouched.nombre && personalErrors.nombre && (
              <p className="text-xs" style={ERROR_STYLE}>{personalErrors.nombre}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-email">
              Email
            </label>
            <input
              id="p-email"
              type="email"
              value={personal.email}
              onChange={(e) => handlePersonalChange('email', e.target.value)}
              onBlur={() => handlePersonalBlur('email')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {personalTouched.email && personalErrors.email && (
              <p className="text-xs" style={ERROR_STYLE}>{personalErrors.email}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-username">
              Username
            </label>
            <input
              id="p-username"
              type="text"
              value={personal.username}
              onChange={(e) => handlePersonalChange('username', e.target.value)}
              onBlur={() => handlePersonalBlur('username')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {personalTouched.username && personalErrors.username && (
              <p className="text-xs" style={ERROR_STYLE}>{personalErrors.username}</p>
            )}
          </div>

          <Button type="submit" className="min-h-[44px]" disabled={isSavingPersonal}>
            {isSavingPersonal ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Guardando...</>
            ) : (
              'Guardar cambios'
            )}
          </Button>
        </form>
      </section>

      <section className="rounded-xl border p-6 space-y-4" style={CARD_STYLE}>
        <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          Cambiar contraseña
        </h2>
        <form onSubmit={handleSavePassword} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-actual">
              Contraseña actual
            </label>
            <input
              id="p-pwd-actual"
              type="password"
              value={password.passwordActual}
              onChange={(e) => handlePasswordChange('passwordActual', e.target.value)}
              onBlur={() => handlePasswordBlur('passwordActual')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {passwordTouched.passwordActual && passwordErrors.passwordActual && (
              <p className="text-xs" style={ERROR_STYLE}>{passwordErrors.passwordActual}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-nueva">
              Nueva contraseña
            </label>
            <input
              id="p-pwd-nueva"
              type="password"
              placeholder="Mínimo 8 caracteres"
              value={password.passwordNueva}
              onChange={(e) => handlePasswordChange('passwordNueva', e.target.value)}
              onBlur={() => handlePasswordBlur('passwordNueva')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {passwordTouched.passwordNueva && passwordErrors.passwordNueva && (
              <p className="text-xs" style={ERROR_STYLE}>{passwordErrors.passwordNueva}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="p-pwd-confirmar">
              Confirmar contraseña
            </label>
            <input
              id="p-pwd-confirmar"
              type="password"
              value={password.confirmarPassword}
              onChange={(e) => handlePasswordChange('confirmarPassword', e.target.value)}
              onBlur={() => handlePasswordBlur('confirmarPassword')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {passwordTouched.confirmarPassword && passwordErrors.confirmarPassword && (
              <p className="text-xs" style={ERROR_STYLE}>{passwordErrors.confirmarPassword}</p>
            )}
          </div>

          <Button type="submit" className="min-h-[44px]" disabled={isSavingPassword}>
            {isSavingPassword ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Cambiando...</>
            ) : (
              'Cambiar contraseña'
            )}
          </Button>
        </form>
      </section>
    </div>
  );
}
