'use client';

import { useState } from 'react';
import type { EstiloEdicion, FormatoSalida, PosicionSubtitulos, ResolucionVideo } from '@/types';
import VarianteHeader from './VarianteHeader';
import VarianteContent from './VarianteContent';

export interface VarianteValues {
  estilo: EstiloEdicion | null;
  formato: FormatoSalida | null;
  posicion_subtitulos: PosicionSubtitulos | null;
  resolucion: ResolucionVideo | null;
}

interface Props {
  index: number;
  data: VarianteValues;
  onChange: (data: VarianteValues) => void;
  onRemove: () => void;
}

export default function VarianteConfig({ index, data, onChange, onRemove }: Props) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="rounded-lg border overflow-hidden" style={{ borderColor: 'var(--color-border)' }}>
      <VarianteHeader
        index={index}
        data={data}
        isOpen={isOpen}
        onToggle={() => setIsOpen((o) => !o)}
        onRemove={onRemove}
      />
      {isOpen && <VarianteContent data={data} onChange={onChange} />}
    </div>
  );
}
