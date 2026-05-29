'use client';

import { Button } from '@/components/ui/button';
import FileUploadArea from './FileUploadArea';
import ProgressTracker from './ProgressTracker';
import GenerationResult from './GenerationResult';
import GammaConfigFields from './GammaConfigFields';
import BaseConfigFields from './BaseConfigFields';
import LogoPicker from './LogoPicker';
import { useGeneratorState } from '@/hooks/useGeneratorState';

export default function GeneratorForm() {
  const {
    files, setFiles, objetivo, setObjetivo, info, setInfo, template, setTemplate,
    tono, setTono, audiencia, setAudiencia, output, setOutput, logo, setLogo,
    logoPreview, isSubmitting, generationId, generation,
    usarImagenes, setUsarImagenes, temaVisual, setTemaVisual,
    estiloImagen, setEstiloImagen, paletaColores, setPaletaColores,
    cantidadSlides, setCantidadSlides, titulo, setTitulo,
    addFiles, removeFile, isFormValid, handleSubmit, handleRetry, handleGenerationComplete,
  } = useGeneratorState();

  if (generation) return <GenerationResult generation={generation} onRetry={handleRetry} />;
  if (generationId) {
    return <ProgressTracker status="procesando" generationId={generationId} onComplete={handleGenerationComplete} />;
  }
  const TA_CLASS    = 'w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';
  const INPUT_CLASS = 'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <FileUploadArea files={files} onAdd={addFiles} onRemove={removeFile} />

      <div className="space-y-3">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Título de la presentación{' '}<span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
        </label>
        <input
          type="text" value={titulo} onChange={(e) => setTitulo(e.target.value)}
          placeholder="Ej: Estrategia comercial Q2 2026"
          className={INPUT_CLASS}
        />
      </div>

      <div className="space-y-3">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Objetivo de la presentación <span style={{ color: 'var(--color-error)' }}>*</span>
        </label>
        <textarea value={objetivo} onChange={(e) => setObjetivo(e.target.value)} rows={3}
          placeholder="Ej: Presentar resultados Q1 a directivos y proponer plan de expansión..."
          className={TA_CLASS} />
        <p className="text-xs" style={{ color: objetivo.trim().length < 10 && objetivo.length > 0 ? 'var(--color-error)' : 'var(--color-text-disabled)' }}>
          Mínimo 10 caracteres ({objetivo.trim().length}/10)
        </p>
      </div>

      <div className="space-y-3">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Información adicional{' '}<span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
        </label>
        <textarea value={info} onChange={(e) => setInfo(e.target.value)} rows={2}
          placeholder="Contexto adicional, instrucciones especiales, datos clave a destacar..."
          className={TA_CLASS} />
      </div>

      <hr style={{ borderColor: 'var(--color-border)' }} />

      <BaseConfigFields
        template={template} setTemplate={setTemplate} tono={tono} setTono={setTono}
        audiencia={audiencia} setAudiencia={setAudiencia} output={output} setOutput={setOutput}
      />

      {output !== 'gamma' && (
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <input id="usar-imagenes" type="checkbox" checked={usarImagenes}
              onChange={(e) => setUsarImagenes(e.target.checked)}
              className="h-4 w-4 cursor-pointer rounded accent-[var(--color-primary)]" />
            <label htmlFor="usar-imagenes" className="text-sm font-medium cursor-pointer" style={{ color: 'var(--color-text-primary)' }}>
              Usar imágenes del documento
            </label>
          </div>
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Las imágenes extraídas de tus archivos se insertan directamente en la presentación
          </p>
        </div>
      )}

      {output !== 'pptx' && (
        <GammaConfigFields
          temaVisual={temaVisual} setTemaVisual={setTemaVisual}
          estiloImagen={estiloImagen} setEstiloImagen={setEstiloImagen}
          paletaColores={paletaColores} setPaletaColores={setPaletaColores}
          cantidadSlides={cantidadSlides} setCantidadSlides={setCantidadSlides}
        />
      )}

      {output !== 'gamma' && (
        <div className="space-y-1">
          <LogoPicker logo={logo} logoPreview={logoPreview}
            onPick={(f) => setLogo(f)} onRemove={() => setLogo(null)} />
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            El logo se incluye en el archivo PPTX descargable
          </p>
        </div>
      )}

      <Button type="submit" disabled={!isFormValid || isSubmitting} className="w-full min-h-[44px]"
        style={{ backgroundColor: isFormValid && !isSubmitting ? 'var(--color-primary)' : undefined }}>
        {isSubmitting ? 'Iniciando...' : 'Generar presentación'}
      </Button>
    </form>
  );
}
