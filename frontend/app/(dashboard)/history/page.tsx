'use client';

import Link from 'next/link';
import { useGenerations } from '@/hooks/useGenerations';
import { Download, ExternalLink, FileText } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { formatDate, formatTemplate, truncateText } from '@/utils/formatters';
import type { Generation, GenerationStatus } from '@/types';

const STATUS_BADGE: Record<GenerationStatus, { label: string; className: string }> = {
  procesando: { label: 'Procesando...', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  listo:      { label: 'Listo',         className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  error:      { label: 'Error',         className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

function SkeletonRow() {
  return (
    <TableRow>
      {Array.from({ length: 6 }).map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 w-full rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        </TableCell>
      ))}
    </TableRow>
  );
}

export default function HistoryPage() {
  const { generations, isLoading } = useGenerations();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Historial
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Todas tus presentaciones generadas
        </p>
      </div>

      <div className="rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ borderColor: 'var(--color-border)' }}>
              <TableHead className="w-[30%]"  style={{ color: 'var(--color-text-secondary)' }}>Objetivo</TableHead>
              <TableHead                       style={{ color: 'var(--color-text-secondary)' }}>Template</TableHead>
              <TableHead                       style={{ color: 'var(--color-text-secondary)' }}>Estado</TableHead>
              <TableHead                       style={{ color: 'var(--color-text-secondary)' }}>Slides</TableHead>
              <TableHead                       style={{ color: 'var(--color-text-secondary)' }}>Fecha</TableHead>
              <TableHead className="text-right" style={{ color: 'var(--color-text-secondary)' }}>Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
            ) : generations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-16">
                  <div className="flex flex-col items-center gap-4 text-center">
                    <FileText className="w-12 h-12" style={{ color: 'var(--color-text-disabled)' }} />
                    <div>
                      <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                        Todavía no generaste ninguna presentación
                      </p>
                      <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                        Usá el Generador para crear tu primera presentación con IA.
                      </p>
                    </div>
                    <Link
                      href="/generator"
                      className="inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-medium min-h-[44px] transition-colors"
                      style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-background)' }}
                    >
                      Ir al Generador
                    </Link>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              generations.map((gen) => {
                const badge = STATUS_BADGE[gen.estado];
                return (
                  <TableRow key={gen.id} style={{ borderColor: 'var(--color-border)' }}>
                    <TableCell style={{ color: 'var(--color-text-primary)' }}>
                      {truncateText(gen.objetivo, 45)}
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {gen.parametros ? formatTemplate(gen.parametros.template) : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={badge.className}>{badge.label}</Badge>
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {gen.slides_count ?? '—'}
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDate(gen.creado_en)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        {gen.output_url && (
                          <a href={gen.output_url} download aria-label="Descargar PPTX">
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                              <Download className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
                            </Button>
                          </a>
                        )}
                        {gen.gamma_url && (
                          <a href={gen.gamma_url} target="_blank" rel="noopener noreferrer" aria-label="Abrir en Gamma">
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                              <ExternalLink className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
                            </Button>
                          </a>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
