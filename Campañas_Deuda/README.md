# Campañas de Deuda

Sistema interno de gestión y recupero de deuda asistido por IA para la Municipalidad de Berazategui. Genera estrategias de campaña (informe Word + PDF) a partir de una cartera de deuda analizada por una cadena de cuatro agentes de IA.

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker y Docker Compose

## Instalación

```bash
git clone <repo>
cd campanas-deuda

# Backend
cp backend/.env.example backend/.env
# Editar backend/.env con las variables reales

cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Cómo correr

```bash
# Backend (desde backend/)
uvicorn main:app --reload

# Con Docker
docker-compose up --build

# Tests
cd backend
pytest tests/test_critical_flows.py -v

# Linting
ruff check . --fix && ruff format .
```

## Endpoints principales

| Método | Path | Descripción |
|---|---|---|
| GET | /health | Liveness check (público) |
| POST | /api/auth/register | Registro |
| POST | /api/auth/login | Login |
| POST | /api/portfolio/upload | Subir cartera |
| POST | /api/executions | Disparar análisis |
| GET | /api/executions/{id} | Estado de la corrida |
