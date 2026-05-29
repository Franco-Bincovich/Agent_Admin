'use client';

import { useEffect, useState } from 'react';
import { FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import PlantillaCard from './PlantillaCard';
import PlantillaForm from './PlantillaForm';
import {
  createTemplate,
  deleteTemplate,
  getMyTemplates,
  setDefaultTemplate,
  updateTemplate,
} from '@/services/documentTemplateService';
import type {
  CreateTemplatePayload,
  DocumentTemplate,
  UpdateTemplatePayload,
} from '@/types';

export default function PlantillasClient() {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<DocumentTemplate | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function loadTemplates() {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyTemplates();
      setTemplates(data);
    } catch {
      setError('No se pudieron cargar las estructuras. Intentá de nuevo.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadTemplates();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openCreate() {
    setEditingTemplate(null);
    setShowForm(true);
  }

  function openEdit(template: DocumentTemplate) {
    setEditingTemplate(template);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingTemplate(null);
  }

  async function handleSave(payload: CreateTemplatePayload | UpdateTemplatePayload) {
    try {
      setIsSaving(true);
      setError(null);
      if (editingTemplate) {
        await updateTemplate(editingTemplate.id, payload as UpdateTemplatePayload);
      } else {
        await createTemplate(payload as CreateTemplatePayload);
      }
      closeForm();
      await loadTemplates();
    } catch {
      setError('No se pudo guardar la estructura. Intentá de nuevo.');
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      setError(null);
      await deleteTemplate(id);
      setTemplates((prev) => prev.filter((t) => t.id !== id));
    } catch {
      setError('No se pudo eliminar la estructura. Intentá de nuevo.');
    }
  }

  async function handleSetDefault(id: string) {
    try {
      setError(null);
      const updated = await setDefaultTemplate(id);
      setTemplates((prev) =>
        prev.map((t) => (t.id === id ? updated : { ...t, is_default: false })),
      );
    } catch {
      setError('No se pudo actualizar la estructura por defecto.');
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card
            key={i}
            style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
          >
            <CardContent className="p-4 space-y-3">
              <div
                className="h-5 w-3/4 rounded animate-pulse"
                style={{ backgroundColor: 'var(--color-border)' }}
              />
              <div className="flex gap-1.5">
                {Array.from({ length: 3 }).map((_, j) => (
                  <div
                    key={j}
                    className="h-6 w-20 rounded-full animate-pulse"
                    style={{ backgroundColor: 'var(--color-border)' }}
                  />
                ))}
              </div>
              <div
                className="h-8 w-full rounded animate-pulse"
                style={{ backgroundColor: 'var(--color-border)' }}
              />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <>
      {error && (
        <div
          className="rounded-lg border px-4 py-3 text-sm"
          style={{
            backgroundColor: 'color-mix(in srgb, var(--color-error) 10%, transparent)',
            borderColor: 'var(--color-error)',
            color: 'var(--color-error)',
          }}
        >
          {error}
        </div>
      )}

      {templates.length === 0 ? (
        <div
          className="flex flex-col items-center gap-4 text-center rounded-lg border py-16 px-6"
          style={{ borderColor: 'var(--color-border)' }}
        >
          <FileText className="w-12 h-12" style={{ color: 'var(--color-text-disabled)' }} />
          <div>
            <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
              Todavía no tenés estructuras
            </p>
            <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
              Creá combinaciones de secciones para reutilizarlas al generar documentos.
            </p>
          </div>
          <Button onClick={openCreate} className="min-h-[44px]">
            <Plus className="w-4 h-4 mr-2" />
            Crear primera estructura
          </Button>
        </div>
      ) : (
        <>
          <div className="flex justify-end">
            <Button onClick={openCreate} className="min-h-[44px]">
              <Plus className="w-4 h-4 mr-2" />
              Nueva estructura
            </Button>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {templates.map((t) => (
              <PlantillaCard
                key={t.id}
                template={t}
                onEdit={openEdit}
                onDelete={handleDelete}
                onSetDefault={handleSetDefault}
              />
            ))}
          </div>
        </>
      )}

      <Dialog open={showForm} onOpenChange={(o) => { if (!o) closeForm(); }}>
        <DialogContent
          className="sm:max-w-md"
          showCloseButton={false}
          style={{ backgroundColor: 'var(--color-surface)' }}
        >
          <DialogHeader>
            <DialogTitle style={{ color: 'var(--color-text-primary)' }}>
              {editingTemplate ? 'Editar estructura' : 'Nueva estructura'}
            </DialogTitle>
          </DialogHeader>
          <PlantillaForm
            initialData={editingTemplate}
            onSave={handleSave}
            onCancel={closeForm}
            isLoading={isSaving}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}
