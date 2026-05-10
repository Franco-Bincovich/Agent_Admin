import { ToggleLeft, ToggleRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import type { User, UserRole } from '@/types';

interface Props {
  users: User[];
  isLoading: boolean;
  currentUserId: string;
  onToggleActive: (userId: string, activo: boolean) => void;
}

const ROL_BADGE: Record<UserRole, string> = {
  administrador: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  editor:        'bg-blue-500/20 text-blue-400 border-blue-500/30',
  viewer:        'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  usuario:       'bg-teal-500/20 text-teal-400 border-teal-500/30',
};

const ROL_LABEL: Record<UserRole, string> = {
  administrador: 'Administrador',
  editor:        'Editor',
  viewer:        'Viewer',
  usuario:       'Usuario',
};

function SkeletonRow() {
  return (
    <TableRow>
      {Array.from({ length: 6 }).map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        </TableCell>
      ))}
    </TableRow>
  );
}

export default function UserTable({ users, isLoading, currentUserId, onToggleActive }: Props) {
  return (
    <div className="rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
      <Table>
        <TableHeader>
          <TableRow style={{ borderColor: 'var(--color-border)' }}>
            <TableHead style={{ color: 'var(--color-text-secondary)' }}>Nombre</TableHead>
            <TableHead style={{ color: 'var(--color-text-secondary)' }}>Email</TableHead>
            <TableHead style={{ color: 'var(--color-text-secondary)' }}>Rol</TableHead>
            <TableHead style={{ color: 'var(--color-text-secondary)' }}>Estado</TableHead>
            <TableHead style={{ color: 'var(--color-text-secondary)' }}>Presentaciones</TableHead>
            <TableHead className="text-right" style={{ color: 'var(--color-text-secondary)' }}>Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
          ) : users.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="py-12 text-center text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                No hay usuarios registrados
              </TableCell>
            </TableRow>
          ) : (
            users.map((user) => (
              <TableRow key={user.id} style={{ borderColor: 'var(--color-border)' }}>
                <TableCell className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {user.nombre}
                </TableCell>
                <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                  {user.email}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={ROL_BADGE[user.rol]}>
                    {ROL_LABEL[user.rol]}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={user.activo
                      ? 'bg-green-500/20 text-green-400 border-green-500/30'
                      : 'bg-red-500/20 text-red-400 border-red-500/30'}
                  >
                    {user.activo ? 'Activo' : 'Inactivo'}
                  </Badge>
                </TableCell>
                <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                  —
                </TableCell>
                <TableCell className="text-right">
                  {user.id !== currentUserId && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => {
                        const confirmed = window.confirm(
                          `¿Seguro que querés ${user.activo ? 'desactivar' : 'activar'} a ${user.nombre}?`
                        );
                        if (!confirmed) return;
                        onToggleActive(user.id, !user.activo);
                      }}
                      aria-label={user.activo ? `Desactivar ${user.nombre}` : `Activar ${user.nombre}`}
                    >
                      {user.activo
                        ? <ToggleRight className="w-5 h-5" style={{ color: 'var(--color-success)' }} />
                        : <ToggleLeft  className="w-5 h-5" style={{ color: 'var(--color-text-disabled)' }} />}
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
