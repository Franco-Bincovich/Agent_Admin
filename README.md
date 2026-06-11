# Agent-Admin

Plataforma interna de productividad con IA que genera presentaciones (PPTX + Gamma), documentos Word (DOCX), gestiona plantillas reutilizables y planifica proyectos con vistas Gantt a partir de cronogramas (MPP/XML/Excel), usando Claude como motor de generación.

## Requisitos

- Python 3.11+
- Node.js 20+ (Next.js 16 + React 19)
- Cuenta en Supabase (PostgreSQL + Storage + Auth)
- API key de Anthropic (Claude Sonnet)
- API key de Gamma (opcional — el pipeline PPTX funciona sin Gamma)
- Cuenta en Vercel para deploy (frontend + backend serverless)

## Instalación

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Agent-Admin

# 2. Configurar variables de entorno (ver .env.example de cada lado)
cp backend/.env.example backend/.env        # credenciales reales
# frontend/.env.local con NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Instalar dependencias
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Aplicar migraciones en Supabase
# Ejecutar los SQL de backend/migrations/ en orden (001 → 017)
# desde el SQL editor de Supabase
```

## Cómo correr

```bash
# Backend (desde backend/) — http://localhost:8000
uvicorn main:app --reload

# Frontend (desde frontend/) — http://localhost:3000
npm run dev

# Tests (desde backend/)
pytest tests/test_critical_flows.py -v
```
