'use client';

import Link from 'next/link';
import type { UserRole } from '@/types';

export interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: UserRole[];
}

interface NavListProps {
  items: NavItem[];
  pathname: string;
  isCollapsed: boolean;
  onClose?: () => void;
}

export default function NavList({ items, pathname, isCollapsed, onClose }: NavListProps) {
  const collapseRow = isCollapsed ? 'lg:justify-center lg:gap-0 lg:px-2' : '';
  const collapseHide = isCollapsed ? 'lg:hidden' : '';

  return (
    <nav className="flex-1 px-3 py-4 space-y-0.5">
      {items.map(({ label, href, icon: Icon }) => {
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
  );
}
