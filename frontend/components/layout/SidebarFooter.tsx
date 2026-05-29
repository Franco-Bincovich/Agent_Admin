'use client';

import { Sun, Moon, LogOut } from 'lucide-react';
import type { User } from '@/types';

interface SidebarFooterProps {
  user: User | null;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onLogout: () => void;
  isCollapsed: boolean;
}

export default function SidebarFooter({
  user,
  theme,
  onToggleTheme,
  onLogout,
  isCollapsed,
}: SidebarFooterProps) {
  const collapseRow = isCollapsed ? 'lg:justify-center lg:gap-0 lg:px-2' : '';
  const collapseHide = isCollapsed ? 'lg:hidden' : '';

  return (
    <div className="px-3 py-4 border-t space-y-0.5" style={{ borderColor: 'var(--color-border)' }}>
      {user && (
        <div className={`px-3 py-2 mb-1 ${collapseHide}`}>
          <p
            className="text-sm font-medium truncate"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {user.nombre}
          </p>
          <p className="text-xs capitalize" style={{ color: 'var(--color-text-secondary)' }}>
            {user.rol}
          </p>
        </div>
      )}
      <button
        onClick={onToggleTheme}
        className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] hover:bg-[var(--color-nav-hover)] ${collapseRow}`}
        style={{ color: 'var(--color-text-secondary)' }}
        aria-label={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      >
        {theme === 'dark'
          ? <Sun  className="w-4 h-4 flex-shrink-0" />
          : <Moon className="w-4 h-4 flex-shrink-0" />}
        <span className={collapseHide}>
          {theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
        </span>
      </button>
      <button
        onClick={onLogout}
        className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] hover:bg-red-500/10 hover:text-red-400 ${collapseRow}`}
        style={{ color: 'var(--color-text-secondary)' }}
        aria-label="Cerrar sesión"
      >
        <LogOut className="w-4 h-4 flex-shrink-0" />
        <span className={collapseHide}>Cerrar sesión</span>
      </button>
    </div>
  );
}
