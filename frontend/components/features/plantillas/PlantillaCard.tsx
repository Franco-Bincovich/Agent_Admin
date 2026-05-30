'use client';

import { useState } from 'react';
import { Pencil, Star, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import type { DocumentTemplate } from '@/types';

interface Props {
  template: DocumentTemplate;
  onEdit: (template: DocumentTemplate) => void;
  onDelete: (id: string) => void;
  onSetDefault: (id: string) => void;
}

export default function PlantillaCard({ template, onEdit, onDelete, onSetDefault }: Props) {
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  return (
    <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <span
            className="font-medium text-sm leading-snug"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {template.nombre}
          </span>
          {template.is_default && (
            <Badge variant="default" className="shrink-0 mt-0.5">
              Default
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {template.secciones.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {template.secciones.map((s) => (
              <span
                key={s.id}
                className="px-2.5 py-1 rounded-full text-xs font-medium border"
                style={{
                  backgroundColor: 'color-mix(in srgb, var(--color-primary) 15%, transparent)',
                  borderColor: 'var(--color-primary)',
                  color: 'var(--color-primary)',
                }}
              >
                {s.nombre}
                {s.descripcion && (
                  <span
                    className="block text-xs font-normal mt-0.5"
                    style={{ color: 'var(--color-text-disabled)' }}
                  >
                    {s.descripcion}
                  </span>
                )}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Sin secciones configuradas.
          </p>
        )}

        <div className="flex flex-wrap gap-2">
          <Button size="sm" variant="outline" onClick={() => onEdit(template)}>
            <Pencil className="w-3.5 h-3.5 mr-1.5" />
            Editar
          </Button>

          {!template.is_default && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onSetDefault(template.id)}
            >
              <Star className="w-3.5 h-3.5 mr-1.5" />
              Marcar como default
            </Button>
          )}

          {isConfirmingDelete ? (
            <>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => onDelete(template.id)}
              >
                Confirmar
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setIsConfirmingDelete(false)}
              >
                Cancelar
              </Button>
            </>
          ) : (
            <Button
              size="sm"
              variant="destructive"
              onClick={() => setIsConfirmingDelete(true)}
            >
              <Trash2 className="w-3.5 h-3.5 mr-1.5" />
              Eliminar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
