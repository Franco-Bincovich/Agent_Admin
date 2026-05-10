export type UserRole = 'administrador' | 'editor' | 'viewer' | 'usuario';

export interface User {
  id: string;
  nombre: string;
  email: string;
  rol: UserRole;
  activo: boolean;
  creado_en: string;
}

export interface Profile {
  id: string;
  nombre: string;
  email: string;
  username: string | null;
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

export type TemaVisual =
  | 'minimalist' | 'playful' | 'organic' | 'modular'
  | 'elegant' | 'digital' | 'geometric';

export type EstiloImagen =
  | 'aiGenerated' | 'webAllImages' | 'webFreeToUse' | 'webFreeToUseCommercially'
  | 'pictographic' | 'giphy' | 'pexels' | 'placeholder' | 'noImages';

export interface GenerationParametros {
  template: GenerationTemplate;
  tono: GenerationTono;
  audiencia: GenerationAudiencia;
  output: GenerationOutput;
  usar_imagenes_documento?: boolean;
  tema_visual?: string;
  estilo_imagen?: string;
  paleta_colores?: string;
  cantidad_slides?: number;
}

export interface Generation {
  id: string;
  usuario_id: string;
  objetivo: string;
  estado: GenerationStatus;
  output_url: string | null;
  gamma_url: string | null;
  pptx_gamma_url?: string | null;
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
