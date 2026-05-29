import Link from 'next/link';
import { FileText } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <FileText className="w-12 h-12" style={{ color: 'var(--color-text-disabled)' }} />
      <div>
        <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Todavía no generaste ninguna presentación
        </p>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Usá el Generador para crear tu primera presentación con IA.
        </p>
      </div>
      <Link
        href="/generator"
        className="inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-medium min-h-[44px] transition-colors"
        style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-background)' }}
      >
        Ir al Generador
      </Link>
    </div>
  );
}
