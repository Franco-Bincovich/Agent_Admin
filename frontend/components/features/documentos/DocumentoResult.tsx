'use client';

import { Download, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Documento } from '@/types';

interface Props {
  documento: Documento;
  onRetry: () => void;
}

export default function DocumentoResult({ documento, onRetry }: Props) {
  if (documento.estado === 'error') {
    return (
      <div className="space-y-4 text-center py-4">
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          Hubo un error al generar el documento. Intentá de nuevo.
        </p>
        <Button type="button" onClick={onRetry} variant="outline" className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Intentar de nuevo
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4 text-center py-4">
      <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        ¡Documento listo!
      </p>
      <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
        {documento.titulo}
      </p>
      {documento.estado === 'listo' && documento.docx_url && (
        <a
          href={documento.docx_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-white font-medium text-sm hover:opacity-90 transition-opacity"
        >
          <Download className="w-4 h-4" />
          Descargar documento
        </a>
      )}
      <div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="gap-2 border-white/20 text-white hover:bg-white/10"
        >
          <RefreshCw className="w-4 h-4" />
          Generar otro documento
        </Button>
      </div>
    </div>
  );
}
