import { redirect } from 'next/navigation'

/**
 * Redirige la raíz al login.
 * TODO Sesión 7: verificar token de sesión y redirigir a /dashboard si ya está autenticado.
 */
export default function RootPage() {
  redirect('/login')
}
