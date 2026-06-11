'use client'

import { useCallback, useRef, useState } from 'react'
import { CheckCircle2, FileSpreadsheet, Loader2, Upload, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatBytes } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

type UploadState = 'idle' | 'dragging' | 'uploading' | 'done' | 'error'

const ALLOWED_TYPES = [
  'text/csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/pdf',
]
const ALLOWED_EXT = ['.csv', '.xlsx', '.pdf']
const MAX_MB = 50

interface FileUploadProps {
  onFileReady: (file: File) => void
  className?: string
}

export function FileUpload({ onFileReady, className }: FileUploadProps) {
  const [state, setState] = useState<UploadState>('idle')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [errorMsg, setErrorMsg] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    (file: File) => {
      setErrorMsg('')
      if (!ALLOWED_TYPES.includes(file.type) && !ALLOWED_EXT.some((e) => file.name.endsWith(e))) {
        setState('error')
        setErrorMsg('Solo se aceptan archivos CSV, XLSX o PDF.')
        return
      }
      if (file.size > MAX_MB * 1024 * 1024) {
        setState('error')
        setErrorMsg(`El archivo supera el límite de ${MAX_MB} MB.`)
        return
      }
      setSelectedFile(file)
      setState('uploading')
      // TODO Sesión 5: enviar al endpoint POST /api/portfolio/upload
      setTimeout(() => {
        setState('done')
        onFileReady(file)
      }, 1500)
    },
    [onFileReady]
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setState('idle')
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const reset = () => {
    setState('idle')
    setSelectedFile(null)
    setErrorMsg('')
  }

  if (state === 'done' && selectedFile) {
    return (
      <div
        className={cn(
          'flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 p-4',
          className
        )}
      >
        <CheckCircle2 className="h-8 w-8 flex-shrink-0 text-green-500" aria-hidden />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-green-800 truncate">{selectedFile.name}</p>
          <p className="text-xs text-green-600">
            {formatBytes(selectedFile.size)} · Listo para analizar
          </p>
        </div>
        <Button size="icon" variant="ghost" onClick={reset} aria-label="Quitar archivo">
          <X className="h-4 w-4 text-green-600" />
        </Button>
      </div>
    )
  }

  if (state === 'uploading') {
    return (
      <div
        className={cn(
          'flex items-center gap-3 rounded-xl border border-card-border bg-surface p-4',
          className
        )}
      >
        <Loader2 className="h-6 w-6 animate-spin text-secondary" aria-hidden />
        <p className="text-sm text-gray-600">Verificando archivo...</p>
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setState('dragging')
        }}
        onDragLeave={() => setState('idle')}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Zona de carga de archivo. Clic o arrastrá para seleccionar"
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        className={cn(
          'flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 transition-all',
          state === 'dragging'
            ? 'border-secondary bg-secondary/5'
            : state === 'error'
              ? 'border-red-400 bg-red-50'
              : 'border-card-border bg-background hover:border-secondary/50 hover:bg-secondary/5'
        )}
      >
        <FileSpreadsheet
          className={cn('h-10 w-10', state === 'error' ? 'text-red-400' : 'text-gray-400')}
          aria-hidden
        />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700">
            {state === 'dragging'
              ? 'Soltá el archivo acá'
              : 'Arrastrá o hacé clic para subir la cartera'}
          </p>
          <p className="mt-1 text-xs text-gray-500">CSV, XLSX o PDF · Máximo {MAX_MB} MB</p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-surface border border-card-border px-4 py-2">
          <Upload className="h-4 w-4 text-secondary" aria-hidden />
          <span className="text-sm font-medium text-secondary">Seleccionar archivo</span>
        </div>
      </div>
      {errorMsg && (
        <p className="text-sm text-red-600" role="alert">
          {errorMsg}
        </p>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.pdf"
        className="sr-only"
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) handleFile(f)
        }}
        aria-hidden
      />
    </div>
  )
}
