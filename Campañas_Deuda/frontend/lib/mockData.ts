import type { Ejecucion, PortfolioFile, User } from '@/types'

export const mockUser: User = {
  id: 'usr-001',
  email: 'analista@berazategui.gob.ar',
  nombre: 'Laura Gómez',
  rol: 'analista',
}

export const mockEjecuciones: Ejecucion[] = [
  {
    id: 'ejc-001',
    cartera: 'servicios_generales',
    dureza: 'dura',
    periodo: '2023',
    estado: 'listo',
    createdAt: '2026-05-28T09:00:00Z',
    startedAt: '2026-05-28T09:01:12Z',
    finishedAt: '2026-05-28T09:08:47Z',
    resultadoUrl: '/mock/informe-sg-dura-2023.docx',
    destinatariosCc: ['director.rentas@berazategui.gob.ar', 'jefe.cobranzas@berazategui.gob.ar'],
  },
  {
    id: 'ejc-002',
    cartera: 'automotor',
    dureza: 'blanda',
    periodo: '2024',
    estado: 'corriendo',
    createdAt: '2026-06-02T10:30:00Z',
    startedAt: '2026-06-02T10:30:55Z',
  },
  {
    id: 'ejc-003',
    cartera: 'servicio_sanitario',
    dureza: 'intermedia',
    periodo: '2022',
    estado: 'pendiente',
    createdAt: '2026-06-02T11:00:00Z',
  },
  {
    id: 'ejc-004',
    cartera: 'todas',
    dureza: 'todas',
    periodo: '2024',
    estado: 'error',
    createdAt: '2026-06-01T14:00:00Z',
    startedAt: '2026-06-01T14:00:42Z',
    errorMessage:
      'No se pudo conectar con el servicio de análisis. Revisá tu conexión e intentá de nuevo.',
  },
]

export const mockPortfolioFiles: PortfolioFile[] = [
  {
    id: 'pf-001',
    filename: 'cartera-servicios-2024-Q1.xlsx',
    cartera: 'servicios_generales',
    sizeBytes: 245760,
    uploadedAt: '2026-06-01T08:00:00Z',
  },
]

export const mockDestinatarios = [
  'director.rentas@berazategui.gob.ar',
  'jefe.cobranzas@berazategui.gob.ar',
  'secretaria.hacienda@berazategui.gob.ar',
]

export const mockDashboardStats = {
  ejecucionesEsteMes: 8,
  carterasAnalizadas: 3,
  ultimaCorreidaHace: '4 días',
  informesGenerados: 6,
}
