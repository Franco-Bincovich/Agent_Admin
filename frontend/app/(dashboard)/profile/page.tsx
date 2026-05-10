'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { getProfile } from '@/services/profileService';
import type { ApiError } from '@/types';
import PersonalSection from './PersonalSection';
import PasswordSection from './PasswordSection';

const CARD_STYLE = { backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' } as const;
const BORDER_STYLE = { backgroundColor: 'var(--color-border)' };

function ProfileSkeleton() {
  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Perfil</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Administrá tu cuenta</p>
      </div>
      {[0, 1].map((i) => (
        <div key={i} className="rounded-xl border p-6 space-y-4 animate-pulse" style={CARD_STYLE}>
          <div className="h-5 w-40 rounded" style={BORDER_STYLE} />
          <div className="space-y-3">
            {[0, 1, 2].map((j) => (
              <div key={j} className="space-y-1.5">
                <div className="h-4 w-24 rounded" style={BORDER_STYLE} />
                <div className="h-10 rounded-lg" style={BORDER_STYLE} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [defaultValues, setDefaultValues] = useState({ nombre: '', email: '', username: '' });

  useEffect(() => {
    async function load() {
      try {
        const data = await getProfile();
        setDefaultValues({ nombre: data.nombre, email: data.email, username: data.username ?? '' });
      } catch (err) {
        const apiErr = err as ApiError;
        toast.error(apiErr?.message ?? 'No se pudo cargar el perfil.');
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  if (isLoading) return <ProfileSkeleton />;

  return (
    <div className="space-y-6 max-w-xl">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Perfil</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Administrá tu cuenta</p>
      </div>
      <PersonalSection defaultValues={defaultValues} />
      <PasswordSection />
    </div>
  );
}
