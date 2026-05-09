'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { createUser } from '@/services/userService';
import type { User, ApiError } from '@/types';

interface Props {
  open: boolean;
  onClose: () => void;
  onCreated: (user: User) => void;
}

type CreateRol = 'administrador' | 'usuario';

interface FormState {
  nombre: string;
  email: string;
  username: string;
  password: string;
  rol: CreateRol;
}

type TextKey = Exclude<keyof FormState, 'rol'>;
type FormErrors = Record<TextKey, string>;

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

const FIELD_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';

const FIELD_STYLE = {
  backgroundColor: 'var(--color-background)',
  borderColor:     'var(--color-border)',
  color:           'var(--color-text-primary)',
} as const;

const LABEL_STYLE  = { color: 'var(--color-text-primary)' };
const ASTERISK     = <span style={{ color: 'var(--color-error)' }}>*</span>;
const ERROR_STYLE  = { color: 'var(--color-error)' };
const MODAL_STYLE  = { backgroundColor: 'var(--color-surface)' };

export default function CreateUserModal({ open, onClose, onCreated }: Props) {
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

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) handleClose(); }}>
      <DialogContent className="sm:max-w-md" showCloseButton={false} style={MODAL_STYLE}>
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--color-text-primary)' }}>
            Agregar usuario
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-2" noValidate>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-nombre">
              Nombre completo {ASTERISK}
            </label>
            <input
              id="cu-nombre"
              type="text"
              placeholder="Nombre completo"
              value={form.nombre}
              onChange={(e) => handleChange('nombre', e.target.value)}
              onBlur={() => handleBlur('nombre')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {touched.nombre && errors.nombre && (
              <p className="text-xs" style={ERROR_STYLE}>{errors.nombre}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-email">
              Email {ASTERISK}
            </label>
            <input
              id="cu-email"
              type="email"
              placeholder="usuario@ejemplo.com"
              value={form.email}
              onChange={(e) => handleChange('email', e.target.value)}
              onBlur={() => handleBlur('email')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {touched.email && errors.email && (
              <p className="text-xs" style={ERROR_STYLE}>{errors.email}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-username">
              Username {ASTERISK}
            </label>
            <input
              id="cu-username"
              type="text"
              placeholder="nombre.apellido"
              value={form.username}
              onChange={(e) => handleChange('username', e.target.value)}
              onBlur={() => handleBlur('username')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {touched.username && errors.username && (
              <p className="text-xs" style={ERROR_STYLE}>{errors.username}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-password">
              Contraseña {ASTERISK}
            </label>
            <input
              id="cu-password"
              type="password"
              placeholder="Mínimo 8 caracteres"
              value={form.password}
              onChange={(e) => handleChange('password', e.target.value)}
              onBlur={() => handleBlur('password')}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            />
            {touched.password && errors.password && (
              <p className="text-xs" style={ERROR_STYLE}>{errors.password}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-rol">
              Rol {ASTERISK}
            </label>
            <select
              id="cu-rol"
              value={form.rol}
              onChange={(e) => handleChange('rol', e.target.value)}
              className={FIELD_CLASS}
              style={FIELD_STYLE}
            >
              <option value="usuario">Usuario</option>
              <option value="administrador">Administrador</option>
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              className="flex-1 min-h-[44px]"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Creando...</>
              ) : (
                'Crear usuario'
              )}
            </Button>
          </div>

        </form>
      </DialogContent>
    </Dialog>
  );
}
