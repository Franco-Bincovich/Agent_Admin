'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import FileUploadArea from './FileUploadArea';
import ProgressTracker from './ProgressTracker';
import GenerationResult from './GenerationResult';
import GammaConfigFields from './GammaConfigFields';
import BaseConfigFields from './BaseConfigFields';
import LogoPicker from './LogoPicker';
import { createGeneration } from '@/services/generationService';
import type {
  Generation, GenerationTemplate, GenerationTono,
  GenerationAudiencia, GenerationOutput, TemaVisual, EstiloImagen, ApiError,
} from '@/types';

export default function GeneratorForm() {
  const [files, setFiles]           = useState<File[]>([]);
  const [objetivo, setObjetivo]     = useState('');
  const [info, setInfo]             = useState('');
  const [template, setTemplate]     = useState<GenerationTemplate>('ejecutivo_oscuro');
  const [tono, setTono]             = useState<GenerationTono>('formal');
  const [audiencia, setAudiencia]   = useState<GenerationAudiencia>('directivos');
  const [output, setOutput]         = useState<GenerationOutput>('ambos');
  const [logo, setLogo]             = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [generation, setGeneration] = useState<Generation | null>(null);
  const [usarImagenes, setUsarImagenes]     = useState(false);
  const [temaVisual, setTemaVisual]         = useState<TemaVisual>('minimalist');
  const [estiloImagen, setEstiloImagen]     = useState<EstiloImagen>('aiGenerated');
  const [paletaColores, setPaletaColores]   = useState('');
  const [cantidadSlides, setCantidadSlides] = useState(10);

  useEffect(() => {
    if (!logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [logo]);
  const addFiles   = (incoming: File[]) => setFiles((prev) => [...prev, ...incoming]);
  const removeFile = (i: number)        => setFiles((prev) => prev.filter((_, idx) => idx !== i));
  const isFormValid = files.length > 0 && objetivo.trim().length >= 10;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      files.forEach((f) => fd.append('archivos', f));
      if (logo) fd.append('logo', logo);
      fd.append('objetivo', objetivo.trim());
      if (info.trim()) fd.append('informacion_adicional', info.trim());
      fd.append('template', template); fd.append('tono', tono);
      fd.append('audiencia', audiencia); fd.append('output', output);
      if (usarImagenes) fd.append('usar_imagenes_documento', 'true');
      if (output !== 'pptx') {
        fd.append('tema_visual', temaVisual); fd.append('estilo_imagen', estiloImagen);
        fd.append('paleta_colores', paletaColores); fd.append('cantidad_slides', String(cantidadSlides));
      }
      const gen = await createGeneration(fd);
      setGenerationId(gen.id);
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'Error al iniciar la generación.');
      setIsSubmitting(false);
    }
  }

  function handleRetry() {
    setFiles([]); setObjetivo(''); setInfo(''); setLogo(null); setIsSubmitting(false); setGenerationId(null); setGeneration(null);
    setTemplate('ejecutivo_oscuro'); setTono('formal'); setAudiencia('directivos'); setOutput('ambos');
    setUsarImagenes(false); setTemaVisual('minimalist'); setEstiloImagen('aiGenerated'); setPaletaColores(''); setCantidadSlides(10);
  }
  if (generation) return <GenerationResult generation={generation} onRetry={handleRetry} />;
  if (generationId) {
    return <ProgressTracker status="procesando" generationId={generationId} onComplete={setGeneration} />;
  }
  const TA_CLASS = 'w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <FileUploadArea files={files} onAdd={addFiles} onRemove={removeFile} />

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

      <LogoPicker logo={logo} logoPreview={logoPreview}
        onPick={(f) => setLogo(f)} onRemove={() => setLogo(null)} />

      <Button type="submit" disabled={!isFormValid || isSubmitting} className="w-full min-h-[44px]"
        style={{ backgroundColor: isFormValid && !isSubmitting ? 'var(--color-primary)' : undefined }}>
        {isSubmitting ? 'Iniciando...' : 'Generar presentación'}
      </Button>
    </form>
  );
}
