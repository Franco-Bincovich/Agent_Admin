'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import FuenteUploadSection from './FuenteUploadSection';
import EstructuraSection from './EstructuraSection';
import OpcionesSection from './OpcionesSection';
import DocumentoProgressTracker from './DocumentoProgressTracker';
import DocumentoResult from './DocumentoResult';
import { createDocumento } from '@/services/documentoService';
import type { Documento, DocumentoSeccion, DocumentoOpciones, ApiError } from '@/types';

const DEFAULT_OPCIONES: DocumentoOpciones = {
  homogeneizar:  false,
  deduplicar:    false,
  usar_imagenes: false,
};

export default function DocumentoForm() {
  const [archivos,     setArchivos]     = useState<File[]>([]);
  const [plantilla,    setPlantilla]    = useState<File | null>(null);
  const [logo,         setLogo]         = useState<File | null>(null);
  const [titulo,       setTitulo]       = useState('');
  const [secciones,    setSecciones]    = useState<DocumentoSeccion[]>([]);
  const [indicaciones, setIndicaciones] = useState('');
  const [opciones,     setOpciones]     = useState<DocumentoOpciones>(DEFAULT_OPCIONES);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [documentoId,  setDocumentoId]  = useState<string | null>(null);
  const [documento,    setDocumento]    = useState<Documento | null>(null);

  const isFormValid = archivos.length > 0 && titulo.trim().length >= 3;

  function toggleSeccion(s: DocumentoSeccion) {
    setSecciones((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);
  }

  function toggleOpcion(key: keyof DocumentoOpciones) {
    setOpciones((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      archivos.forEach((f) => fd.append('archivos', f));
      if (plantilla) fd.append('plantilla', plantilla);
      if (logo) fd.append('logo', logo);
      fd.append('titulo', titulo.trim());
      fd.append('secciones', JSON.stringify(secciones));
      if (indicaciones.trim()) fd.append('indicaciones', indicaciones.trim());
      fd.append('opciones', JSON.stringify(opciones));
      const doc = await createDocumento(fd);
      setDocumentoId(doc.id);
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'Error al iniciar la generación.');
      setIsSubmitting(false);
    }
  }

  function handleComplete(doc: Documento) {
    if (doc.estado === 'error') toast.error('Hubo un error al generar el documento. Intentá de nuevo.');
    setDocumento(doc);
  }

  function handleRetry() {
    setArchivos([]); setPlantilla(null); setLogo(null); setTitulo('');
    setSecciones([]); setIndicaciones(''); setOpciones(DEFAULT_OPCIONES);
    setIsSubmitting(false); setDocumentoId(null); setDocumento(null);
  }

  if (documento)   return <DocumentoResult documento={documento} onRetry={handleRetry} />;
  if (documentoId) return <DocumentoProgressTracker documentoId={documentoId} onComplete={handleComplete} />;

  return (
    <form onSubmit={handleSubmit} className="space-y-8" noValidate>
      <FuenteUploadSection
        archivos={archivos}
        onAdd={(f) => setArchivos((p) => [...p, ...f])}
        onRemove={(i) => setArchivos((p) => p.filter((_, idx) => idx !== i))}
        plantilla={plantilla}
        onSetPlantilla={setPlantilla}
        logo={logo}
        onSetLogo={setLogo}
        titulo={titulo}
        onTituloChange={setTitulo}
      />
      <hr style={{ borderColor: 'var(--color-border)' }} />
      <EstructuraSection
        secciones={secciones}
        onToggleSeccion={toggleSeccion}
        indicaciones={indicaciones}
        onIndicacionesChange={setIndicaciones}
      />
      <hr style={{ borderColor: 'var(--color-border)' }} />
      <OpcionesSection opciones={opciones} onToggleOpcion={toggleOpcion} />
      <Button
        type="submit"
        disabled={!isFormValid || isSubmitting}
        className="w-full min-h-[44px]"
        style={{ backgroundColor: isFormValid && !isSubmitting ? 'var(--color-primary)' : undefined }}
      >
        {isSubmitting ? 'Iniciando...' : 'Generar documento'}
      </Button>
      <p className="text-xs text-center" style={{ color: 'var(--color-text-disabled)' }}>
        Los campos con <span style={{ color: 'var(--color-error)' }}>*</span> son obligatorios
      </p>
    </form>
  );
}
