import PlanificacionClient from '@/components/features/planificacion/PlanificacionClient';

export default function PlanificacionPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Planificación
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Gestioná los cronogramas de cada proyecto y su avance.
        </p>
      </div>
      <PlanificacionClient />
    </div>
  );
}
