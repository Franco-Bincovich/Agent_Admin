# CLAUDE.md — Agent Admin

## Qué es este proyecto

Agent Admin es una plataforma interna de productividad con IA que permite a equipos
generar presentaciones ejecutivas (PPTX descargable + link Gamma) a partir de archivos
fuente (PDF, DOCX, TXT, XLSX) y parámetros de diseño definidos por el usuario.
Es un producto de uso interno, multiusuario, con historial y control de accesos.

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Frontend | Next.js 14 (App Router) + Tailwind CSS + Shadcn/ui |
| Base de datos | Supabase (PostgreSQL + Storage + Auth) |
| Motor de IA | Anthropic API — Claude Sonnet (claude-sonnet-4-6) |
| Generación PPTX | python-pptx |
| Integración Gamma | Gamma API |
| Extracción archivos | PyMuPDF (PDF), mammoth (DOCX), openpyxl (XLSX), lectura directa (TXT) |
| Hosting | Vercel (frontend) + Supabase (backend/db/storage) |

---

## Estructura de carpetas

```
agent-admin/
├── backend/
│   ├── main.py                        ← punto de entrada FastAPI
│   ├── config/
│   │   └── settings.py                ← única fuente de variables de entorno
│   ├── routers/
│   │   ├── auth.py
│   │   ├── generations.py
│   │   └── users.py
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── generation_controller.py
│   │   └── user_controller.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── generation_service.py      ← orquesta el pipeline completo
│   │   ├── extraction_service.py      ← extrae texto de archivos
│   │   ├── ai_service.py              ← construye prompt + llama a Claude
│   │   ├── pptx_service.py            ← genera el .pptx con python-pptx
│   │   └── gamma_service.py           ← publica en Gamma y retorna link
│   ├── repositories/
│   │   ├── user_repo.py
│   │   └── generation_repo.py
│   ├── integrations/
│   │   ├── anthropic_client.py
│   │   ├── gamma_client.py
│   │   └── supabase_client.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── generation.py
│   │   └── user.py
│   ├── middleware/
│   │   ├── auth.py
│   │   └── error_handler.py
│   ├── templates/
│   │   ├── ejecutivo_oscuro.py        ← definición del template (colores, fonts, layouts)
│   │   ├── profesional_claro.py
│   │   └── corporativo_neutro.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── errors.py
│   ├── migrations/                    ← SQL versionado (se completa en siguiente fase)
│   ├── tests/
│   │   └── test_critical_flows.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── app/
    │   ├── (auth)/
    │   │   ├── login/page.tsx
    │   │   └── register/page.tsx
    │   ├── dashboard/page.tsx
    │   ├── generator/page.tsx
    │   ├── history/page.tsx
    │   ├── users/page.tsx
    │   └── layout.tsx
    ├── components/
    │   ├── ui/                        ← Button, Input, Modal, etc (Shadcn)
    │   └── features/
    │       ├── generator/
    │       │   ├── GeneratorForm.tsx
    │       │   └── ProgressTracker.tsx
    │       ├── history/
    │       │   └── HistoryTable.tsx
    │       └── users/
    │           └── UserTable.tsx
    ├── hooks/
    │   ├── useGenerations.ts
    │   └── useAuth.ts
    ├── services/
    │   ├── api.ts
    │   ├── generationService.ts
    │   └── authService.ts
    ├── store/
    │   └── authStore.ts
    ├── types/
    │   └── index.ts
    └── utils/
        └── formatters.ts
```

---

## Convenciones de código

- Seguir arquitectura por capas estricta: router → controller → service → repository
- Errores: siempre `AppError(message, code, status_code)` — nunca levantar excepciones genéricas
- Logs: solo eventos de negocio (registro, generación iniciada, error en pipeline, pago)
- Máximo 150 líneas en services, 100 en routers, 100 en repositories
- Docstring obligatorio en todas las funciones de services e integrations
- Sin `print()` — usar el logger centralizado de `utils/logger.py`
- TypeScript estricto en el frontend — `any` prohibido
- Sin lógica de negocio en routers ni en componentes React

---

## Flujo principal del sistema

```
Usuario completa formulario (archivos + parámetros)
  → extraction_service: extrae texto de cada archivo por tipo
  → ai_service: construye prompt maestro + llama a Claude → outline JSON
  → pptx_service: convierte outline en .pptx usando el template seleccionado
  → gamma_service: publica el outline en Gamma → retorna URL
  → generation_repo: guarda metadatos, pptx_url, gamma_url, estado
  → Frontend recibe resultado: descarga PPTX + link Gamma
```

---

## Templates PPTX disponibles (v1.0)

Tres templates de texto puro (sin imágenes por ahora). Cada uno define:
colores de fondo y texto, tipografía, y layouts por tipo de slide.

| Template | Fondo | Acento | Uso típico |
|---|---|---|---|
| `ejecutivo_oscuro` | Azul marino (#0F1B2D) | Celeste (#4FC3F7) | Presentaciones a directivos |
| `profesional_claro` | Blanco (#FFFFFF) | Azul (#1E40AF) | Documentación interna, reportes |
| `corporativo_neutro` | Gris antracita (#1E1E2E) | Violeta (#7C3AED) | Propuestas comerciales |

Layouts por tipo de slide (todos los templates los implementan):
- `portada` — título grande + subtítulo
- `contenido` — título + bullets (máx 5 ítems)
- `destacado` — título + texto central en caja
- `cierre` — mensaje de cierre + línea inferior

---

## Roles de usuario

| Rol | Capacidades |
|---|---|
| `administrador` | Todo: gestión de usuarios, historial global, métricas |
| `editor` | Generar slides, ver su propio historial, descargar |
| `viewer` | Ver historial asignado, descargar, abrir links Gamma |

---

## Variables de entorno requeridas (.env)

```
APP_ENV=development

ANTHROPIC_API_KEY=sk-ant-...
GAMMA_API_KEY=...

SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...

JWT_SECRET=min-32-chars
JWT_EXPIRATION_MINUTES=60
REFRESH_TOKEN_EXPIRATION_DAYS=30

ALLOWED_ORIGINS=http://localhost:3000
```

---

## Reglas para Claude

- No modificar archivos fuera del scope de la tarea pedida
- Si un archivo va a superar su límite de líneas, proponer cómo dividirlo antes de escribir
- Docstring completo en todas las funciones de `services/` e `integrations/`
- Los templates PPTX viven en `backend/templates/` — uno por archivo, nunca inline en el service
- El pipeline de generación es orquestado únicamente desde `generation_service.py`
- Ante dos enfoques posibles, preguntar antes de implementar
- Las migraciones SQL se trabajarán en una fase posterior — no crearlas aún

---

## Estado actual del proyecto

**Implementado:**
- Módulo de presentaciones (pipeline Claude → PPTX): funcional
- Módulo de documentos Word (docx_template, extraction_service): funcional
- Autenticación con refresh tokens vía cookies httpOnly: funcional
- Tests críticos: 12/12

**Pendiente:**
- Deploy en Vercel + Supabase producción (en curso)
- Migraciones SQL versionadas (fase siguiente)
- Templates PPTX v2 con imágenes (roadmap)

**Deuda técnica:** ver ARCHITECTURE.md
