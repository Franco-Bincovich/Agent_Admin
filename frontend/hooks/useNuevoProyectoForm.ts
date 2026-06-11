'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { createProyecto } from '@/services/planificacionService';
import type { Proyecto, ProyectoPrioridad, ApiError } from '@/types';

interface Params {
  onClose: () => void;
  onCreated: (proyecto: Proyecto) => void;
}

interface FormState {
  nombre: string;
  expediente: string;
  prioridad: ProyectoPrioridad;
  archivo: File | null;
}

const EMPTY: FormState = { nombre: '', expediente: '', prioridad: 'media', archivo: null };

export function useNuevoProyectoForm({ onClose, onCreated }: Params) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormState>(EMPTY);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function canNext() {
    if (step === 1) return form.nombre.trim().length > 0;
    if (step === 2) return form.archivo !== null;
    return true;
  }

  function handleNext() {
    if (canNext() && step < 4) setStep((s) => s + 1);
  }

  function handleBack() {
    if (step > 1) setStep((s) => s - 1);
  }

  function handleClose() {
    if (isSubmitting) return;
    setStep(1);
    setForm(EMPTY);
    onClose();
  }

  async function handleSubmit() {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      fd.append('nombre', form.nombre.trim());
      if (form.expediente.trim()) fd.append('expediente', form.expediente.trim());
      fd.append('prioridad', form.prioridad);
      if (form.archivo) fd.append('archivo', form.archivo);
      const proyecto = await createProyecto(fd);
      onCreated(proyecto);
      setStep(1);
      setForm(EMPTY);
      onClose();
    } catch (err) {
      toast.error((err as ApiError)?.message ?? 'No se pudo crear el proyecto.');
      setIsSubmitting(false);
    }
  }

  return { step, form, setForm, isSubmitting, canNext, handleNext, handleBack, handleClose, handleSubmit };
}
