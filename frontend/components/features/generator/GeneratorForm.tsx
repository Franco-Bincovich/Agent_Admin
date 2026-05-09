'use client';

import { useEffect, useRef, useState } from 'react';
import { Image, X } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import FileUploadArea from './FileUploadArea';
import ProgressTracker from './ProgressTracker';
import GenerationResult from './GenerationResult';
import { createGeneration } from '@/services/generationService';
import type {
  Generation,
  GenerationTemplate,
  GenerationTono,
  GenerationAudiencia,
  GenerationOutput,
  ApiError,
} from '@/types';

const TEMPLATES: [GenerationTemplate, string][] = [
  ['ejecutivo_oscuro',   'Ejecutivo oscuro'],
  ['profesional_claro',  'Profesional claro'],
  ['corporativo_neutro', 'Corporativo neutro'],
];

const TONOS: [GenerationTono, string][] = [
  ['formal',        'Formal'],
  ['institucional', 'Institucional'],
  ['comercial',     'Comercial'],
  ['tecnico',       'Técnico'],
];

const AUDIENCIAS: [GenerationAudiencia, string][] = [
  ['directivos',     'Directivos'],
  ['equipo_interno', 'Equipo interno'],
  ['clientes',       'Clientes'],
  ['tecnicos',       'Técnicos'],
];

const OUTPUTS: [GenerationOutput, string][] = [
  ['ambos', 'PPTX + Gamma'],
  ['pptx',  'Solo PPTX'],
  ['gamma', 'Solo Gamma'],
];

const SELECT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] border-[var(--color-border)]';

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
  const logoRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [logo]);

  function handleLogoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const ext = f.name.split('.').pop()?.toLowerCase() ?? '';
    if (!['png', 'jpg', 'jpeg'].includes(ext) || f.size > 2 * 1024 * 1024) return;
    setLogo(f);
    e.target.value = '';
  }

  const addFiles   = (incoming: File[]) => setFiles((prev) => [...prev, ...incoming]);
  const removeFile = (i: number)        => setFiles((prev) => prev.filter((_, idx) => idx !== i));
  const isFormValid = files.length > 0 && objetivo.trim().length >= 10;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      files.forEach((f) => fd.append('files', f));
      if (logo) fd.append('logo', logo);
      fd.append('objetivo', objetivo.trim());
      if (info.trim()) fd.append('info_adicional', info.trim());
      fd.append('template', template);
      fd.append('tono', tono);
      fd.append('audiencia', audiencia);
      fd.append('output', output);
      const gen = await createGeneration(fd);
      setGenerationId(gen.id);
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'Error al iniciar la generación.');
      setIsSubmitting(false);
    }
  }

  function handleRetry() {
    setFiles([]);
    setObjetivo('');
    setInfo('');
    setTemplate('ejecutivo_oscuro');
    setTono('formal');
    setAudiencia('directivos');
    setOutput('ambos');
    setLogo(null);
    setIsSubmitting(false);
    setGenerationId(null);
    setGeneration(null);
  }

  if (generation) {
    return <GenerationResult generation={generation} onRetry={handleRetry} />;
  }

  if (generationId) {
    return (
      <ProgressTracker
        status="procesando"
        generationId={generationId}
        onComplete={setGeneration}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <FileUploadArea files={files} onAdd={addFiles} onRemove={removeFile} />

      <div className="space-y-3">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Objetivo de la presentación <span style={{ color: 'var(--color-error)' }}>*</span>
        </label>
        <textarea
          value={objetivo}
          onChange={(e) => setObjetivo(e.target.value)}
          placeholder="Ej: Presentar resultados Q1 a directivos y proponer plan de expansión..."
          rows={3}
          className="w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]"
        />
        <p className="text-xs" style={{ color: objetivo.trim().length < 10 && objetivo.length > 0 ? 'var(--color-error)' : 'var(--color-text-disabled)' }}>
          Mínimo 10 caracteres ({objetivo.trim().length}/10)
        </p>
      </div>

      <div className="space-y-3">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Información adicional{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
        </label>
        <textarea
          value={info}
          onChange={(e) => setInfo(e.target.value)}
          placeholder="Contexto adicional, instrucciones especiales, datos clave a destacar..."
          rows={2}
          className="w-full rounded-lg border px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]"
        />
      </div>

      <hr style={{ borderColor: 'var(--color-border)' }} />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Template</label>
          <select value={template} onChange={(e) => setTemplate(e.target.value as GenerationTemplate)} className={SELECT_CLASS}>
            {TEMPLATES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Tono</label>
          <select value={tono} onChange={(e) => setTono(e.target.value as GenerationTono)} className={SELECT_CLASS}>
            {TONOS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Audiencia</label>
          <select value={audiencia} onChange={(e) => setAudiencia(e.target.value as GenerationAudiencia)} className={SELECT_CLASS}>
            {AUDIENCIAS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Output</label>
          <select value={output} onChange={(e) => setOutput(e.target.value as GenerationOutput)} className={SELECT_CLASS}>
            {OUTPUTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Logo{' '}
          <span style={{ color: 'var(--color-text-disabled)' }}>(opcional · PNG, JPG, JPEG · máx 2MB)</span>
        </label>
        {logo ? (
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-background)' }}>
            {logoPreview ? (
              <img src={logoPreview} alt="Logo" className="h-8 w-8 object-contain flex-shrink-0 rounded" />
            ) : (
              <Image className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-text-secondary)' }} />
            )}
            <span className="text-sm flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{logo.name}</span>
            <button type="button" onClick={() => setLogo(null)} className="flex-shrink-0 p-0.5 rounded hover:bg-red-500/10 transition-colors" aria-label="Eliminar logo">
              <X className="w-3.5 h-3.5" style={{ color: 'var(--color-text-secondary)' }} />
            </button>
          </div>
        ) : (
          <button type="button" onClick={() => logoRef.current?.click()} className="text-sm px-3 py-2 rounded-lg border transition-colors hover:bg-white/5" style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
            Subir logo
          </button>
        )}
        <input ref={logoRef} type="file" accept=".png,.jpg,.jpeg" className="hidden" onChange={handleLogoChange} />
      </div>

      <Button
        type="submit"
        disabled={!isFormValid || isSubmitting}
        className="w-full min-h-[44px]"
        style={{ backgroundColor: isFormValid && !isSubmitting ? 'var(--color-primary)' : undefined }}
      >
        {isSubmitting ? 'Iniciando...' : 'Generar presentación'}
      </Button>
    </form>
  );
}
