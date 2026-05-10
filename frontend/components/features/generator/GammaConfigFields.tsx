import type { EstiloImagen, TemaVisual } from '@/types';

const SELECT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] border-[var(--color-border)]';

const INPUT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-disabled)] border-[var(--color-border)]';

const TEMAS_VISUALES: [TemaVisual, string][] = [
  ['minimalist', 'Minimalista'],
  ['playful',    'Dinámico'],
  ['organic',    'Orgánico'],
  ['modular',    'Modular'],
  ['elegant',    'Elegante'],
  ['digital',    'Digital'],
  ['geometric',  'Geométrico'],
];

const ESTILOS_IMAGEN: [EstiloImagen, string][] = [
  ['aiGenerated',  'Generadas por IA'],
  ['pictographic', 'Íconos'],
  ['pexels',       'Fotos reales (Pexels)'],
  ['noImages',     'Sin imágenes'],
];

type Props = {
  temaVisual: TemaVisual;
  setTemaVisual: (v: TemaVisual) => void;
  estiloImagen: EstiloImagen;
  setEstiloImagen: (v: EstiloImagen) => void;
  paletaColores: string;
  setPaletaColores: (v: string) => void;
  cantidadSlides: number;
  setCantidadSlides: (v: number) => void;
};

export default function GammaConfigFields({
  temaVisual,
  setTemaVisual,
  estiloImagen,
  setEstiloImagen,
  paletaColores,
  setPaletaColores,
  cantidadSlides,
  setCantidadSlides,
}: Props) {
  return (
    <div
      className="space-y-4 p-4 rounded-lg border"
      style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-surface)' }}
    >
      <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
        Configuración de Gamma
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Tema visual
          </label>
          <select
            value={temaVisual}
            onChange={(e) => setTemaVisual(e.target.value as TemaVisual)}
            className={SELECT_CLASS}
          >
            {TEMAS_VISUALES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Estilo de imágenes
          </label>
          <select
            value={estiloImagen}
            onChange={(e) => setEstiloImagen(e.target.value as EstiloImagen)}
            className={SELECT_CLASS}
          >
            {ESTILOS_IMAGEN.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Paleta de colores{' '}
            <span style={{ color: 'var(--color-text-disabled)' }}>(opcional)</span>
          </label>
          <input
            type="text"
            value={paletaColores}
            onChange={(e) => setPaletaColores(e.target.value)}
            placeholder="Ej: azul navy, blanco, acento naranja"
            className={INPUT_CLASS}
          />
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Describí los colores que querés que use Gamma
          </p>
        </div>
        <div className="space-y-1.5">
          <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Cantidad de slides
          </label>
          <input
            type="number"
            min={5}
            max={20}
            value={cantidadSlides}
            onChange={(e) => setCantidadSlides(Number(e.target.value))}
            className={INPUT_CLASS}
          />
          <p className="text-xs" style={{ color: 'var(--color-text-disabled)' }}>
            Entre 5 y 20 slides
          </p>
        </div>
      </div>
    </div>
  );
}
