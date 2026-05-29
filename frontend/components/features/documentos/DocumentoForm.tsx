'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import FuenteUploadSection from './FuenteUploadSection';
import EstructuraSection from './EstructuraSection';
import OpcionesSection from './OpcionesSection';
import DocumentoProgressTracker from './DocumentoProgressTracker';
import DocumentoResult from './DocumentoResult';
import { createDocumento } from '@/services/documentoService';
import { getMyTemplates } from '@/services/documentTemplateService';
import type { Documento, DocumentoOutcome, DocumentoSeccion, DocumentoOpciones, ApiError, DocumentTemplate } from '@/types';

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
  const [templates,          setTemplates]          = useState<DocumentTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  useEffect(() => {
    getMyTemplates().then(setTemplates).catch(() => {})
  }, [])

  const isFormValid = archivos.length > 0 && titulo.trim().length >= 3;

  function handleSelectTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId)
    if (!template) return
    setSelectedTemplateId(templateId)
    setSecciones(template.secciones)
  }

  function toggleOpcion(key: keyof DocumentoOpciones) {
    setOpciones((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const doc = await createDocumento({
        archivos,
        plantilla,
        logo,
        titulo: titulo.trim(),
        secciones,
        indicaciones: indicaciones.trim(),
        opciones,
      });
      setDocumentoId(doc.id);
    } catch (err) {
      const apiErr = err as ApiError;
      toast.error(apiErr?.message ?? 'Error al iniciar la generación.');
      setIsSubmitting(false);
    }
  }

  function handleComplete(doc: DocumentoOutcome) {
    if (doc.estado === 'error') toast.error('Hubo un error al generar el documento. Intentá de nuevo.');
    setDocumento(doc as Documento);
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
      {templates.length > 0 && (
        <div className="space-y-2">
          <label className="text-sm font-medium">
            Usar estructura pre-guardada
          </label>
          <select
            value={selectedTemplateId ?? ''}
            onChange={(e) => {
              if (e.target.value) handleSelectTemplate(e.target.value)
              else {
                setSelectedTemplateId(null)
                setSecciones([])
              }
            }}
            className="w-full border rounded-md px-3 py-2 text-sm
                       bg-background text-foreground
                       focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">— Seleccionar estructura —</option>
            {templates.map(t => (
              <option key={t.id} value={t.id}>
                {t.nombre}{t.is_default ? ' (por defecto)' : ''}
              </option>
            ))}
          </select>
          {selectedTemplateId && (
            <p className="text-xs text-muted-foreground">
              Las secciones se cargaron desde la estructura seleccionada.
            </p>
          )}
        </div>
      )}
      <EstructuraSection
        secciones={secciones}
        setSecciones={setSecciones}
        indicaciones={indicaciones}
        setIndicaciones={setIndicaciones}
        isDisabled={selectedTemplateId !== null}
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
