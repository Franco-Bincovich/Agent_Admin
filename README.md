# Agent Admin — Plataforma de Generación de Documentos

Plataforma web para generar presentaciones PPTX y documentos DOCX a partir de archivos fuente, usando IA (Claude) y plantillas visuales predefinidas.

## Requisitos

- Python 3.11+
- Node.js 20+
- Cuenta en Supabase
- API key de Anthropic
- API key de Gamma (opcional)

## Instalación

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Agent-Admin

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con las credenciales reales

# 3. Instalar dependencias backend
cd backend
pip install -r requirements.txt

# 4. Instalar dependencias frontend
cd ../frontend
npm install

# 5. Ejecutar migraciones en Supabase
# Aplicar los archivos en backend/migrations/ en orden (001 → 007)
# desde el SQL editor de Supabase o con la CLI de Supabase
```

## Cómo correr

```bash
# Backend (desde backend/)
uvicorn main:app --reload

# Frontend (desde frontend/)
npm run dev

# Tests
pytest tests/test_critical_flows.py -v
```
