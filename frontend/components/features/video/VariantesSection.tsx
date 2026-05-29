'use client';

import { Plus } from 'lucide-react';
import VarianteConfig, { type VarianteValues } from './VarianteConfig';

interface VarianteItem {
  id: number;
  values: VarianteValues;
}

interface Props {
  variantes: VarianteItem[];
  onAdd: () => void;
  onChange: (id: number, values: VarianteValues) => void;
  onRemove: (id: number) => void;
}

export default function VariantesSection({ variantes, onAdd, onChange, onRemove }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            Variantes de edición
          </h3>
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-disabled)' }}>
            {variantes.length}/5 · Completá todos los campos de cada variante
          </p>
        </div>
        <button
          type="button"
          onClick={onAdd}
          disabled={variantes.length >= 5}
          className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition-colors disabled:opacity-40"
          style={{
            borderColor: 'var(--color-border)',
            color: variantes.length >= 5 ? 'var(--color-text-disabled)' : 'var(--color-primary)',
          }}
        >
          <Plus className="w-3.5 h-3.5" />
          Agregar variante
        </button>
      </div>

      <div className="space-y-2">
        {variantes.map((item, i) => (
          <VarianteConfig
            key={item.id}
            index={i}
            data={item.values}
            onChange={(values) => onChange(item.id, values)}
            onRemove={() => onRemove(item.id)}
          />
        ))}
      </div>
    </div>
  );
}
