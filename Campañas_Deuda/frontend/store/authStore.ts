import { create } from 'zustand'
import { mockUser } from '@/lib/mockData'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  // TODO Sesión 7: conectar con POST /api/auth/login
  login: (email: string, password: string) => Promise<void>
  // TODO Sesión 7: llamar POST /api/auth/logout y limpiar tokens httpOnly
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (email: string, _password: string) => {
    set({ isLoading: true })
    // Simula latencia de red
    await new Promise<void>((resolve) => setTimeout(resolve, 1200))
    if (email === 'error@test.com') {
      set({ isLoading: false })
      throw new Error('Credenciales incorrectas. Verificá tu email y contraseña.')
    }
    set({ user: mockUser, isAuthenticated: true, isLoading: false })
  },

  logout: () => {
    set({ user: null, isAuthenticated: false })
  },
}))
