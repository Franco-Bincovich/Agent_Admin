'use client';

import { useRef, useState } from 'react';
import { Plus, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import VideoUploadArea from './VideoUploadArea';
import BrandConfigFields from './BrandConfigFields';
import VarianteConfig, { type VarianteValues } from './VarianteConfig';
import { createVideoJob } from '@/services/videoService';
import type { BrandConfigValues, VideoJob, ApiError } from '@/types';

type FormStatus = 'idle' | 'uploading' | 'success';

interface VarianteItem { id: number; values: VarianteValues; }

const EMPTY_VARIANTE: VarianteValues = {
  estilo: null, formato: null, posicion_subtitulos: null, resolucion: null,
};

const EMPTY_BRAND: BrandConfigValues = {
  logo: null, colorPrimario: '', colorSecundario: '', fuente: '',
};

const INPUT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

export default function VideoForm() {
  const nextId = useRef(1);
  const [video, setVideo]         = useState<File | null>(null);
  const [titulo, setTitulo]       = useState('');
  const [brand, setBrand]         = useState<BrandConfigValues>(EMPTY_BRAND);
  const [variantes, setVariantes] = useState<VarianteItem[]>([{ id: 0, values: { ...EMPTY_VARIANTE } }]);
  const [status, setStatus]       = useState<FormStatus>('idle');
  const [createdJob, setCreatedJob] = useState<VideoJob | null>(null);

  const isFormValid =
    video !== null &&
    titulo.trim().length > 0 &&
    variantes.length > 0 &&
    variantes.every((v) => v.values.estilo && v.values.formato && v.values.posicion_subtitulos && v.values.resolucion);

  function addVariante() {
    if (variantes.length >= 5) return;
    setVariantes((prev) => [...prev, { id: nextId.current++, values: { ...EMPTY_VARIANTE } }]);
  }

  function updateVariante(id: number, values: VarianteValues) {
    setVariantes((prev) => prev.map((v) => v.id === id ? { ...v, values } : v));
  }

  function removeVariante(id: number) {
    setVariantes((prev) => prev.filter((v) => v.id !== id));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || status === 'uploading' || !video) return;
    setStatus('uploading');
    try {
      const fd = new FormData();
      fd.append('video', video);
      fd.append('titulo', titulo.trim());
      fd.append('variantes', JSON.stringify(variantes.map((v) => v.values)));
      // Brand config
      if (brand.logo) {
        fd.append('logo', brand.logo);
      }
      if (brand.colorPrimario.trim()) {
        fd.append('color_primario', brand.colorPrimario.trim());
      }
      if (brand.colorSecundario.trim()) {
        fd.append('color_secundario', brand.colorSecundario.trim());
      }
      if (brand.fuente.trim()) {
        fd.append('fuente', brand.fuente.trim());
      }
      const job = await createVideoJob(fd);
      setCreatedJob(job);
      setStatus('success');
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'Error al crear el job de video.');
      setStatus('idle');
    }
  }

  function handleReset() {
    setVideo(null); setTitulo(''); setBrand(EMPTY_BRAND);
    setVariantes([{ id: nextId.current++, values: { ...EMPTY_VARIANTE } }]);
    setStatus('idle'); setCreatedJob(null);
  }

  if (status === 'success' && createdJob) {
    return (
      <div className="flex flex-col items-center gap-4 py-10 text-center">
        <CheckCircle className="w-12 h-12" style={{ color: 'var(--color-primary)' }} />
        <div className="space-y-1">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            Tu video está en cola
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Job ID:{' '}
            <span className="font-mono text-xs" style={{ color: 'var(--color-text-primary)' }}>
              {createdJob.id}
            </span>
          </p>
        </div>
        <button
          type="button"
          onClick={handleReset}
          className="text-sm underline underline-offset-2"
          style={{ color: 'var(--color-primary)' }}
        >
          Crear otro job
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      <VideoUploadArea file={video} onSelect={setVideo} onRemove={() => setVideo(null)} />

      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
          Título del job <span style={{ color: 'var(--color-error)' }}>*</span>
        </label>
        <input
          type="text"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          placeholder="Ej: Campaña verano 2026 — versión redes"
          className={INPUT_CLASS}
        />
      </div>

      <BrandConfigFields values={brand} onChange={setBrand} />

      <hr style={{ borderColor: 'var(--color-border)' }} />

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              Variantes de edición
            </h3>
            <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-disabled)' }}>
              {variantes.length}/5 · Completá todos los campos de cada variante
            </p>
          </div>
          <button
            type="button"
            onClick={addVariante}
            disabled={variantes.length >= 5}
            className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-colors disabled:opacity-40"
            style={{
              borderColor: 'var(--color-border)',
              color: variantes.length >= 5 ? 'var(--color-text-disabled)' : 'var(--color-primary)',
            }}
          >
            <Plus className="w-3.5 h-3.5" />
            Agregar variante
          </button>
        </div>

        <div className="space-y-2">
          {variantes.map((item, i) => (
            <VarianteConfig
              key={item.id}
              index={i}
              data={item.values}
              onChange={(values) => updateVariante(item.id, values)}
              onRemove={() => removeVariante(item.id)}
            />
          ))}
        </div>
      </div>

      <Button
        type="submit"
        disabled={!isFormValid || status === 'uploading'}
        className="w-full min-h-[44px]"
        style={{
          backgroundColor: isFormValid && status !== 'uploading' ? 'var(--color-primary)' : undefined,
        }}
      >
        {status === 'uploading' ? 'Subiendo...' : 'Iniciar edición'}
      </Button>
    </form>
  );
}
