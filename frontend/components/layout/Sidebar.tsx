'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Zap,
  LayoutDashboard,
  Sparkles,
  FileText,
  History,
  Users,
  UserCircle,
  LogOut,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import type { UserRole } from '@/types';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: UserRole[];
}

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Presentaciones', href: '/generator', icon: Sparkles },
  { label: 'Documentos', href: '/documentos', icon: FileText },
  { label: 'Historial', href: '/history', icon: History },
  { label: 'Usuarios', href: '/users', icon: Users, roles: ['administrador'] },
  { label: 'Perfil', href: '/profile', icon: UserCircle },
];

export default function Sidebar({
  isOpen = false,
  onClose,
  isCollapsed = false,
  onToggleCollapse,
}: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.roles || (user?.rol && item.roles.includes(user.rol)),
  );

  // El collapse sólo aplica en lg+; en mobile (drawer) el sidebar siempre va expandido
  const collapseRow = isCollapsed ? 'lg:justify-center lg:gap-0 lg:px-2' : '';
  const collapseHide = isCollapsed ? 'lg:hidden' : '';

  return (
    <>
      {/* Mobile overlay — sólo activo en < lg cuando isOpen */}
      <div
        className={`lg:hidden fixed inset-0 z-40 bg-black/50 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col w-64 min-h-screen flex-shrink-0 border-r transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:static lg:z-auto lg:translate-x-0 ${isCollapsed ? 'lg:w-16' : 'lg:w-64'}`}
        style={{
          backgroundColor: 'var(--color-surface)',
          borderColor: 'var(--color-border)',
        }}
      >
        {/* Logo */}
        <div
          className={`flex items-center gap-2.5 px-6 py-5 border-b ${
            isCollapsed ? 'lg:justify-center lg:px-0' : ''
          }`}
          style={{ borderColor: 'var(--color-border)' }}
        >
          <Zap className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--color-primary)' }} />
          <span
            className={`font-semibold text-lg ${collapseHide}`}
            style={{ color: 'var(--color-text-primary)' }}
          >
            Agent Admin
          </span>
        </div>

        {/* Nav items */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {visibleItems.map(({ label, href, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={() => onClose?.()}
                aria-label={label}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] ${collapseRow} ${
                  active ? '' : 'hover:bg-[var(--color-nav-hover)]'
                }`}
                style={{
                  color: active ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                  backgroundColor: active
                    ? 'color-mix(in srgb, var(--color-primary) 12%, transparent)'
                    : undefined,
                }}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className={collapseHide}>{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Toggle collapse — sólo desktop, arriba del footer */}
        <div className="hidden lg:block px-3 pb-2">
          <button
            onClick={onToggleCollapse}
            className="flex items-center justify-center w-full px-3 py-2 rounded-lg transition-colors hover:bg-[var(--color-nav-hover)]"
            style={{ color: 'var(--color-text-secondary)' }}
            aria-label={isCollapsed ? 'Expandir menú' : 'Colapsar menú'}
          >
            {isCollapsed
              ? <ChevronRight className="w-4 h-4" />
              : <ChevronLeft  className="w-4 h-4" />}
          </button>
        </div>

        {/* Footer: user info + theme + logout */}
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
            onClick={toggleTheme}
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
            onClick={logout}
            className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] hover:bg-red-500/10 hover:text-red-400 ${collapseRow}`}
            style={{ color: 'var(--color-text-secondary)' }}
            aria-label="Cerrar sesión"
          >
            <LogOut className="w-4 h-4 flex-shrink-0" />
            <span className={collapseHide}>Cerrar sesión</span>
          </button>
        </div>
      </aside>
    </>
  );
}
