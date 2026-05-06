import { Download, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Generation } from '@/types';

interface Props {
  generation: Generation;
  onRetry: () => void;
}

export default function GenerationResult({ generation, onRetry }: Props) {
  const isSuccess = generation.estado === 'listo';

  return (
    <div
      className="space-y-5 p-6 rounded-lg border text-center"
      style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
    >
      <p
        className="text-lg font-semibold"
        style={{ color: isSuccess ? 'var(--color-success)' : 'var(--color-error)' }}
      >
        {isSuccess ? '¡Tu presentación está lista!' : 'Hubo un error en la generación.'}
      </p>

      {isSuccess && (
        <div className="flex justify-center gap-3 flex-wrap">
          {generation.pptx_url && (
            <a href={generation.pptx_url} download>
              <Button><Download className="w-4 h-4 mr-2" />Descargar PPTX</Button>
            </a>
          )}
          {generation.gamma_url && (
            <a href={generation.gamma_url} target="_blank" rel="noopener noreferrer">
              <Button variant="outline">
                <ExternalLink className="w-4 h-4 mr-2" />Abrir en Gamma
              </Button>
            </a>
          )}
        </div>
      )}

      <button
        onClick={onRetry}
        className="text-sm underline-offset-2 hover:underline"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        Generar otra presentación
      </button>
    </div>
  );
}
