# CLAUDE.md — Agent Admin

## Qué es este proyecto

Agent Admin es una plataforma interna de productividad con IA. Tiene tres módulos en producción:

1. **Presentaciones** — genera PPTX descargable + link Gamma a partir de archivos fuente (PDF, DOCX, TXT, XLSX) y parámetros de diseño.
2. **Documentos** — genera documentos Word (DOCX) a partir de archivos fuente y plantillas.
3. **Plantillas de documentos** — gestión de plantillas reutilizables (en desarrollo).

Y un módulo nuevo en construcción:

4. **Planificación** — importa cronogramas de proyectos de licitación (Excel/CSV de Microsoft Project, `.mpp`, y PDF como caso opcional), los normaliza, los muestra como visuales tipo Gantt y permite marcar tareas como completas.

Es un producto de uso interno, multiusuario, con historial y control de accesos.

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + FastAPI 0.115.0 |
| Frontend | Next.js 16.2.4 + React 19.2.4 + Tailwind CSS + Shadcn/ui + Zustand 5 |
| Base de datos | Supabase (PostgreSQL + Storage + Auth) |
| Motor de IA | Anthropic API — Claude Sonnet (anthropic 0.34.2) |
| Generación PPTX | python-pptx |
| Generación DOCX | python-docx |
| Integración Gamma | Gamma API |
| Extracción archivos | openpyxl (XLSX), PyMuPDF (PDF), mammoth (DOCX), lectura directa (TXT) |
| Hosting | Vercel (frontend **y** backend serverless) + Supabase (db/storage) |

> **Nota de deploy:** el backend hoy corre en Vercel serverless y funciona (Generaciones y Documentos
> operan con el patrón async descrito abajo). Existen además `render.yaml` y `Dockerfile` en el repo
> como configuración alternativa de proceso persistente, no activa.

---

## Arquitectura por capas

Estricta: **router → controller → service → repository**. Integraciones externas en `integrations/`.
Cada módulo es paralelo e independiente; solo comparten la FK a `usuarios`.

### Backend (`backend/`)

```
routers/        auth · users · profile · activity · generations · documentos · document_templates · video
controllers/    auth · user · token · profile · activity · generation · documento · document_template · video
services/       (~27) ai · anthropic · auth · token · user · generation* · documento* · docx* · pptx* ·
                document_template · gamma · image_extraction · prompt_builder
repositories/   user · user_mutations · generation · documento · documento_mutations · document_template ·
                token · video · video_brand_config
integrations/   anthropic_client · gamma_client · supabase_client
schemas/        auth · user · generation · documento · document_template · video
middleware/     auth · error_handler
migrations/     16 archivos SQL numerados (001–016), aplicados manualmente en Supabase SQL editor
```

### Frontend (`frontend/`)

```
Next.js 16 App Router · Tailwind · Shadcn (components/ui/) · Zustand
```

> **⚠ A VERIFICAR antes de trabajar el frontend:** el diagnóstico encontró `app/` con poco más que
> `layout.tsx` y `page.tsx`, y `features/` casi vacío (solo `documentos/OpcionesSection.tsx`), pese a
> que las rutas del backend existen. La UI real puede estar en otro directorio (`src/`?) o la
> exploración fue parcial. **Confirmar la ubicación real de las páginas antes de asumir que hay que
> construir UI desde cero.**

---

## Convenciones de código

- Arquitectura por capas estricta: router → controller → service → repository. Sin lógica de negocio en routers ni en componentes React. Sin queries a la DB fuera de repositories.
- Errores: siempre `AppError(message, code, status_code)` — nunca excepciones genéricas.
- Logs: solo eventos de negocio. Sin `print()` — usar el logger centralizado de `utils/logger.py`.
- Límites de líneas: services 150, routers 100, repositories 100, componentes React 150.
- Docstring obligatorio en funciones de `services/` e `integrations/`.
- TypeScript estricto en el frontend — `any` prohibido.

---

## Patrón asíncrono (subir → procesar → polling)

Patrón establecido y en producción, usado por Generaciones y Documentos. **Planificación lo reutiliza.**

```
1. POST multipart/form-data → router (archivos: list[UploadFile])
2. controller crea registro en BD con estado='procesando' → retorna 202 inmediato
3. background_tasks.add_task(run_*)  → procesamiento en segundo plano
4. run_*: extrae → procesa → guarda en Storage → repo.update(estado='listo' | 'error')
5. Frontend hace polling a GET /<recurso>/{id} hasta estado != 'procesando'
```

- Reaper en `main.py`: marca como `error` los jobs en `procesando` por más de 30 min (corre cada 10 min vía `asyncio`).
- Timeouts: cliente Anthropic 60s · payload máximo 50 MB · rate limit 20 req/min en endpoints de generación.
- No hay Celery/RQ/Redis/workers externos: todo es en-process con `asyncio` + `BackgroundTasks`.

---

## Integración con Anthropic

- `integrations/anthropic_client.py` — singleton `AsyncAnthropic`, timeout 60s.
- `services/ai_service.py` — outlines JSON, retry con backoff (3 intentos: 5/10/20s), multimodal (imágenes base64), detección de prompt injection, parsing JSON robusto. **Solo generación de texto — no usa `tool_use` ni `code_execution` hoy.**
- Hay fragmentación: existen además `anthropic_service.py` y `documento_claude_client.py`. **Deuda conocida:** al sumar el adaptador PDF de Planificación, decidir cuál reutilizar en vez de crear un cuarto wrapper.

---

## Supabase — DB, Auth y Storage

- Conexión: singleton con `service_key` (acceso administrativo, **bypasea RLS**).
- Migraciones: 16 SQL numerados (001–016), aplicados **manualmente** en el SQL editor de Supabase. Sin Alembic/Flyway.
- Buckets: `pptx-generados` ({generation_id}.pptx) · `docx-generados` ({documento_id}.docx). Planificación usará un bucket nuevo `cronogramas`.

### Roles (`usuarios.rol`)

```
CHECK (rol IN ('administrador', 'editor', 'viewer', 'usuario'))
```

| Rol | Capacidades |
|---|---|
| `administrador` | Todo: gestión de usuarios, historial global, métricas |
| `editor` | Generar, ver su historial, descargar |
| `viewer` | Ver historial asignado, descargar, abrir links Gamma |

> No existe rol "líder de área" y **no se agrega**. En Planificación, el responsable de un área es un
> **dato de contacto en texto** (nombre, teléfono, mail), no un usuario. El marcado de tareas en V1 queda
> abierto a los usuarios autenticados (admin/editor); el control fino por área se difiere.

---

## Módulo Planificación (en construcción)

Módulo nuevo y paralelo. No toca Plantillas ni ningún módulo existente.

```
backend/routers/planificacion.py
backend/controllers/planificacion_controller.py
backend/services/planificacion_service.py        ← orquesta importación + normalización
backend/services/planificacion_storage.py        ← bucket 'cronogramas'
backend/repositories/planificacion_repo.py
backend/schemas/planificacion.py
backend/migrations/017_create_planificacion.sql
```

### Modelo (resumen funcional)

- **Proyecto** — nombre, prioridad, duración, archivo de origen, **estado** (`procesando`/`listo`/`error`, igual que Generaciones).
- **Área** — pertenece a un proyecto; nombre, color (derivado del capítulo WBS nivel 2), responsable/teléfono/mail (texto), disponibilidad (horas × empleados).
- **Tarea** — pertenece a proyecto y área; WBS, nombre, nivel, si es resumen, **inicio/fin como fecha real**; cuando el origen no trae fechas (PDF de barras) se guarda **fecha estimada + nivel de confianza**; estado pendiente/completada + fecha y autor del marcado. **Identidad estable: proyecto + WBS** (preserva el marcado al reimportar).

### Formatos de entrada (prioridad)

1. **Excel/CSV de Project** — primario, confiable (openpyxl ya disponible).
2. **`.mpp` nativo** — vía MPXJ. Requiere Java; se resuelve con el code execution tool de la API (el sandbox ya trae JVM), no en infra propia.
3. **PDF** — opcional/"si llegamos". Claude visión → estructura + niveles de confianza. Siempre con pantalla de revisión editable.

### Visuales

Cuatro vistas sobre el mismo dato: **Gantt** (jerárquico colapsable, color por área), **Planilla** (tabla WBS), **Portfolio** (proyectos por color de proyecto), **Unificado** (proyectos desglosados por área). Tareas completas se muestran en gris.

---

## Variables de entorno requeridas (.env)

```
APP_ENV=development
ANTHROPIC_API_KEY=sk-ant-...
GAMMA_API_KEY=...                 # opcional (pipeline PPTX funciona sin Gamma)
SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
JWT_SECRET=min-32-chars
JWT_EXPIRATION_MINUTES=60
REFRESH_TOKEN_EXPIRATION_DAYS=30
ALLOWED_ORIGINS=http://localhost:3000
```

---

## Levantar en local

```
# Terminal 1 — backend
cd backend
pip install -r requirements.txt          # crear backend/.env desde .env.example
uvicorn main:app --reload                 # http://localhost:8000

# Terminal 2 — frontend
cd frontend
npm install                               # crear frontend/.env.local con NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                               # http://localhost:3000
```

Migraciones: aplicar los SQL en orden en el SQL editor de Supabase.

---

## Reglas para Claude

- No modificar archivos fuera del scope de la tarea pedida. En particular, **no tocar el módulo de Plantillas** (`document_templates`/`document_template_*`).
- Si un archivo va a superar su límite de líneas, proponer cómo dividirlo antes de escribir.
- Docstring completo en funciones de `services/` e `integrations/`.
- Reutilizar el patrón asíncrono de Generaciones para Planificación — no inventar uno nuevo.
- Las migraciones son manuales y numeradas: la próxima de Planificación es la **017**.
- Ante dos enfoques posibles, preguntar antes de implementar.

---

## Estado actual del proyecto

**En producción:** Presentaciones (Claude → PPTX), Documentos (DOCX), Auth con refresh tokens. Backend en Vercel serverless.

**En desarrollo:** Plantillas de documentos · **Planificación (este documento, módulo nuevo)**.

**Deuda técnica conocida:** `CLAUDE.md` venía desactualizado (corregido en esta versión) · fragmentación de wrappers de Claude (3 clientes) · rate limiting in-memory (×4 workers) · ubicación real de la UI del frontend a verificar.