import DocumentoForm from '@/components/features/documentos/DocumentoForm';

export default function DocumentosPage() {
  return (
    <div className="max-w-[800px] mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Documentos
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Unificá múltiples documentos en uno solo usando IA.
        </p>
      </div>

      <div
        className="rounded-lg border p-6"
        style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
      >
        <DocumentoForm />
      </div>
    </div>
  );
}
