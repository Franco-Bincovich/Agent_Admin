'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import UserTable from '@/components/features/users/UserTable';
import { getUsers, toggleUserActive } from '@/services/userService';
import { useAuthStore } from '@/store/authStore';
import type { User, ApiError } from '@/types';

export default function UsersPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    if (user.rol !== 'administrador') {
      router.replace('/dashboard');
      return;
    }
    async function load() {
      try {
        const data = await getUsers();
        setUsers(data);
      } catch (err) {
        const apiErr = err as ApiError;
        toast.error(apiErr?.message ?? 'No pudimos cargar los usuarios.');
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [user, router]);

  async function handleToggleActive(userId: string, activo: boolean) {
    try {
      const updated = await toggleUserActive(userId, activo);
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
      toast.success('Usuario actualizado');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'No se pudo actualizar el usuario.');
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Usuarios
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
            Gestioná los accesos a la plataforma
          </p>
        </div>
        <Button
          disabled
          title="Próximamente"
          className="flex items-center gap-2 min-h-[44px]"
        >
          <UserPlus className="w-4 h-4" />
          Invitar usuario
        </Button>
      </div>

      <UserTable
        users={users}
        isLoading={isLoading}
        currentUserId={user?.id ?? ''}
        onToggleActive={handleToggleActive}
      />
    </div>
  );
}
