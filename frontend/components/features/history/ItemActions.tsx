import { Download, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { sanitizeFilename } from './historyConstants';
import type { ActivityItem } from '@/types';

interface ItemActionsProps {
  item: ActivityItem;
  align: 'end' | 'stretch';
}

export function ItemActions({ item, align }: ItemActionsProps) {
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
        <a href={item.docx_url} download={`${sanitizeFilename(item.titulo ?? '') || 'documento'}.docx`} className={aClass}>
          <Button variant="ghost" size="sm" className={btnClass} style={{ color: 'var(--color-text-secondary)' }}>
            <Download className="w-3.5 h-3.5" />
            Descargar DOCX
          </Button>
        </a>
      )}
    </div>
  );
}
