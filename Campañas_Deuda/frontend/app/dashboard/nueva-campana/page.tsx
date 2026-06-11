'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { PageLayout } from '@/components/features/layout/PageLayout'
import { DimensionSelector } from '@/components/features/campana/DimensionSelector'
import { FileUpload } from '@/components/features/campana/FileUpload'
import { Button } from '@/components/ui/Button'

const CARTERA_OPTS = [
  { value: 'servicios_generales', label: 'Servicios Generales' },
  { value: 'servicio_sanitario', label: 'Sanitario (Agua)' },
  { value: 'automotor', label: 'Automotor' },
  { value: 'todas', label: 'Todas' },
]
const DUREZA_OPTS = [
  { value: 'blanda', label: 'Blanda' },
  { value: 'intermedia', label: 'Intermedia' },
  { value: 'dura', label: 'Dura' },
  { value: 'todas', label: 'Todas' },
]
const PERIODO_OPTS = ['2021', '2022', '2023', '2024', '2025', '2026', 'todas'].map((v) => ({
  value: v,
  label: v === 'todas' ? 'Todos los períodos' : v,
}))

export default function NuevaCampanaPage() {
  const router = useRouter()
  const [cartera, setCartera] = useState('')
  const [dureza, setDureza] = useState('')
  const [periodo, setPeriodo] = useState('')
  const [fileReady, setFileReady] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const isValid = cartera && dureza && periodo && fileReady

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid) return
    setIsSubmitting(true)
    // TODO Sesión 6: POST /api/executions con portfolio_file_id + dimensiones
    await new Promise<void>((r) => setTimeout(r, 1000))
    toast.success('Corrida iniciada. Podés seguir el avance en Ejecuciones.')
    router.push('/dashboard/ejecuciones')
  }

  return (
    <PageLayout title="Nueva campaña" description="Configurá el análisis de la cartera de deuda">
      <form onSubmit={handleSubmit} className="flex flex-col gap-8 max-w-2xl">
        {/* Archivo */}
        <section className="flex flex-col gap-3">
          <h2 className="text-sm font-semibold text-gray-800">
            1. Cargar archivo de cartera <span className="text-red-500">*</span>
          </h2>
          <p className="text-xs text-gray-500">
            Subí el archivo con los datos agregados de la cartera. Los agentes trabajan sobre
            totales — nunca sobre datos individuales de contribuyentes.
          </p>
          <FileUpload onFileReady={() => setFileReady(true)} />
        </section>

        {/* Dimensiones */}
        <section className="flex flex-col gap-6">
          <h2 className="text-sm font-semibold text-gray-800">2. Seleccioná las dimensiones</h2>
          <p className="text-xs text-gray-500 -mt-3">
            Una opción por dimensión. Seleccioná &quot;Todas&quot; para incluir todo el segmento.
          </p>
          <DimensionSelector
            id="cartera"
            label="Cartera"
            options={CARTERA_OPTS}
            value={cartera}
            onChange={setCartera}
            required
          />
          <DimensionSelector
            id="dureza"
            label="Dureza de deuda"
            options={DUREZA_OPTS}
            value={dureza}
            onChange={setDureza}
            required
          />
          <DimensionSelector
            id="periodo"
            label="Período"
            description="Año de origen de la deuda"
            options={PERIODO_OPTS}
            value={periodo}
            onChange={setPeriodo}
            required
          />
        </section>

        {/* Nota */}
        <p className="text-xs text-gray-400">Los campos marcados con * son obligatorios</p>

        {/* Acción */}
        <Button
          type="submit"
          loading={isSubmitting}
          disabled={!isValid}
          title={!isValid ? 'Completá todos los campos para continuar' : undefined}
          className="w-full sm:w-auto"
        >
          {isSubmitting ? 'Iniciando análisis...' : 'Iniciar análisis con IA'}
        </Button>
      </form>
    </PageLayout>
  )
}
