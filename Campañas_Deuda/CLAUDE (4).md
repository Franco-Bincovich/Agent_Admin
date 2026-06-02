# CLAUDE.md — Campañas de Deuda

> Documento de contexto del proyecto. Claude Code lo lee al inicio de **cada** sesión.
> Se actualiza cada vez que cambia algo relevante (estado de fases, decisiones, deuda técnica).

---

## Antes de tocar nada — leer estos documentos

En la raíz del proyecto viven los cuatro documentos de la agencia. Son la constitución del
proyecto y tienen prioridad sobre cualquier suposición:

1. `BASES-DE-DESARROLLO.md` — las 10 bases universales + bases de manual y vibe coding
2. `ORDEN-Y-LEGIBILIDAD.md` — estructura de carpetas, naming, límites de líneas, errores, git
3. `SEGURIDAD-PENTEST.md` — secretos, auth, validación, RLS, seguridad con Anthropic
4. `UX-UI.md` — diseño de interfaces, estados, responsive, accesibilidad

Regla de arranque de toda sesión: *leer este CLAUDE.md y los cuatro documentos antes de escribir una línea.*

---

## Qué es este proyecto

Sistema **interno** de gestión y recuperación de deuda asistido por IA para la **Municipalidad
de Berazategui**. A partir de una cartera de deuda, corre una cadena de cuatro agentes que la
analizan desde distintas miradas y produce un **informe ejecutivo de estrategia** (Word + PDF)
que se envía por correo a los ejecutivos internos.

**Importante:** el sistema **genera la estrategia de la campaña, no ejecuta la cobranza.** No
contacta deudores, no manda intimaciones ni arma planes de pago operativos. Produce el análisis;
la dirección ejecuta por sus canales.

---

## Stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React + Next.js 14 (App Router) + Tailwind CSS + Shadcn/ui
- **DB**: Supabase (PostgreSQL) — ⚠️ ver "Estado de la base de datos" más abajo
- **IA**: Anthropic Claude (los agentes) + Perplexity API (contexto económico del Economista)
- **Entrega**: Gmail API (OAuth por usuario, tokens en DB)
- **Documentos**: generación Word + PDF
- **Deploy**: AWS (fuera de alcance por ahora — primero local)

---

## Contexto del dominio

**La cartera** se organiza en tres carteras, cada una segmentada por dureza y período:

| Cartera | Dureza | Período |
|---|---|---|
| Servicios Generales | Blanda · Intermedia · Dura | 2021 – 2026 |
| Servicio Sanitario (Agua) | Blanda · Intermedia · Dura | 2021 – 2026 |
| Automotor | Blanda · Intermedia · Dura | 2021 – 2026 |

- **Datos agregados siempre.** Los agentes nunca reciben registros individuales de deudores —
  trabajan sobre totales y segmentos (monto, cantidad de partidas, distribución capital/interés,
  evolución interanual).
- **Input por corrida**: la cartera se sube como archivo (CSV / XLSX / PDF) antes de cada corrida
  + un formulario con tres dimensiones (cartera, dureza, período), **selección única por dimensión**
  (cada dimensión admite un valor puntual o "todas").
- **Salida**: informe ejecutivo Word + PDF enviado por Gmail en **CC**, destinatarios elegidos al
  momento del envío desde una lista configurable.

---

## Los cuatro agentes (la cadena)

| # | Agente | Rol |
|---|---|---|
| 1 | Experto en Gestión de Deuda | Primera estrategia: escenario optimista y pesimista + riesgos |
| 2 | Director de Rentas | Critica y mejora la estrategia del agente 1 con criterio administrativo |
| 3 | Economista | Integra contexto macro y zonal (vía Perplexity) y reevalúa las estrategias |
| 4 | Ejecutivo | Sintetiza las tres miradas en una estrategia final consolidada |

**Loop de revisión:** una sola iteración. Tras la pasada inicial, cada agente revisa las tres
estrategias antes de que el Ejecutivo haga la síntesis. Sin loops abiertos (evita costo e inestabilidad).

**De dónde sale la información de la estrategia** (tres fuentes):
1. Datos agregados de la cartera cargada (Fuente principal — Agente 1)
2. Contexto económico externo en vivo vía Perplexity (Agente 3)
3. El criterio experto de cada rol, cargado en su system prompt

---

## Decisiones de arquitectura ya tomadas (no reabrir sin discutir)

- Control de acceso por roles (RBAC); rol admin asignable; primer admin por **script de seed** en DB
- Ejecución **asincrónica con polling**; corridas **programadas por cron** en `America/Argentina/Buenos_Aires`
- Gmail **OAuth por usuario**, tokens almacenados en DB (hasheados donde corresponda)
- Cartera subida como **archivo** antes de cada corrida (sin conexión en vivo a la base municipal)
- **Selección única** por dimensión en el formulario
- Destinatarios elegidos al **envío**, en modo **CC**
- El Economista usa **únicamente Perplexity** (BCRA e INDEC descartados por disponibilidad;
  posible capa opcional a futuro si se necesita trazabilidad oficial)
- **Degradación elegante** ante falla de API externa: health check previo a la corrida + aviso
  dentro del documento; **nunca** abortar la entrega del informe

---

## Estado de la base de datos (leer con atención)

🚫 **Por ahora NO se conecta a Supabase ni se ejecuta ninguna query real.**

- Las migraciones se escriben como **archivos SQL versionados** en `/migrations`, pero **no se aplican** todavía.
- El wrapper `integrations/supabase_client.py` se deja escrito, pero el sistema debe poder **levantar
  sin una conexión activa a la DB** en esta etapa (la capa de datos queda mockeable / inerte).
- No crear proyecto de Supabase, no cargar credenciales reales, no correr migraciones contra una DB.
- Cuando se habilite la DB, será una decisión explícita y una sesión aparte.

---

## Estructura de carpetas

```
proyecto/
├── CLAUDE.md
├── BASES-DE-DESARROLLO.md · ORDEN-Y-LEGIBILIDAD.md · SEGURIDAD-PENTEST.md · UX-UI.md
├── README.md · ARCHITECTURE.md · CHANGELOG.md · PLAN-DE-TRABAJO.md
├── docker-compose.yml
├── backend/
│   ├── main.py                      ← app, middlewares, registro de routers
│   ├── config/settings.py           ← única fuente de config y variables de entorno
│   ├── routers/                     ← endpoints, sin lógica de negocio (≤80 líneas)
│   ├── controllers/                 ← orquestación (≤100)
│   ├── services/                    ← lógica de negocio (≤150)
│   │   ├── agents/                  ← los 4 agentes + orquestador de la cadena
│   │   │   ├── debt_management_agent.py
│   │   │   ├── revenue_director_agent.py
│   │   │   ├── economist_agent.py
│   │   │   ├── executive_agent.py
│   │   │   └── chain_orchestrator.py
│   │   ├── document_service.py      ← generación Word / PDF
│   │   └── email_service.py         ← envío por Gmail
│   ├── repositories/                ← único acceso a la DB (≤100)
│   ├── integrations/                ← anthropic_client · perplexity_client · gmail_client · supabase_client
│   ├── schemas/                     ← Pydantic de entrada y salida
│   ├── middleware/                  ← auth · error_handler · security · rate limit
│   ├── utils/                       ← logger, helpers
│   ├── migrations/                  ← 001–008 SQL versionado (sin aplicar todavía)
│   └── tests/                       ← flujos críticos
└── frontend/
    ├── app/                         ← rutas App Router (page.tsx ≤80)
    ├── components/ui · components/features   ← componentes (≤150)
    ├── hooks/ (≤80) · services/ · store/ · types/ · utils/
    └── styles/design-system.ts      ← tokens de diseño del producto
```

---

## Convenciones de código (destiladas de los docs de la agencia)

- **Arquitectura por capas estricta**: router → controller → service → repository → DB.
  Sin lógica de negocio en routers; sin queries fuera de repositories; los services no conocen HTTP.
- **Errores**: siempre `AppError(message, code, status_code)`. Respuesta de error siempre el mismo
  formato `{ "error": true, "message": ..., "code": ... }`. Handler global único.
- **Config**: nunca `os.environ` fuera de `config/settings.py`. El resto importa `settings`.
- **Logs**: solo eventos de negocio importantes (Base 7), con el logger JSON centralizado.
  Nunca `print()` ni `console.log()`.
- **Límites de líneas**: router 80 · controller 100 · service 150 · repository 100 ·
  componente React 150 · hook 80 · cualquier otro 200. Si se supera, dividir.
- **Docstring completo** en funciones de services e integrations.
- **Seguridad Anthropic**: el system prompt SIEMPRE separado del input del usuario; sanitizar input.
- **Datos a los agentes**: siempre agregados, nunca registros individuales.
- **Validación en la frontera**: schema Pydantic en cada endpoint; TypeScript estricto (`any` prohibido).
- **Migraciones**: SQL numerado y versionado, RLS habilitado en tablas con datos de usuario,
  comentarios que explican el *por qué*.
- **Git**: commits convencionales (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).
  Una tarea = un commit coherente.

---

## Reglas para Claude Code

1. Leer este `CLAUDE.md` y los cuatro documentos de la agencia antes de empezar.
2. **Una sola tarea por sesión** (la del plan de trabajo). No adelantarse a sesiones futuras.
3. No modificar archivos fuera del scope de la tarea actual.
4. Si un archivo va a superar su límite de líneas, proponer cómo dividirlo **antes** de escribir.
5. Errores siempre con `AppError`; nunca devolver formatos de error distintos.
6. Nunca `os.environ` directo; todo vía `settings`.
7. Nunca `print()` ni `console.log()`; usar el logger.
8. Docstring en services e integrations; sin comentarios que repiten lo que dice el código.
9. Ante la duda entre dos enfoques, **preguntar antes de implementar**.
10. Antes de cada tarea, leer el archivo existente si lo hay — no sobreescribir sin entender.
11. **No conectar Supabase ni correr queries reales** en esta etapa (ver estado de la DB).
12. Al cerrar la sesión: revisar el diff, correr `ruff check . --fix && ruff format .` y los tests,
    commitear con formato convencional, y **actualizar el `CHANGELOG.md` y el estado de fases de este archivo**.

---

## Plan de trabajo por sesiones

Una tarea acotada por sesión (Base V3). Marcar el estado a medida que se avanza.

| # | Fase | Tarea | Estado |
|---|---|---|---|
| 1 | Fundación | Estructura de carpetas, `settings`, `.env.example`, `.gitignore`, `requirements.txt`, `AppError` + handler global, logger JSON, `main.py` con middlewares, Docker Compose, docs base | 🟡 |
| 2 | Fundación | Migraciones SQL 001–008 con RLS + script de seed del primer admin (archivos, **sin aplicar**) | ⬜ |
| 3 | Fundación | Auth: JWT access + refresh con rotación, middleware + `PUBLIC_ROUTES`, register/login/refresh/logout, rate limit en login + tests | ⬜ |
| 4 | Fundación | Gestión de usuarios con roles: CRUD, enforcement de admin, ownership + tests | ⬜ |
| 5 | Input | Carga de cartera: upload (CSV/XLSX/PDF), validación tipo/tamaño, repository, parser de agregados + tests | ⬜ |
| 6 | Input | Formulario de análisis: schema de 3 dimensiones, validación, registro de ejecución "pendiente" + tests | ⬜ |
| 7 | Input | Frontend base: Next.js, design system, cliente API, auth store, login con estados | ⬜ |
| 8 | Input | Frontend: formulario + carga de archivo con estados cargando/vacío/error | ⬜ |
| 9 | Agentes | Integración Perplexity: wrapper + manejo de errores + health check (con mock) | ⬜ |
| 10 | Agentes | Agente 1 — Gestión de Deuda: service + system prompt separado, escenarios | ⬜ |
| 11 | Agentes | Agente 2 — Director de Rentas: critica y mejora | ⬜ |
| 12 | Agentes | Agente 3 — Economista: integra Perplexity + estrategias previas | ⬜ |
| 13 | Agentes | Agente 4 — Ejecutivo: síntesis final | ⬜ |
| 14 | Agentes | Orquestador de la cadena + loop de revisión de una iteración | ⬜ |
| 15 | Agentes | Ejecución asincrónica + polling: disparo async, estados, endpoint de status | ⬜ |
| 16 | Agentes | Corridas programadas por cron (`scheduled_runs`) en timezone Buenos Aires | ⬜ |
| 17 | Documentos | Generación del informe en Word | ⬜ |
| 18 | Documentos | Generación del informe en PDF | ⬜ |
| 19 | Entrega | Gmail OAuth por usuario + almacenamiento de tokens + flujo de autorización | ⬜ |
| 20 | Entrega | Envío por Gmail en CC + selección de destinatarios + aviso de degradación | ⬜ |
| 21 | Logging | Wiring de `execution_logs` por corrida + endpoint de historial/estado | ⬜ |
| 22 | Testing/local | Tests de flujos críticos punta a punta + Docker corriendo todo + fixes | ⬜ |

> La franja 9–16 (agentes) es la más iterativa: afinar los prompts puede sumar sesiones extra.
> Fuera de alcance actual: AWS, WhatsApp, ejecución operativa de cobranza, BCRA/INDEC.

---

## Estado actual del proyecto

- **Implementado**: Sesión 1 — cáscara completa del backend (estructura, fundación y stubs).
- **En desarrollo**: Sesión 2 — Auth (JWT, refresh con rotación, tests).
- **Base de datos**: migraciones 001–008 escritas como archivos SQL en `backend/migrations/`; **sin aplicar y sin conexión a Supabase** por ahora.
- **Deuda técnica conocida**:
  - La riqueza de los datos agregados de la cartera está **sin definir** — faltan las columnas
    reales del archivo del municipio. Es el **riesgo principal** del proyecto: la calidad de la
    estrategia depende de qué tan completo sea el agregado que recibe el Agente 1.
- **Fuera de alcance actual**: AWS, WhatsApp Business API, ejecución de cobranza, integración BCRA/INDEC.

---

*Proyecto interno — Municipalidad de Berazategui · 2026*
*Desarrollado siguiendo las bases de desarrollo de la agencia v1.0*
