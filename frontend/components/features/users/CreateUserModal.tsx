'use client';

import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { User } from '@/types';
import { useCreateUserForm } from './useCreateUserForm';

interface Props {
  open: boolean;
  onClose: () => void;
  onCreated: (user: User) => void;
}

const FIELD_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]';
const FIELD_STYLE = {
  backgroundColor: 'var(--color-background)',
  borderColor:     'var(--color-border)',
  color:           'var(--color-text-primary)',
} as const;
const LABEL_STYLE = { color: 'var(--color-text-primary)' };
const ASTERISK    = <span style={{ color: 'var(--color-error)' }}>*</span>;
const ERROR_STYLE = { color: 'var(--color-error)' };
const MODAL_STYLE = { backgroundColor: 'var(--color-surface)' };

export default function CreateUserModal({ open, onClose, onCreated }: Props) {
  const { form, errors, touched, isSubmitting, handleChange, handleBlur, handleClose, handleSubmit } =
    useCreateUserForm({ onClose, onCreated });

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
              id="cu-nombre" type="text" placeholder="Nombre completo"
              value={form.nombre} onChange={(e) => handleChange('nombre', e.target.value)}
              onBlur={() => handleBlur('nombre')} className={FIELD_CLASS} style={FIELD_STYLE}
            />
            {touched.nombre && errors.nombre && <p className="text-xs" style={ERROR_STYLE}>{errors.nombre}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-email">
              Email {ASTERISK}
            </label>
            <input
              id="cu-email" type="email" placeholder="usuario@ejemplo.com"
              value={form.email} onChange={(e) => handleChange('email', e.target.value)}
              onBlur={() => handleBlur('email')} className={FIELD_CLASS} style={FIELD_STYLE}
            />
            {touched.email && errors.email && <p className="text-xs" style={ERROR_STYLE}>{errors.email}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-username">
              Username {ASTERISK}
            </label>
            <input
              id="cu-username" type="text" placeholder="nombre.apellido"
              value={form.username} onChange={(e) => handleChange('username', e.target.value)}
              onBlur={() => handleBlur('username')} className={FIELD_CLASS} style={FIELD_STYLE}
            />
            {touched.username && errors.username && <p className="text-xs" style={ERROR_STYLE}>{errors.username}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-password">
              Contraseña {ASTERISK}
            </label>
            <input
              id="cu-password" type="password" placeholder="Mínimo 8 caracteres"
              value={form.password} onChange={(e) => handleChange('password', e.target.value)}
              onBlur={() => handleBlur('password')} className={FIELD_CLASS} style={FIELD_STYLE}
            />
            {touched.password && errors.password && <p className="text-xs" style={ERROR_STYLE}>{errors.password}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block text-sm font-medium" style={LABEL_STYLE} htmlFor="cu-rol">
              Rol {ASTERISK}
            </label>
            <select
              id="cu-rol" value={form.rol}
              onChange={(e) => handleChange('rol', e.target.value)}
              className={FIELD_CLASS} style={FIELD_STYLE}
            >
              <option value="usuario">Usuario</option>
              <option value="administrador">Administrador</option>
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="button" variant="outline" className="flex-1"
              onClick={handleClose} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button type="submit" className="flex-1 min-h-[44px]" disabled={isSubmitting}>
              {isSubmitting
                ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Creando...</>
                : 'Crear usuario'}
            </Button>
          </div>

        </form>
      </DialogContent>
    </Dialog>
  );
}
