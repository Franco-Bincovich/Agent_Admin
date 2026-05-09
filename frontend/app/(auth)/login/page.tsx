'use client';

import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { useLoginForm } from '@/hooks/useLoginForm';
import type { ApiError } from '@/types';

const INPUT_CLASS =
  'bg-[var(--color-background)] border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)]';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuth();
  const {
    username, password,
    usernameError, passwordError,
    isFormValid,
    handleUsernameChange, handlePasswordChange, handleBlur,
    validateAll,
  } = useLoginForm();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validateAll()) return;
    try {
      await login(username, password);
      router.push('/dashboard');
    } catch (err) {
      const apiError = err as ApiError;
      toast.error(apiError?.message ?? 'Algo salió mal. Intentá de nuevo en unos minutos.');
    }
  }

  return (
    <div
      className="flex items-center justify-center min-h-screen px-4"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      <Card
        className="w-full max-w-sm"
        style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
      >
        <CardHeader className="text-center space-y-1 pb-4">
          <CardTitle className="text-2xl font-bold" style={{ color: 'var(--color-primary)' }}>
            Agent Admin
          </CardTitle>
          <CardDescription style={{ color: 'var(--color-text-secondary)' }}>
            Iniciá sesión para continuar
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div className="space-y-1.5">
              <Label htmlFor="username" style={{ color: 'var(--color-text-primary)' }}>
                Usuario <span className="text-red-500">*</span>
              </Label>
              <Input
                id="username" type="text" placeholder="tu usuario" autoComplete="username"
                value={username} onChange={(e) => handleUsernameChange(e.target.value)}
                onBlur={() => handleBlur('username')} aria-invalid={!!usernameError}
                aria-describedby={usernameError ? 'username-error' : undefined} className={INPUT_CLASS}
              />
              {usernameError && <p id="username-error" className="text-sm text-red-500">{usernameError}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" style={{ color: 'var(--color-text-primary)' }}>
                Contraseña <span className="text-red-500">*</span>
              </Label>
              <Input
                id="password" type="password" placeholder="Mínimo 8 caracteres"
                autoComplete="current-password" value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                onBlur={() => handleBlur('password')} aria-invalid={!!passwordError}
                aria-describedby={passwordError ? 'password-error' : undefined} className={INPUT_CLASS}
              />
              {passwordError && <p id="password-error" className="text-sm text-red-500">{passwordError}</p>}
            </div>

            <Button
              type="submit" className="w-full min-h-[44px]"
              disabled={isLoading || !isFormValid}
              title={!isFormValid ? 'Completá el usuario y la contraseña para continuar' : undefined}
            >
              {isLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Iniciando sesión...</>
              ) : 'Iniciar sesión'}
            </Button>

            <p className="text-xs text-center" style={{ color: 'var(--color-text-disabled)' }}>
              Los campos con * son obligatorios
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
