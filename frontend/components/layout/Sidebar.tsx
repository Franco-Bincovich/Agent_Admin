'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Zap,
  LayoutDashboard,
  Sparkles,
  History,
  Users,
  LogOut,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import type { UserRole } from '@/types';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Generador', href: '/generator', icon: Sparkles },
  { label: 'Historial', href: '/history', icon: History },
  { label: 'Usuarios', href: '/users', icon: Users, roles: ['administrador'] },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.roles || (user?.rol && item.roles.includes(user.rol)),
  );

  return (
    <aside
      className="hidden lg:flex flex-col w-64 min-h-screen flex-shrink-0 border-r"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 px-6 py-5 border-b"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <Zap className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--color-primary)' }} />
        <span className="font-semibold text-lg" style={{ color: 'var(--color-text-primary)' }}>
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
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] ${
                active ? '' : 'hover:bg-white/5'
              }`}
              style={{
                color: active ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                backgroundColor: active
                  ? 'color-mix(in srgb, var(--color-primary) 12%, transparent)'
                  : undefined,
              }}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User info + logout */}
      <div className="px-3 py-4 border-t space-y-0.5" style={{ borderColor: 'var(--color-border)' }}>
        {user && (
          <div className="px-3 py-2 mb-1">
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
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] hover:bg-red-500/10 hover:text-red-400"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
