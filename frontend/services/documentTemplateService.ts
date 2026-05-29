import { del, get, patch, post, put } from '@/services/api';
import type { CreateTemplatePayload, DocumentTemplate, UpdateTemplatePayload } from '@/types';

const BASE = '/api/v1/document-templates';

export async function getMyTemplates(): Promise<DocumentTemplate[]> {
  return get<DocumentTemplate[]>(BASE);
}

export async function getTemplate(id: string): Promise<DocumentTemplate> {
  return get<DocumentTemplate>(`${BASE}/${id}`);
}

export async function createTemplate(payload: CreateTemplatePayload): Promise<DocumentTemplate> {
  return post<DocumentTemplate>(BASE, payload);
}

export async function updateTemplate(id: string, payload: UpdateTemplatePayload): Promise<DocumentTemplate> {
  return put<DocumentTemplate>(`${BASE}/${id}`, payload);
}

export async function deleteTemplate(id: string): Promise<void> {
  return del<void>(`${BASE}/${id}`);
}

export async function setDefaultTemplate(id: string): Promise<DocumentTemplate> {
  return patch<DocumentTemplate>(`${BASE}/${id}/default`, {});
}
