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
      {documento.docx_url && (
        <a
          href={documento.docx_url}
          download
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium min-h-[44px] transition-colors"
          style={{
            backgroundColor: 'var(--color-primary)',
            color: '#fff',
          }}
        >
          <Download className="w-4 h-4" />
          Descargar Word (.docx)
        </a>
      )}
      <div>
        <button
          type="button"
          onClick={onRetry}
          className="text-xs underline"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Generar otro documento
        </button>
      </div>
    </div>
  );
}
