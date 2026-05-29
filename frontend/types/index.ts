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
  titulo?: string;
  objetivo: string;
  estado: GenerationStatus;
  output_url: string | null;
  gamma_url: string | null;
  pptx_gamma_url?: string | null;
  slides_count: number | null;
  gamma_warning?: string | null;
  creado_en: string;
  archivos?: string[];
  parametros?: GenerationParametros;
}

export interface GenerationTimeoutError {
  estado: 'error';
  error: string;
}

export type GenerationOutcome = Generation | GenerationTimeoutError;

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

export interface DocumentoTimeoutError {
  estado: 'error';
  error: string;
}

export type DocumentoOutcome = Documento | DocumentoTimeoutError;

export interface ActivityItem {
  id: string;
  tipo: 'presentacion' | 'documento';
  objetivo?: string;
  titulo?: string;
  estado: string;
  creado_en: string;
  output_url?: string | null;
  docx_url?: string | null;
  gamma_url?: string | null;
  pptx_gamma_url?: string | null;
  slides_count?: number;
  parametros?: {
    template?: string;
    [key: string]: unknown;
  } | null;
}

// ── Document templates ────────────────────────────────────────────────────────

export interface DocumentTemplate {
  id: string
  usuario_id: string
  nombre: string
  secciones: DocumentoSeccion[]
  is_default: boolean
  creado_en: string
  actualizado_en: string
}

export interface CreateTemplatePayload {
  nombre: string
  secciones: DocumentoSeccion[]
}

export interface UpdateTemplatePayload {
  nombre: string
  secciones: DocumentoSeccion[]
  is_default: boolean
}

// ── Video agent ───────────────────────────────────────────────────────────────

export type VideoJobStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type EstiloEdicion = 'dinamico' | 'corporativo' | 'minimalista';
export type FormatoSalida = 'horizontal_16_9' | 'vertical_9_16' | 'cuadrado_1_1';
export type PosicionSubtitulos = 'abajo' | 'centro' | 'arriba' | 'sin_subtitulos';
export type ResolucionVideo = 'hd_720p' | 'full_hd_1080p' | 'ultra_hd_4k';

export interface BrandConfigValues {
  logo: File | null;
  colorPrimario: string;
  colorSecundario: string;
  fuente: string;
}

export interface VideoJob {
  id: string;
  usuario_id: string;
  titulo: string | null;
  estado: VideoJobStatus;
  video_input_url: string | null;
  output_url: string | null;
  parametros: Record<string, unknown>;
  error_message: string | null;
  creado_en: string;
}
