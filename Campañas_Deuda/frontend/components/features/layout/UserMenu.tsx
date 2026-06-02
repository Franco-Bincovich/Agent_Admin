'use client'

import { useState } from 'react'
import { ChevronDown, LogOut, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

export function UserMenu() {
  const { user, logout } = useAuthStore()
  const [open, setOpen] = useState(false)

  const initials =
    user?.nombre
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase() ?? '??'

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label="Menú de usuario"
        className={cn(
          'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors min-h-[44px]',
          'text-blue-100 hover:bg-white/10 hover:text-white'
        )}
      >
        <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-white text-xs font-bold">
          {initials}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{user?.nombre ?? 'Usuario'}</p>
          <p className="text-xs text-blue-300 truncate">{user?.rol ?? ''}</p>
        </div>
        <ChevronDown
          className={cn('h-4 w-4 flex-shrink-0 transition-transform', open && 'rotate-180')}
          aria-hidden
        />
      </button>

      {open && (
        <>
          <div className="absolute bottom-full left-0 right-0 mb-1 rounded-xl bg-surface border border-card-border shadow-xl overflow-hidden z-50">
            <div className="px-4 py-3 border-b border-card-border">
              <p className="text-sm font-medium text-gray-900">{user?.nombre}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
            <button
              onClick={() => {
                logout()
                setOpen(false)
              }}
              className="flex w-full items-center gap-2 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors min-h-[44px]"
              role="menuitem"
            >
              <LogOut className="h-4 w-4" aria-hidden />
              Cerrar sesión
            </button>
          </div>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden />
        </>
      )}
    </div>
  )
}
