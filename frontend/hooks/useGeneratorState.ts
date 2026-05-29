import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { createGeneration } from '@/services/generationService';
import type {
  Generation, GenerationOutcome, GenerationTemplate, GenerationTono,
  GenerationAudiencia, GenerationOutput, TemaVisual, EstiloImagen, ApiError,
} from '@/types';

export function useGeneratorState() {
  const [files, setFiles] = useState<File[]>([]);
  const [objetivo, setObjetivo] = useState('');
  const [info, setInfo] = useState('');
  const [template, setTemplate] = useState<GenerationTemplate>('ejecutivo_oscuro');
  const [tono, setTono] = useState<GenerationTono>('formal');
  const [audiencia, setAudiencia] = useState<GenerationAudiencia>('directivos');
  const [output, setOutput] = useState<GenerationOutput>('ambos');
  const [logo, setLogo] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [generation, setGeneration] = useState<Generation | null>(null);
  const [usarImagenes, setUsarImagenes] = useState(false);
  const [temaVisual, setTemaVisual] = useState<TemaVisual>('minimalist');
  const [estiloImagen, setEstiloImagen] = useState<EstiloImagen>('aiGenerated');
  const [paletaColores, setPaletaColores] = useState('');
  const [cantidadSlides, setCantidadSlides] = useState(10);
  const [titulo, setTitulo] = useState('');

  useEffect(() => {
    if (!logo) { setLogoPreview(null); return; }
    const url = URL.createObjectURL(logo);
    setLogoPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [logo]);

  const addFiles = (incoming: File[]) => setFiles((prev) => [...prev, ...incoming]);
  const removeFile = (i: number) => setFiles((prev) => prev.filter((_, idx) => idx !== i));
  const isFormValid = files.length > 0 && objetivo.trim().length >= 10;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      files.forEach((f) => fd.append('archivos', f));
      if (logo) fd.append('logo', logo);
      fd.append('titulo', titulo.trim());
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
    setFiles([]); setTitulo(''); setObjetivo(''); setInfo(''); setLogo(null); setIsSubmitting(false); setGenerationId(null); setGeneration(null);
    setTemplate('ejecutivo_oscuro'); setTono('formal'); setAudiencia('directivos'); setOutput('ambos');
    setUsarImagenes(false); setTemaVisual('minimalist'); setEstiloImagen('aiGenerated'); setPaletaColores(''); setCantidadSlides(10);
  }

  function handleGenerationComplete(result: GenerationOutcome) {
    if (result.estado === 'error') toast.error('Hubo un error al generar la presentación. Intentá de nuevo.');
    setGeneration(result as Generation);
  }

  return {
    files, setFiles, objetivo, setObjetivo, info, setInfo, template, setTemplate,
    tono, setTono, audiencia, setAudiencia, output, setOutput, logo, setLogo,
    logoPreview, isSubmitting, generationId, generation,
    usarImagenes, setUsarImagenes, temaVisual, setTemaVisual,
    estiloImagen, setEstiloImagen, paletaColores, setPaletaColores,
    cantidadSlides, setCantidadSlides, titulo, setTitulo,
    addFiles, removeFile, isFormValid, handleSubmit, handleRetry, handleGenerationComplete,
  };
}
