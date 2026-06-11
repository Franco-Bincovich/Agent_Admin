# Agent-Admin

## Qué es

Agent-Admin es una plataforma interna de productividad con IA pensada para equipos que producen material ejecutivo a partir de documentación dispersa: informes, pliegos, planillas, minutas. El problema que resuelve es el tiempo que se pierde convirtiendo esa documentación en entregables presentables — armar una presentación para un directorio, consolidar varios informes en un documento Word coherente, o pasar un cronograma de Microsoft Project a un Gantt navegable que todo el equipo pueda consultar y actualizar.

El uso diario es simple: el usuario entra a la plataforma, sube sus archivos fuente (PDF, Word, Excel, texto plano o cronogramas de MS Project), configura algunos parámetros (template, tono, audiencia, estructura) y la plataforma genera el entregable usando Claude (Anthropic) como motor de IA. Todo lo generado queda en un historial por usuario, con descarga directa desde Supabase Storage. Es multiusuario, con tres roles (administrador, editor, viewer) y autenticación propia con JWT + refresh tokens en cookies httpOnly.

La plataforma tiene cuatro módulos en uso: **Presentaciones** (PPTX descargable + presentación en Gamma), **Documentos** (Word generado por secciones), **Plantillas de documentos** (estructuras reutilizables para el módulo de Documentos) y **Planificación** (importación de cronogramas de licitación con vistas Gantt, planilla, portfolio y vista unificada multi-proyecto). Existe además un módulo de Video en etapa temprana (endpoints y pantalla creados, pipeline en desarrollo).

---

## Módulos

### Presentaciones

El usuario sube entre 1 y 10 archivos fuente, escribe el **objetivo** de la presentación (qué quiere comunicar y a quién) y configura los parámetros de diseño. El sistema extrae el texto y las imágenes de los archivos, arma un prompt maestro, le pide a Claude un outline estructurado en JSON y con ese outline genera el entregable.

**Formatos de entrada:** PDF, DOCX, TXT, XLSX (también acepta PPTX como fuente).

**Parámetros configurables:**

| Parámetro | Opciones | Default |
|---|---|---|
| Template (PPTX) | `ejecutivo_oscuro` · `profesional_claro` · `corporativo_neutro` | `ejecutivo_oscuro` |
| Tono | formal · institucional · comercial · técnico | formal |
| Audiencia | directivos · equipo interno · clientes · técnicos | directivos |
| Output | PPTX · Gamma · ambos | ambos |
| Usar imágenes del documento | sí / no (solo para output PPTX) | no |
| Logo | imagen opcional (solo para output PPTX) | — |
| Tema visual (Gamma) | minimalist · playful · organic · modular · elegant · digital · geometric | minimalist |
| Estilo de imágenes (Gamma) | IA generadas · pictográfico · Pexels · sin imágenes (entre otros) | IA generadas |
| Paleta de colores (Gamma) | descripción libre | — |
| Cantidad de slides (Gamma) | 5 a 20 | 10 |
| Título | texto libre opcional | se genera automáticamente |

**Qué genera:**
- Un **PPTX descargable** construido con python-pptx sobre uno de los tres templates (guardado en Supabase Storage).
- Una **presentación en Gamma**: link a la presentación online (`gamma_url`) más un PPTX exportado desde Gamma (`pptx_gamma_url`). Gamma es opcional — si no hay API key, el pipeline PPTX funciona igual.

La generación es asíncrona: el formulario responde al instante y la pantalla muestra el progreso hasta que la presentación está lista (ver [patrón asíncrono](#arquitectura--decisiones-relevantes)).

**Casos de uso típicos:** presentación de resultados para un directorio a partir de un informe PDF, resumen comercial de una propuesta para enviar a un cliente, deck interno de avance de proyecto a partir de minutas y planillas.

### Documentos

El usuario sube hasta 10 archivos fuente (50 MB máximo cada uno), define un **título**, elige una **estructura de secciones** (predefinida, desde una plantilla guardada, o armada a mano con drag & drop) y opcionalmente agrega indicaciones. Claude redacta cada sección consolidando el contenido de todas las fuentes, y el sistema arma un Word con formato profesional.

**Formatos de entrada:** PDF, DOCX, XLSX.

**Opciones de procesamiento:**
- **Homogeneizar tono y estilo** — unifica la redacción aunque las fuentes tengan estilos distintos.
- **Eliminar información duplicada** — deduplica contenido repetido entre fuentes.
- **Incluir imágenes de los documentos** — incorpora imágenes extraídas de las fuentes.

También admite un **logo** para la portada y una **plantilla DOCX** de referencia.

**Qué genera:** un **DOCX descargable** (Supabase Storage), con el outline guardado en base de datos para poder reintentarlo.

**Casos de uso típicos:** consolidar varios informes técnicos en un único documento ejecutivo, redactar el resumen de un expediente a partir de sus anexos, convertir planillas y notas sueltas en un informe con introducción, análisis y conclusiones.

### Plantillas de Documentos

Las plantillas son **estructuras de secciones reutilizables** para el módulo de Documentos: una lista ordenada de secciones (cada una con nombre y descripción opcional) que se guarda con un nombre propio. Por ejemplo, "Informe mensual" = Resumen ejecutivo → Contexto → Desarrollo → Conclusiones → Próximos pasos.

En la pantalla de Plantillas el usuario puede crear, editar, eliminar y reordenar secciones con drag & drop, combinando secciones predefinidas (Resumen ejecutivo, Introducción, Contexto, Objetivos, Desarrollo, Conclusiones, Recomendaciones) con secciones personalizadas. Una plantilla puede marcarse como **predeterminada** (una por usuario).

En el flujo de generación de documentos, el formulario ofrece un selector de plantillas: al elegir una, la estructura de secciones se precarga y el usuario puede ajustarla antes de generar. Esto evita rearmar la misma estructura cada vez que se genera un tipo de documento recurrente.

### Planificación

Módulo para importar **cronogramas de proyectos de licitación** hechos en Microsoft Project, normalizarlos y trabajarlos visualmente. El usuario crea un proyecto con un wizard de 4 pasos (datos del proyecto → carga del archivo → detección automática de áreas → confirmación), y el sistema parsea el cronograma respetando la jerarquía WBS: el nivel 1 es el proyecto, el **nivel 2 define las áreas** (cada una con color propio), y los niveles siguientes son las tareas.

**Formatos de entrada:**
- **`.mpp`** (archivo nativo de MS Project) — se parsea con MPXJ vía JPype; requiere Java en el servidor (ver nota de JAVA_HOME más abajo). Si Java no está disponible, el sistema responde con un mensaje claro sugiriendo exportar a XML.
- **`.xml`** (formato MSPDI, "Guardar como XML" desde MS Project) — se parsea con la librería estándar de Python, sin dependencias externas. Es la vía más portable.
- **Excel/CSV y PDF** figuran en el roadmap pero **no están implementados todavía** — hoy el backend rechaza cualquier extensión que no sea `.mpp` o `.xml`.

Cada proyecto tiene nombre, expediente (opcional) y prioridad (alta/media/baja). Cada área tiene color, responsable (nombre, teléfono, mail — datos de contacto en texto, no usuarios del sistema) y disponibilidad (horas × empleados). Cada tarea conserva su WBS, nivel, fechas reales de inicio/fin, y un flag de confianza para fechas estimadas. La identidad de una tarea es **proyecto + WBS**, lo que permite reimportar un cronograma actualizado sin perder el marcado de tareas completadas.

**Las cinco vistas:**

| Vista | Qué muestra | Cuándo usarla |
|---|---|---|
| **Revisión** | Tabla completa de tareas importadas (WBS, nombre, fechas, área, confianza) más las áreas detectadas, todas editables. Alerta si hay fechas estimadas. | Inmediatamente después de importar: verificar que el parseo fue correcto, completar responsables y disponibilidad de cada área, reasignar tareas a otra área si hace falta. |
| **Gantt** | Diagrama de Gantt jerárquico y colapsable de un proyecto, con barras coloreadas por área, indicador del día de hoy y zoom anual o cuatrimestral. | Seguimiento operativo de un proyecto: ver qué tareas vienen, qué área está cargada, y marcar avances directamente sobre la barra. |
| **Planilla** | Tabla estilo Project: WBS, nombre indentado por nivel, inicio, fin y duración en días. Las tareas completas aparecen tachadas. | Cuando se necesita el detalle exacto de fechas y duraciones, o para marcar tareas rápido en formato lista. |
| **Portfolio** | Una fila por proyecto: barra de duración con color propio más una barra de progreso (porcentaje de tareas hoja completadas). Zoom anual/cuatrimestral. | Vista gerencial: estado de todos los proyectos de la cartera de un vistazo, comparando plazos y avances. |
| **Unificado** | Gantt multi-proyecto desglosado por área: cada proyecto se abre en bloques de área expandibles, y cada área en sus tareas. | Coordinar carga entre proyectos: ver qué áreas tienen trabajo simultáneo en varios proyectos en el mismo período. |

**Funcionalidades:**
- **Marcar tareas como completadas** (clic en la barra del Gantt o en la fila de la Planilla) — queda registrado quién y cuándo la marcó; las tareas completas se atenúan en gris.
- **Editar áreas**: responsable, contacto, disponibilidad, color; crear áreas nuevas y reasignar tareas entre áreas.
- **Navegar por cuatrimestres** en Gantt, Portfolio y Unificado, con zoom anual para la foto completa.
- **Reimportar** un cronograma actualizado sin perder el estado de las tareas ya marcadas (upsert por proyecto + WBS).

**Casos de uso típicos:** seguimiento de obra o licitación con cronograma de Project sin que todo el equipo necesite licencia de MS Project, reporte semanal de avance marcando tareas completadas, vista de cartera para dirección con todos los proyectos activos y sus plazos.

---

## Stack técnico

### Backend

| Tecnología | Versión | Para qué se usa |
|---|---|---|
| Python | 3.11 | Runtime del backend |
| FastAPI | 0.115.0 | Framework HTTP (API REST) |
| Uvicorn | 0.30.6 | Servidor ASGI |
| Pydantic | 2.9.2 | Validación de schemas de entrada/salida |
| anthropic | 0.52.0 | SDK de Claude — modelo `claude-sonnet-4-6` (configurable vía `ANTHROPIC_MODEL`) |
| supabase | 2.7.4 | Cliente de PostgreSQL + Storage + Auth |
| python-pptx | 1.0.2 | Generación de archivos PPTX |
| python-docx | 1.1.2 | Generación de archivos DOCX |
| PyMuPDF | 1.24.10 | Extracción de texto/imágenes de PDF, rasterización de páginas DOCX, conversión EMF |
| mammoth | 1.8.0 | Extracción de texto de DOCX |
| openpyxl | 3.1.5 | Extracción de datos de XLSX |
| mpxj | 13.12.0 | Parseo de archivos `.mpp` de MS Project (librería Java, JARs bundleados) |
| JPype1 | 1.5.1 | Puente Python ↔ JVM para ejecutar MPXJ en proceso |
| python-jose | 3.3.0 | Firma y verificación de JWT |
| bcrypt | 4.1.3 | Hashing de contraseñas |
| slowapi | 0.1.9 | Rate limiting (in-memory, por worker) |

### Frontend

| Tecnología | Versión | Para qué se usa |
|---|---|---|
| Next.js | 16.2.4 | Framework React con App Router |
| React | 19.2.4 | UI |
| TypeScript | 5.9.3 | Tipado estricto (`any` prohibido por convención) |
| Tailwind CSS | 4.2.4 | Estilos |
| Shadcn/ui | 4.7.0 | Componentes base (Button, Dialog, Select, etc.) |
| Zustand | 5.0.13 | Estado global (auth) |
| @dnd-kit | 6.x | Drag & drop (reordenar secciones de plantillas) |
| lucide-react | 1.14.0 | Iconografía |
| sonner | 2.0.7 | Toasts/notificaciones |
| next-themes | 0.4.6 | Tema claro/oscuro |

### Servicios externos

| Servicio | Para qué se usa |
|---|---|
| Supabase | PostgreSQL (datos), Storage (PPTX/DOCX/cronogramas generados), RLS |
| Anthropic API | Generación de outlines, redacción de secciones, lectura visual de documentos (Claude Vision) |
| Gamma API | Publicación de presentaciones online + export PPTX desde Gamma (opcional) |
| Vercel | Hosting del frontend y del backend (serverless) |

---

## Estructura del proyecto

```
Agent-Admin/
├── backend/
│   ├── main.py                  ← entrada FastAPI: routers, CORS, reaper de jobs colgados
│   ├── vercel.json              ← deploy serverless en Vercel (@vercel/python)
│   ├── render.yaml              ← deploy alternativo en Render (proceso persistente, no activo)
│   ├── Dockerfile               ← imagen alternativa (uvicorn, 4 workers, no activa)
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   └── settings.py          ← única fuente de variables de entorno (pydantic-settings)
│   ├── routers/                 ← capa HTTP: auth, users, profile, activity,
│   │                               generations, documentos, document_templates,
│   │                               planificacion, video
│   ├── controllers/             ← validación de permisos + orquestación request/response
│   ├── services/                ← lógica de negocio (~27 servicios):
│   │   │                           generation_service, documento_service (pipelines),
│   │   │                           extraction_service (texto por tipo de archivo),
│   │   │                           image_extraction_service (imágenes + EMF + rasterizado),
│   │   │                           ai_service (prompt + Claude + parsing JSON robusto),
│   │   │                           pptx_service, docx_service, gamma_service,
│   │   │                           planificacion_service, planificacion_mpp_adapter (JPype+MPXJ),
│   │   │                           planificacion_xml_adapter (MSPDI)
│   ├── repositories/            ← acceso a datos (única capa que toca la DB)
│   ├── integrations/            ← clientes externos: anthropic_client (AsyncAnthropic,
│   │                               timeout 60s), gamma_client, supabase_client (service key)
│   ├── schemas/                 ← modelos Pydantic por módulo
│   ├── middleware/              ← auth (JWT desde cookies) + error_handler (AppError)
│   ├── templates/               ← templates PPTX: ejecutivo_oscuro, profesional_claro,
│   │                               corporativo_neutro (uno por archivo)
│   ├── migrations/              ← 17 SQL numerados (001 → 017), aplicados a mano en Supabase
│   ├── utils/                   ← logger centralizado + AppError
│   └── tests/
│       └── test_critical_flows.py
│
└── frontend/
    ├── app/
    │   ├── (auth)/login/        ← login
    │   └── (dashboard)/         ← layout autenticado con navegación
    │       ├── dashboard/       ← métricas y actividad reciente
    │       ├── generator/       ← formulario de presentaciones
    │       ├── documentos/      ← formulario de documentos Word
    │       ├── plantillas/      ← CRUD de plantillas de documentos
    │       ├── planificacion/   ← listado de proyectos + detalle con las 5 vistas
    │       │   └── [proyecto_id]/
    │       ├── history/         ← historial de generaciones y documentos
    │       ├── users/           ← gestión de usuarios (solo administrador)
    │       ├── profile/         ← perfil y cambio de contraseña
    │       └── video/           ← módulo de video (en desarrollo)
    ├── components/
    │   ├── ui/                  ← componentes Shadcn
    │   ├── layout/              ← shell, navegación
    │   └── features/            ← componentes por módulo:
    │                               generator/ (GeneratorForm, GammaConfigFields, ProgressTracker…)
    │                               documentos/ (DocumentoForm, EstructuraSection, OpcionesSection…)
    │                               plantillas/ (PlantillasClient, PlantillaForm…)
    │                               planificacion/ (NuevoProyectoModal, ProyectoRevisionView,
    │                                               GanttView, PlanillaView, PortfolioView,
    │                                               UnificadoView…)
    ├── hooks/                   ← useAuth, useGenerations, usePlanificacion, usePortfolioData…
    ├── services/                ← clientes HTTP por módulo (api.ts + uno por recurso)
    ├── store/                   ← Zustand (authStore)
    ├── types/                   ← contratos TypeScript compartidos
    └── utils/                   ← formatters, ganttUtils
```

**Arquitectura por capas (estricta):** router → controller → service → repository. Sin lógica de negocio en routers ni en componentes React; sin queries fuera de repositories. Errores siempre como `AppError(message, code, status_code)`; logging centralizado solo de eventos de negocio.

---

## Requisitos

- **Python 3.11+**
- **Node.js 20+** (Next.js 16 / React 19)
- **Java JDK 11+** — opcional, solo necesario para importar archivos `.mpp` en Planificación (los `.xml` no lo requieren)
- Cuenta de **Supabase** (PostgreSQL + Storage)
- API key de **Anthropic**
- API key de **Gamma** — opcional (el pipeline PPTX funciona sin Gamma)
- Cuenta de **Vercel** para el deploy

---

## Variables de entorno

### Backend (`backend/.env` — ver `backend/.env.example`)

| Variable | Descripción | Obligatoria |
|---|---|---|
| `APP_ENV` | Entorno de ejecución (`development` / `production`) | Sí |
| `ANTHROPIC_API_KEY` | API key de Anthropic (`sk-ant-...`) | Sí |
| `ANTHROPIC_MODEL` | Modelo de Claude a usar (default: `claude-sonnet-4-6`) | No |
| `GAMMA_API_KEY` | API key de Gamma; sin ella el output Gamma no está disponible pero el PPTX sí | No |
| `SUPABASE_URL` | URL del proyecto Supabase | Sí |
| `SUPABASE_SERVICE_KEY` | Service key de Supabase (acceso administrativo — **bypasea RLS**, nunca exponerla al cliente) | Sí |
| `SUPABASE_ANON_KEY` | Anon key de Supabase | Sí |
| `JWT_SECRET` | Secreto de firma de JWT (mínimo 32 caracteres) | Sí |
| `JWT_EXPIRATION_MINUTES` | Vida del access token en minutos (default: 60) | No |
| `REFRESH_TOKEN_EXPIRATION_DAYS` | Vida del refresh token en días (default: 30) | No |
| `ALLOWED_ORIGINS` | Orígenes permitidos para CORS (ej.: `http://localhost:3000`) | Sí |

### Frontend (`frontend/.env.local` — ver `frontend/.env.example`)

| Variable | Descripción | Obligatoria |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL del backend (local: `http://localhost:8000`) | Sí |
| `NEXT_PUBLIC_SUPABASE_URL` | URL del proyecto Supabase | No (según features) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon key de Supabase | No (según features) |

---

## Instalación y desarrollo

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd Agent-Admin

# 2. Variables de entorno
cp backend/.env.example backend/.env       # completar con credenciales reales
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local

# 3. Dependencias
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Base de datos
# Ejecutar los SQL de backend/migrations/ EN ORDEN (001 → 017)
# desde el SQL editor de Supabase. Crear además los buckets de Storage.
```

```bash
# Backend — http://localhost:8000 (docs interactivas en /docs)
cd backend
uvicorn main:app --reload

# Frontend — http://localhost:3000
cd frontend
npm run dev

# Tests
cd backend
pytest tests/test_critical_flows.py -v
```

> **Nota — JAVA_HOME en Windows (módulo Planificación):** para importar archivos `.mpp`, JPype necesita encontrar la JVM. En Windows eso requiere tener un JDK instalado (por ejemplo [Eclipse Temurin](https://adoptium.net/)) y la variable de entorno `JAVA_HOME` apuntando a su carpeta raíz (ej.: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x`), de modo que JPype localice `jvm.dll` vía `jpype.getDefaultJVMPath()`. Reiniciar la terminal después de setearla. Si Java no está disponible, el endpoint responde 422 con un mensaje que sugiere exportar el cronograma como `.xml` desde MS Project — esa vía funciona sin Java.

---

## Deploy en Vercel

El frontend y el backend se deployan como **dos proyectos de Vercel separados** sobre el mismo repo:

1. **Backend** — proyecto Vercel con *root directory* `backend/`. El `backend/vercel.json` ya configura el runtime Python (`@vercel/python`) y rutea todo el tráfico a `main.py` (app ASGI). Cargar en el dashboard de Vercel todas las variables de entorno del backend (tabla de arriba), con `APP_ENV=production` y `ALLOWED_ORIGINS` apuntando al dominio del frontend.
2. **Frontend** — proyecto Vercel con *root directory* `frontend/` (Next.js se autodetecta). Configurar `NEXT_PUBLIC_API_URL` con la URL del backend deployado.
3. **Supabase** — aplicar las migraciones 001 → 017 en el SQL editor del proyecto de producción y crear los buckets de Storage.

> **Limitaciones conocidas de serverless:**
> - Las generaciones corren como `BackgroundTasks` de FastAPI **dentro de la función serverless**: si una generación larga supera la duración máxima de la función, el proceso se corta a mitad de pipeline. El reaper (corre cada 10 min) marca como `error` los jobs que llevan más de 30 min en `procesando`, así que el frontend no queda esperando para siempre — pero la generación se pierde y hay que reintentarla. Para cargas pesadas sostenidas, la alternativa de proceso persistente (`render.yaml` / `Dockerfile`, hoy no activa) no tiene este límite.
> - El parseo de **`.mpp` requiere una JVM**, que no existe en el runtime Python de Vercel. En producción serverless, los `.mpp` fallan con un mensaje que indica exportar a `.xml` — formato que sí funciona en cualquier entorno.
> - El **rate limiting es in-memory** (slowapi): cada instancia serverless (o cada worker de uvicorn) cuenta por separado, así que el límite efectivo se multiplica. Es una limitación aceptada para uso interno; con más escala correspondería un backend de rate limiting compartido (Redis).

---

## Arquitectura — decisiones relevantes

**Patrón asíncrono subir → procesar → polling.** Todas las generaciones (presentaciones, documentos, cronogramas) siguen el mismo patrón: el POST crea el registro con `estado='procesando'` y responde **202 al instante**; el procesamiento corre en un `BackgroundTask` en el mismo proceso (sin Celery/Redis/workers externos); el frontend hace polling al `GET /{id}` hasta que el estado pasa a `listo` o `error`. Un *reaper* en `main.py` corre cada 10 minutos y marca como `error` cualquier job que lleve más de 30 minutos procesando. Complementos: timeout de 60 s en el cliente de Anthropic con retry y backoff (3 intentos), payload máximo 50 MB, rate limit de 20 req/min en los endpoints de generación (10/min en Planificación).

**Migraciones SQL versionadas (001 → 017), aplicadas a mano.** No hay Alembic ni Flyway: cada cambio de esquema es un archivo SQL numerado en `backend/migrations/` que se ejecuta manualmente en el SQL editor de Supabase, en orden. Es deliberadamente simple para un equipo chico con una sola base: el historial completo del esquema queda versionado en el repo y revisable en PRs, a cambio de disciplina manual (no saltearse números, no editar migraciones ya aplicadas). La próxima migración continúa la numeración.

**Vercel serverless para el backend.** Se eligió Vercel para tener frontend y backend en la misma plataforma con deploy automático por push y costo cero de infraestructura — adecuado para un producto interno con tráfico esporádico. Las limitaciones (duración máxima de función para generaciones largas, sin JVM para `.mpp`, rate limiting in-memory por instancia) están detalladas en la sección de Deploy. El repo conserva `render.yaml` y `Dockerfile` como configuración alternativa de proceso persistente, lista para activar si el patrón de uso lo exige.

**MPXJ + JPype para leer archivos `.mpp`.** El formato nativo de MS Project es binario y propietario; la única librería madura que lo lee es MPXJ, que es Java. En lugar de montar un microservicio Java aparte, el backend usa **JPype** para levantar una JVM dentro del propio proceso Python, cargando los JARs que el paquete pip `mpxj` trae bundleados, y parsea con `UniversalProjectReader`. El trabajo Java es bloqueante, así que corre en un thread (`asyncio.to_thread`) para no frenar el event loop; la JVM se arranca una sola vez por proceso. Si no hay Java instalado, el error es controlado (422) y orienta al usuario a la alternativa: exportar el cronograma como `.xml` (MSPDI), que se parsea con `xml.etree.ElementTree` de la stdlib sin ninguna dependencia.

**Imágenes de contenido vs. decorativas en el pipeline PPTX.** Al generar presentaciones con `usar_imagenes_documento`, el sistema distingue dos tipos de imagen con roles distintos frente a Claude:
- *Imágenes de contenido*: páginas completas de los DOCX **rasterizadas a PNG (150 DPI) con PyMuPDF**. Existen porque los DOCX de origen suelen traer tablas y gráficos como EMF embebidos que la extracción de texto no captura; la página rasterizada se envía a Claude Vision como **fuente de información para redactar el outline**, no para insertarse en slides.
- *Imágenes decorativas*: las imágenes embebidas (EMF/WMF/PNG de `word/media/`, imágenes de PDF y XLSX) se extraen, se convierten a PNG con una cadena de fallbacks (PyMuPDF nativo → SVG → PIL), se deduplican por hash y se filtran por tamaño mínimo (5 KB), con tope de 20. Se envían a Claude como **índice visual**: el outline devuelve un `imagen_idx` por slide y `pptx_service` inserta la imagen correspondiente.

La heurística que decide cuánto pesa cada vía es la densidad de texto del documento: si un DOCX tiene menos de ~100 caracteres de texto por página, se asume "EMF-heavy" (el contenido real está en las imágenes) y se priorizan ambas extracciones combinadas.

---

## Estado actual

**En producción:** Presentaciones, Documentos, Plantillas de documentos, Autenticación con refresh tokens. Backend en Vercel serverless.

**En desarrollo:** Planificación (funcional: importación MPP/XML, 5 vistas, marcado de tareas; pendiente: importación Excel/CSV y PDF) · módulo de Video.

**Deuda técnica conocida:** fragmentación de wrappers de Claude (`ai_service`, `anthropic_service`, `documento_claude_client`) · rate limiting in-memory multiplicado por workers/instancias · ver `ARCHITECTURE.md`.
