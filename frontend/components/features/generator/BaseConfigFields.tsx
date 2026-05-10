'use client';

import type {
  GenerationTemplate,
  GenerationTono,
  GenerationAudiencia,
  GenerationOutput,
} from '@/types';

const TEMPLATES: [GenerationTemplate, string][] = [
  ['ejecutivo_oscuro',   'Ejecutivo oscuro'],
  ['profesional_claro',  'Profesional claro'],
  ['corporativo_neutro', 'Corporativo neutro'],
];

const TONOS: [GenerationTono, string][] = [
  ['formal',        'Formal'],
  ['institucional', 'Institucional'],
  ['comercial',     'Comercial'],
  ['tecnico',       'Técnico'],
];

const AUDIENCIAS: [GenerationAudiencia, string][] = [
  ['directivos',     'Directivos'],
  ['equipo_interno', 'Equipo interno'],
  ['clientes',       'Clientes'],
  ['tecnicos',       'Técnicos'],
];

const OUTPUTS: [GenerationOutput, string][] = [
  ['ambos', 'PPTX + Gamma'],
  ['pptx',  'Solo PPTX'],
  ['gamma', 'Solo Gamma'],
];

const SELECT_CLASS =
  'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-[var(--color-background)] text-[var(--color-text-primary)] border-[var(--color-border)]';

interface Props {
  template: GenerationTemplate; setTemplate: (v: GenerationTemplate) => void;
  tono: GenerationTono;         setTono: (v: GenerationTono) => void;
  audiencia: GenerationAudiencia; setAudiencia: (v: GenerationAudiencia) => void;
  output: GenerationOutput;     setOutput: (v: GenerationOutput) => void;
}

export default function BaseConfigFields({ template, setTemplate, tono, setTono, audiencia, setAudiencia, output, setOutput }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Template</label>
        <select value={template} onChange={(e) => setTemplate(e.target.value as GenerationTemplate)} className={SELECT_CLASS}>
          {TEMPLATES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Tono</label>
        <select value={tono} onChange={(e) => setTono(e.target.value as GenerationTono)} className={SELECT_CLASS}>
          {TONOS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Audiencia</label>
        <select value={audiencia} onChange={(e) => setAudiencia(e.target.value as GenerationAudiencia)} className={SELECT_CLASS}>
          {AUDIENCIAS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
      <div className="space-y-1.5">
        <label className="block text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Output</label>
        <select value={output} onChange={(e) => setOutput(e.target.value as GenerationOutput)} className={SELECT_CLASS}>
          {OUTPUTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
    </div>
  );
}
