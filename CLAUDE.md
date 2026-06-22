# CLAUDE.md — Agent Admin

## Qué es este proyecto

Agent Admin es una plataforma interna de productividad con IA. Tiene tres módulos en producción:

1. **Presentaciones** — genera PPTX descargable + link Gamma a partir de archivos fuente (PDF, DOCX, TXT, XLSX) y parámetros de diseño.
2. **Documentos** — genera documentos Word (DOCX) a partir de archivos fuente y plantillas.
3. **Plantillas de documentos** — gestión de plantillas reutilizables (en desarrollo).

Y un módulo nuevo en construcción:

4. **Planificación** — importa cronogramas de proyectos de licitación, los normaliza, los muestra como visuales tipo Gantt y permite marcar avance de tareas (0/25/50/75/100) y reprogramar.

Es un producto de uso interno **para una sola empresa**: todos los usuarios autenticados **ven todo** (lectura compartida, sin importar quién subió el recurso); lo que se restringe por rol es **qué puede modificar cada quién**. Incluye historial/auditoría visible solo para admin y control de accesos por rol.

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
routers/        auth · users · profile · activity · generations · documentos · document_templates · video · planificacion
controllers/    auth · user · token · profile · activity · generation · documento · document_template · video · planificacion
services/       (~27) ai · anthropic · auth · token · user · generation* · documento* · docx* · pptx* ·
                document_template · gamma · image_extraction · prompt_builder ·
                planificacion · planificacion_tarea · planificacion_mpp_adapter · planificacion_xml_adapter · planificacion_storage
repositories/   user · user_mutations · generation · documento · documento_mutations · document_template ·
                token · video · video_brand_config · planificacion · planificacion_area · planificacion_tarea
integrations/   anthropic_client · gamma_client · supabase_client
schemas/        auth · user · generation · documento · document_template · video · planificacion
middleware/     auth · error_handler
migrations/     19 archivos SQL numerados (001–019), aplicados manualmente en Supabase SQL editor
```

### Frontend (`frontend/`)

```
Next.js 16 App Router · Tailwind · Shadcn (components/ui/) · Zustand
```

> **⚠ A VERIFICAR antes de trabajar el frontend:** el diagnóstico encontró `app/` con poco más que
> `layout.tsx` y `page.tsx`, y `features/` casi vacío, pese a que las rutas del backend existen.
> La UI real puede estar en otro directorio. **Confirmar la ubicación real de las páginas antes de
> asumir que hay que construir UI desde cero.** (El módulo Planificación sí tiene UI en
> `components/features/planificacion/`.)

---

## Convenciones de código

- Arquitectura por capas estricta: router → controller → service → repository. Sin lógica de negocio en routers ni en componentes React. Sin queries a la DB fuera de repositories.
- Errores: siempre `AppError(message, code, status_code)` — nunca excepciones genéricas.
- Logs: solo eventos de negocio. Sin `print()` — usar el logger centralizado de `utils/logger.py`.
- Límites de líneas: **routers 80 · controllers 100 · services 150 · repositories 100 · componentes React 150 · hooks 80**.
- Docstring obligatorio en funciones de `services/` e `integrations/`.
- TypeScript estricto en el frontend — `any` prohibido.

---

## Modelo de accesos y roles

> **Plataforma de una sola empresa.** No hay clientes externos ni multiempresa. Todos los usuarios
> pertenecen a la misma organización. La **lectura es abierta** para todos los autenticados (cualquiera
> ve todos los proyectos, áreas y tareas, sin importar quién los subió). Lo único que se restringe por
> rol es la **escritura**.

### Roles (`usuarios.rol`)

```
CHECK (rol IN ('administrador', 'gerente', 'lider'))   -- a partir de la migración 020
```

| Rol | Sube proyectos | Modifica tareas (avance/completar/reprogramar) | Administración (usuarios, roles, asignación de áreas) | Ve historial/auditoría |
|---|---|---|---|---|
| `administrador` | Sí | Cualquier tarea | Sí | Sí |
| `gerente` | Sí | Solo tareas de **sus** áreas asignadas | No | No |
| `lider` | No | Solo tareas de las áreas **de su gerente** | No | No |

- **Cómo se resuelve el permiso de escritura sobre una tarea:** admin → siempre; gerente → si el
  área de la tarea le pertenece; líder → si el área de la tarea pertenece a su gerente.
- **El gerente es "dueño" de un área.** El vínculo gerente→área lo asigna **únicamente un admin**, por
  proyecto, después de importar (no es automático, no hay tabla maestra de nombres por ahora). Es lo que
  habilita a los líderes de ese gerente a operar sobre esas tareas.
- **El líder no se asigna a un área directamente.** Hereda las áreas de su gerente vía la jerarquía
  líder→gerente. Un gerente puede tener varios líderes.
- **Lectura siempre abierta.** Ningún rol restringe ver. Restringir lectura no es un objetivo.

### Jerarquía y propiedad

- **`usuarios.manager_id`** (FK a `usuarios`, nullable) — vínculo líder→gerente.
- **Dueño de área** en `planificacion_areas` (FK a `usuarios`, nullable) — el gerente responsable.
  Reemplaza, a efectos de permisos, al viejo "responsable en texto". El contacto en texto
  (nombre/teléfono/mail) queda como dato informativo / a jubilar — decisión a cerrar en la sesión de
  modelo de datos.

### Dónde vive cada cosa (rendimiento y frescura)

- **El rol viaja en el JWT** (claim `role`). Es barato para el gate admin/gerente. Costo: un cambio de
  rol en DB no surte efecto hasta el próximo refresh/re-login.
- **La jerarquía (manager_id) y la propiedad de áreas se consultan en la DB en cada request de
  escritura — NUNCA se cachean en el token.** Esto da revocación inmediata y no agrega costo real
  (resolver el permiso de un líder ya obliga a pegarle a la DB).

### Reglas de gestión de usuarios

- **Registro público cerrado.** No hay alta self-service. Los usuarios los crea **solo un admin** vía el
  endpoint admin-only de `/users`.
- Existe (a construir) un endpoint admin-only para **cambiar el rol** de un usuario y para **asignar
  líderes a un gerente** y **áreas a un gerente**.

### ⚠ Naming rol vs role

La DB usa `rol` (español); el JWT usa `role` (inglés). Todos los consumidores leen
`current_user.get("role")` (del token), armado desde `user["rol"]` (de la DB). **Cualquier código nuevo
que lea `current_user["rol"]` rompe con KeyError.** Seguir la convención: `role` en el token.

### Historial / auditoría (admin-only)

Sección de historial visible **solo para admin** que trackea todo cambio en Planificación: **quién, cuándo,
qué acción, sobre qué recurso, valor antes→después**. Se implementa como un audit log (tabla propia +
punto único de escritura en cada mutación). Es una pieza posterior al modelo de permisos.

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

- Reaper en `main.py`: marca como `error` los jobs colgados en `procesando` (corre cada 10 min vía `asyncio`).
- Timeouts: cliente Anthropic 60s · rate limit en endpoints de generación.
- No hay Celery/RQ/Redis/workers externos: todo es en-process con `asyncio` + `BackgroundTasks`.

---

## Integración con Anthropic

- `integrations/anthropic_client.py` — singleton `AsyncAnthropic`, timeout 60s.
- `services/ai_service.py` — outlines JSON, retry con backoff (3 intentos: 5/10/20s), multimodal (imágenes base64), detección de prompt injection, parsing JSON robusto. **Solo generación de texto — no usa `tool_use` ni `code_execution` hoy.**
- Hay fragmentación: existen además `anthropic_service.py` y `documento_claude_client.py`. **Deuda conocida:** consolidar wrappers.

---

## Supabase — DB, Auth y Storage

- Conexión: singleton con `service_key` (acceso administrativo, **bypasea RLS**).
  > **Implicancia de seguridad:** las policies RLS (incluidas las de admin "ve todo") son **inertes** porque
  > el service_key las saltea. **Toda la autorización vive en la capa app (controllers/services), no en RLS.**
  > No confiar en policies para el control de acceso.
- Migraciones: 19 SQL numerados (001–019), aplicados **manualmente** en el SQL editor de Supabase. Sin Alembic/Flyway. **La próxima es la 020.**
- Buckets: `pptx-generados` ({generation_id}.pptx) · `docx-generados` ({documento_id}.docx) · `cronogramas` (Planificación).

---

## Módulo Planificación (en construcción)

Módulo nuevo y paralelo. No toca Plantillas ni ningún módulo existente.

```
backend/routers/planificacion.py
backend/controllers/planificacion_controller.py
backend/services/planificacion_service.py            ← orquesta importación + normalización
backend/services/planificacion_tarea_service.py      ← progreso, completar, reprogramar
backend/services/planificacion_mpp_adapter.py        ← parser .mpp (JPype + MPXJ)
backend/services/planificacion_xml_adapter.py        ← parser XML MSPDI (stdlib, sin Java)
backend/services/planificacion_storage.py            ← bucket 'cronogramas'
backend/repositories/planificacion_repo.py
backend/repositories/planificacion_area_repo.py
backend/repositories/planificacion_tarea_repo.py
backend/schemas/planificacion.py
backend/migrations/017_create_planificacion.sql
backend/migrations/019_add_progreso_reprogramacion_tareas.sql
frontend/components/features/planificacion/*         ← UI (4 vistas + revisión)
```

### Modelo (resumen funcional)

- **Proyecto** — nombre, prioridad, duración, archivo de origen, **estado** (`procesando`/`listo`/`error`, igual que Generaciones).
- **Área** — pertenece a un proyecto; nombre, color (derivado del capítulo WBS nivel 2), disponibilidad.
  **Dueño = gerente (FK usuario), asignado por admin** (gobierna permisos de líderes). Contacto en texto
  (nombre/teléfono/mail) = dato informativo / a jubilar.
- **Tarea** — pertenece a proyecto y área; WBS, nombre, nivel, si es resumen, inicio/fin como fecha real.
  **Progreso 0/25/50/75/100** (`completada` se deriva de progreso==100; `completada_por`/`completada_en`
  para auditoría). Reprogramación preserva el plan base (`fecha_*_original`) y marca `reprogramada`.
  **Identidad estable: proyecto + WBS** (preserva el avance al reimportar vía UPSERT).
- **Acceso:** lectura abierta a todos; escritura de tareas según el modelo de roles de arriba.

> **Quién puede tocar el progreso lo resuelve el rol + propiedad de área**, no un "usuario asignado por
> tarea" (ese mecanismo se descartó por redundante; quién tocó efectivamente lo registra la auditoría).

### Paleta de áreas

Fuente de verdad en backend (`planificacion_service.AREA_COLORS`): azul, violeta, cyan, naranja, rosa,
índigo, teal, púrpura. **Sin verde/amarillo/rojo** (reservados para el semáforo del borde de tarea; el
ámbar `#B45309` indica tarea reprogramada). **Deuda conocida:** el frontend duplica un `AREA_COLORS`
distinto en varios archivos que sí incluye verde/ámbar/rojo — unificar contra el backend.

### Visuales

Cuatro vistas sobre el mismo dato: **Gantt** (jerárquico colapsable, color por área), **Planilla** (tabla WBS), **Portfolio** (proyectos por color de proyecto), **Unificado** (proyectos desglosados por área). Tareas completas en gris.

> **⚠ Drift de formatos a corregir (pendiente, no tocar sin sesión propia):** el `CLAUDE.md` venía
> describiendo "Excel/CSV de Project como formato primario" y ".mpp vía code execution tool de la API".
> La implementación real es: el origen `'excel'` es en realidad **XML MSPDI** (stdlib, sin Java); el `.mpp`
> se procesa **in-process con JPype/MPXJ** (no via code execution tool — y por eso cae en 422 en Vercel
> serverless, que no trae JVM); el **PDF no está implementado**. Confirmar y reescribir esta sección en su
> propia pasada antes de tocar el pipeline de importación.

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

> **MPXJ / .mpp:** requiere JVM. `JAVA_HOME` debe estar seteado en la sesión (en Windows/PowerShell,
> por sesión). En Vercel serverless no hay JVM → el `.mpp` degrada a 422; el camino operativo es XML.

---

## Reglas para Claude

- No modificar archivos fuera del scope de la tarea pedida. En particular, **no tocar el módulo de Plantillas** (`document_templates`/`document_template_*`).
- Si un archivo va a superar su límite de líneas, proponer cómo dividirlo antes de escribir.
- Docstring completo en funciones de `services/` e `integrations/`.
- Reutilizar el patrón asíncrono de Generaciones para Planificación — no inventar uno nuevo.
- Las migraciones son manuales y numeradas: **la próxima es la 020.**
- **Toda autorización vive en la capa app, no en RLS** (el service_key saltea RLS).
- **Modelo de accesos vigente (ver sección "Modelo de accesos y roles"):** lectura abierta a todos;
  escritura por rol (admin todo · gerente sus áreas · líder áreas de su gerente). **No revertir esto a
  ownership puro (`usuario_id == sub`)** — ese era el modelo viejo y está siendo reemplazado. La
  decisión previa de "no existe rol líder de área" quedó **superada** por este modelo.
- Ante dos enfoques posibles, preguntar antes de implementar.

---

## Estado actual del proyecto

**En producción:** Presentaciones (Claude → PPTX), Documentos (DOCX), Auth con refresh tokens. Backend en Vercel serverless.

**En desarrollo:** Plantillas de documentos · **Planificación**.

**Migración de modelo de accesos (en curso):** la plataforma pasa de cuentas aisladas (cada usuario veía
solo lo suyo) a **una sola empresa con lectura compartida + escritura por roles (admin/gerente/líder)**.
Secuencia: (1) lectura compartida en Planificación · (2) migración 020 (CHECK de rol + jubilar legacy +
cerrar registro) · (3) jerarquía `manager_id` + dueño de área · (4) endpoints de cambio de rol y asignación ·
(5) matriz de permisos de escritura que reemplaza `usuario_id == sub` · (6) audit log / historial admin.

**Deuda técnica conocida:** drift de formatos de Planificación (Excel/CSV/.mpp/PDF vs. realidad — ver
sección del módulo) · fragmentación de wrappers de Claude (3 clientes) · rate limiting in-memory ·
`AREA_COLORS` duplicado en frontend · roles legacy (`editor`/`viewer`/`usuario`) a migrar en la 020 ·
ubicación real de la UI del frontend a verificar · sin tests en Planificación.