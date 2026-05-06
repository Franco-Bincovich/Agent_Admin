export type UserRole = 'administrador' | 'editor' | 'viewer';

export interface User {
  id: string;
  nombre: string;
  email: string;
  rol: UserRole;
  activo: boolean;
  creado_en: string;
}

export type GenerationStatus = 'procesando' | 'listo' | 'error';

export type GenerationTemplate =
  | 'ejecutivo_oscuro'
  | 'profesional_claro'
  | 'corporativo_neutro';

export type GenerationTono = 'formal' | 'institucional' | 'comercial' | 'tecnico';

export type GenerationAudiencia =
  | 'directivos'
  | 'equipo_interno'
  | 'clientes'
  | 'tecnicos';

export type GenerationOutput = 'pptx' | 'gamma' | 'ambos';

export interface GenerationParametros {
  template: GenerationTemplate;
  tono: GenerationTono;
  audiencia: GenerationAudiencia;
  output: GenerationOutput;
}

export interface Generation {
  id: string;
  usuario_id: string;
  objetivo: string;
  estado: GenerationStatus;
  pptx_url: string | null;
  gamma_url: string | null;
  slides_count: number | null;
  creado_en: string;
  archivos?: string[];
  parametros?: GenerationParametros;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiError {
  error: true;
  message: string;
  code: string;
}

export type DocumentoEstado = 'procesando' | 'listo' | 'error';

export type DocumentoSeccion =
  | 'Resumen ejecutivo'
  | 'Introducción'
  | 'Contexto'
  | 'Objetivos'
  | 'Desarrollo'
  | 'Conclusiones'
  | 'Recomendaciones';

export interface DocumentoOpciones {
  homogeneizar: boolean;
  deduplicar: boolean;
  usar_imagenes: boolean;
}

export interface Documento {
  id: string;
  usuario_id: string;
  titulo: string;
  estado: DocumentoEstado;
  docx_url?: string;
  creado_en: string;
}
