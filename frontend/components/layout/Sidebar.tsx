'use client';

import { usePathname } from 'next/navigation';
import {
  Zap,
  LayoutDashboard,
  Sparkles,
  FileText,
  GanttChartSquare,
  History,
  Users,
  UserCircle,
  ChevronLeft,
  ChevronRight,
  LayoutTemplate,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import NavList, { type NavItem } from './NavList';
import SidebarFooter from './SidebarFooter';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',      href: '/dashboard', icon: LayoutDashboard },
  { label: 'Presentaciones', href: '/generator',  icon: Sparkles },
  { label: 'Documentos',     href: '/documentos',   icon: FileText },
  { label: 'Planificación',  href: '/planificacion', icon: GanttChartSquare },
  { label: 'Estructuras',    href: '/plantillas',   icon: LayoutTemplate },
  { label: 'Historial',      href: '/history',    icon: History },
  { label: 'Usuarios',       href: '/users',      icon: Users, roles: ['administrador'] },
  { label: 'Perfil',         href: '/profile',    icon: UserCircle },
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

        <NavList
          items={visibleItems}
          pathname={pathname}
          isCollapsed={isCollapsed}
          onClose={onClose}
        />

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

        <SidebarFooter
          user={user}
          theme={theme}
          onToggleTheme={toggleTheme}
          onLogout={logout}
          isCollapsed={isCollapsed}
        />
      </aside>
    </>
  );
}
