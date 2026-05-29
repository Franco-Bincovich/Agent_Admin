import PlantillasClient from '@/components/features/plantillas/PlantillasClient';

export default function PlantillasPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Estructuras de documentos</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Guardá combinaciones de secciones como estructuras reutilizables para tus documentos.
        </p>
      </div>
      <PlantillasClient />
    </div>
  );
}
