import GeneratorForm from '@/components/features/generator/GeneratorForm';

export default function GeneratorPage() {
  return (
    <div className="max-w-[800px] mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Generador de slides
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Subí tus archivos, definí el objetivo y dejá que la IA construya tu presentación.
        </p>
      </div>

      <div
        className="rounded-lg border p-6"
        style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
      >
        <GeneratorForm />
      </div>
    </div>
  );
}
