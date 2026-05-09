'use client';

import { useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

const STORAGE_KEY = 'theme';
const DEFAULT: Theme = 'dark';

function readStored(): Theme {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return v === 'light' || v === 'dark' ? v : DEFAULT;
  } catch {
    return DEFAULT;
  }
}

function applyTheme(t: Theme) {
  document.documentElement.setAttribute('data-theme', t);
}

export function useTheme() {
  // Inicializa con el default para evitar mismatch SSR; se corrige en el efecto.
  const [theme, setTheme] = useState<Theme>(DEFAULT);

  useEffect(() => {
    const stored = readStored();
    setTheme(stored);
    applyTheme(stored);
  }, []);

  function toggleTheme() {
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    applyTheme(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // localStorage no disponible (modo privado extremo)
    }
  }

  return { theme, toggleTheme };
}
