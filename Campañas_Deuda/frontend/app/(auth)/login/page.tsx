'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuthStore } from '@/store/authStore'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, isLoading } = useAuthStore()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      toast.success('¡Bienvenido/a!')
      router.push('/dashboard')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Algo salió mal. Intentá de nuevo.'
      setError(msg)
    }
  }

  return (
    <div className="rounded-2xl border border-card-border bg-surface shadow-sm p-8">
      {/* Logo */}
      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-white font-bold text-lg">
          CD
        </div>
        <h1 className="text-xl font-bold text-gray-900">Campañas de Deuda</h1>
        <p className="mt-1 text-sm text-gray-500">Municipalidad de Berazategui</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Input
          label="Email institucional"
          type="email"
          placeholder="usuario@berazategui.gob.ar"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          helper='Tip: usá "error@test.com" para ver el estado de error'
        />
        <Input
          label="Contraseña"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />

        {error && (
          <p
            className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700"
            role="alert"
          >
            {error}
          </p>
        )}

        <Button type="submit" loading={isLoading} className="w-full mt-2">
          {isLoading ? 'Ingresando...' : 'Ingresar al sistema'}
        </Button>
      </form>

      <p className="mt-6 text-center text-xs text-gray-400">
        Sistema de uso interno — acceso restringido
      </p>
    </div>
  )
}
