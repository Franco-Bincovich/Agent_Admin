'use client';

import Link from 'next/link';
import { useActivity } from '@/hooks/useActivity';
import { Download, ExternalLink, FileText } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { formatDate, truncateText } from '@/utils/formatters';
import type { ActivityItem } from '@/types';

const STATUS_BADGE: Record<string, { label: string; className: string }> = {
  procesando: { label: 'Procesando...', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  listo:      { label: 'Listo',         className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  error:      { label: 'Error',         className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

const TEMPLATE_LABELS: Record<string, string> = {
  ejecutivo_oscuro: 'Ejecutivo oscuro',
  profesional_claro: 'Profesional claro',
  corporativo_neutro: 'Corporativo neutro',
};

const TYPE_BADGE: Record<ActivityItem['tipo'], { label: string; className: string }> = {
  presentacion: { label: 'Presentación', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  documento:    { label: 'Documento',    className: 'bg-green-500/20 text-green-400 border-green-500/30' },
};

function SkeletonRow() {
  return (
    <TableRow>
      {Array.from({ length: 7 }).map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 w-full rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        </TableCell>
      ))}
    </TableRow>
  );
}

function SkeletonCard() {
  return (
    <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
      <CardContent className="p-4 space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-4 w-full rounded animate-pulse" style={{ backgroundColor: 'var(--color-border)' }} />
        ))}
      </CardContent>
    </Card>
  );
}

function EmptyState() {
  return (
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
  );
}

function ItemActions({ item, align }: { item: ActivityItem; align: 'end' | 'stretch' }) {
  const isStretch = align === 'stretch';
  const wrapperClass = isStretch
    ? 'flex flex-col gap-1.5'
    : 'flex flex-col items-end gap-1';
  const aClass = isStretch ? 'block' : '';
  const btnClass = isStretch
    ? 'h-10 gap-1.5 px-3 text-xs justify-start w-full'
    : 'h-8 gap-1.5 px-2 text-xs';
  return (
    <div className={wrapperClass}>
      {item.gamma_url && (
        <a href={item.gamma_url} target="_blank" rel="noopener noreferrer" className={aClass}>
          <Button variant="ghost" size="sm" className={btnClass} style={{ color: 'var(--color-text-secondary)' }}>
            <ExternalLink className="w-3.5 h-3.5" />
            Abrir en Gamma
          </Button>
        </a>
      )}
      {item.pptx_gamma_url && (
        <a href={item.pptx_gamma_url} target="_blank" rel="noopener noreferrer" className={aClass}>
          <Button variant="ghost" size="sm" className={btnClass} style={{ color: 'var(--color-text-secondary)' }}>
            <Download className="w-3.5 h-3.5" />
            Descargar PPTX Gamma
          </Button>
        </a>
      )}
      {item.output_url && (
        <a href={item.output_url} download className={aClass}>
          <Button variant="ghost" size="sm" className={btnClass} style={{ color: 'var(--color-text-secondary)' }}>
            <Download className="w-3.5 h-3.5" />
            Descargar PPTX
          </Button>
        </a>
      )}
      {item.docx_url && (
        <a href={item.docx_url} download className={aClass}>
          <Button variant="ghost" size="sm" className={btnClass} style={{ color: 'var(--color-text-secondary)' }}>
            <Download className="w-3.5 h-3.5" />
            Descargar DOCX
          </Button>
        </a>
      )}
    </div>
  );
}

export default function HistoryPage() {
  const { activity, isLoading } = useActivity();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Historial
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Todas tus presentaciones y documentos generados
        </p>
      </div>

      {/* Mobile: cards apiladas */}
      <div className="lg:hidden space-y-3">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
        ) : activity.length === 0 ? (
          <Card style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}>
            <CardContent className="py-12">
              <EmptyState />
            </CardContent>
          </Card>
        ) : (
          activity.map((item) => {
            const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
            const typeBadge = TYPE_BADGE[item.tipo];
            const label = item.titulo?.trim() || item.objetivo || '';
            return (
              <Card
                key={item.id}
                style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
              >
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className={typeBadge.className}>{typeBadge.label}</Badge>
                    <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDate(item.creado_en)}
                    </span>
                  </div>
                  <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                    {truncateText(label, 60)}
                  </p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
                    {item.tipo === 'presentacion' && item.slides_count != null && (
                      <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                        {item.slides_count} slides
                      </span>
                    )}
                  </div>
                  <ItemActions item={item} align="stretch" />
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Desktop: tabla */}
      <div className="hidden lg:block rounded-lg border overflow-hidden overflow-x-auto" style={{ borderColor: 'var(--color-border)' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ borderColor: 'var(--color-border)' }}>
              <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Tipo</TableHead>
              <TableHead className="w-[30%]"      style={{ color: 'var(--color-text-secondary)' }}>Objetivo</TableHead>
              <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Template</TableHead>
              <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Estado</TableHead>
              <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Slides</TableHead>
              <TableHead                          style={{ color: 'var(--color-text-secondary)' }}>Fecha</TableHead>
              <TableHead className="text-right"   style={{ color: 'var(--color-text-secondary)' }}>Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
            ) : activity.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-16">
                  <EmptyState />
                </TableCell>
              </TableRow>
            ) : (
              activity.map((item) => {
                const statusBadge = STATUS_BADGE[item.estado] ?? STATUS_BADGE['procesando'];
                const typeBadge = TYPE_BADGE[item.tipo];
                const label = item.titulo?.trim() || item.objetivo || '';
                return (
                  <TableRow key={item.id} style={{ borderColor: 'var(--color-border)' }}>
                    <TableCell>
                      <Badge variant="outline" className={typeBadge.className}>{typeBadge.label}</Badge>
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-primary)' }}>
                      {truncateText(label, 45)}
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {TEMPLATE_LABELS[item.parametros?.template ?? ''] ?? '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className={statusBadge.className}>{statusBadge.label}</Badge>
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {item.tipo === 'presentacion' ? (item.slides_count ?? '—') : '—'}
                    </TableCell>
                    <TableCell style={{ color: 'var(--color-text-secondary)' }}>
                      {formatDate(item.creado_en)}
                    </TableCell>
                    <TableCell className="text-right">
                      <ItemActions item={item} align="end" />
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
