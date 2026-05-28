import { redirect } from 'next/navigation';

// Sección de Video temporalmente oculta — aún no está lista.
// Los componentes en components/features/video/ se conservan intactos.
export default function VideoPage() {
  redirect('/dashboard');
}
