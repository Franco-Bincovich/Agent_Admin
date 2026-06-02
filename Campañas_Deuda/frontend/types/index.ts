export type UserRole = 'admin' | 'analista'

export interface User {
  id: string
  email: string
  nombre: string
  rol: UserRole
}

export type Cartera = 'servicios_generales' | 'servicio_sanitario' | 'automotor' | 'todas'
export type Dureza = 'blanda' | 'intermedia' | 'dura' | 'todas'
export type Periodo = '2021' | '2022' | '2023' | '2024' | '2025' | '2026' | 'todas'
export type EstadoEjecucion = 'pendiente' | 'corriendo' | 'listo' | 'error'

export interface Ejecucion {
  id: string
  cartera: Cartera
  dureza: Dureza
  periodo: Periodo
  estado: EstadoEjecucion
  createdAt: string
  startedAt?: string
  finishedAt?: string
  resultadoUrl?: string
  errorMessage?: string
  destinatariosCc?: string[]
}

export interface PortfolioFile {
  id: string
  filename: string
  cartera: string
  sizeBytes: number
  uploadedAt: string
}

export interface ApiError {
  error: true
  message: string
  code: string
}

export const CARTERA_LABELS: Record<Cartera, string> = {
  servicios_generales: 'Servicios Generales',
  servicio_sanitario: 'Servicio Sanitario (Agua)',
  automotor: 'Automotor',
  todas: 'Todas',
}

export const DUREZA_LABELS: Record<Dureza, string> = {
  blanda: 'Blanda',
  intermedia: 'Intermedia',
  dura: 'Dura',
  todas: 'Todas',
}
