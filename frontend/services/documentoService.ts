import { get } from '@/services/api';
import { uploadFileToStorage } from '@/services/storageService';
import type {
  Documento,
  DocumentoSeccion,
  DocumentoOpciones,
  ApiError,
} from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function getMyDocumentos(): Promise<Documento[]> {
  return get<Documento[]>('/api/v1/documentos');
}

export async function getDocumento(id: string): Promise<Documento> {
  return get<Documento>(`/api/v1/documentos/${id}`);
}

export interface CreateDocumentoInput {
  archivos: File[];
  plantilla: File | null;
  logo: File | null;
  titulo: string;
  secciones: DocumentoSeccion[];
  indicaciones: string;
  opciones: DocumentoOpciones;
}

export async function createDocumento(input: CreateDocumentoInput): Promise<Documento> {
  const archivos_urls = await Promise.all(
    input.archivos.map((f) => uploadFileToStorage(f, 'documentos-fuente', f.name)),
  );
  const plantilla_url = input.plantilla
    ? await uploadFileToStorage(input.plantilla, 'plantillas', input.plantilla.name)
    : null;
  const logo_url = input.logo
    ? await uploadFileToStorage(input.logo, 'logos-documentos', input.logo.name)
    : null;

  const payload = {
    titulo: input.titulo,
    secciones: JSON.stringify(input.secciones),
    indicaciones: input.indicaciones || null,
    opciones: JSON.stringify(input.opciones),
    archivos_urls,
    plantilla_url,
    logo_url,
  };

  const response = await fetch(`${BASE_URL}/api/v1/documentos`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw (await response.json()) as ApiError;
  }

  if (!response.ok) {
    throw (await response.json()) as ApiError;
  }

  return response.json() as Promise<Documento>;
}
