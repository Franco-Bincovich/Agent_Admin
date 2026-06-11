# PLAN-DE-TRABAJO.md — Campañas de Deuda

> Guía de construcción del proyecto, dividida en sesiones de trabajo de Claude Code.
> Cada sesión = **una sola tarea acotada** (Base V3) que arranca y cierra limpia.
> Se actualiza el estado a medida que se avanza. El detalle de contexto vive en `CLAUDE.md`.

---

## Cómo se trabaja

- **Una tarea por sesión.** No se adelantan tareas de sesiones futuras ni se mezclan dos cosas.
- **Cada sesión cierra con un commit coherente** y el estado actualizado.
- **Se respetan las bases de la agencia** en todo momento (los cuatro documentos de la raíz).
- **Por ahora no se conecta Supabase ni se corren queries reales** — las migraciones se escriben
  como archivos pero no se aplican (ver `CLAUDE.md`).

---

## Preparación previa (la hacés vos, no Claude Code)

1. Crear el repo en GitHub (vacío, sin README).
2. Clonarlo a la máquina de trabajo.
3. Poner en la **raíz** de la carpeta:
   - Los cuatro documentos de la agencia: `BASES-DE-DESARROLLO.md`, `ORDEN-Y-LEGIBILIDAD.md`,
     `SEGURIDAD-PENTEST.md`, `UX-UI.md`
   - `CLAUDE.md` y este `PLAN-DE-TRABAJO.md`
4. Abrir Claude Code desde adentro de la carpeta: `claude`
5. El `.env` se completa recién cuando una sesión lo necesite. La cáscara no requiere claves reales
   y la DB no se conecta todavía.

---

## Ritual fijo de cada sesión

**Apertura**
- Prompt inicial: *"Leé el `CLAUDE.md` y los cuatro documentos de la agencia antes de tocar nada."*
- Confirmar cuál es la tarea de la sesión — y que es la única.

**Durante**
- Una sola tarea (V3). No tocar archivos fuera del scope (regla 3 / M5).
- Respetar los límites de líneas. Si un archivo va a superarlos, proponer cómo dividirlo **antes** de escribir.
- Errores con `AppError`; config vía `settings`; logger centralizado; docstrings en services e integrations.
- No conectar Supabase ni ejecutar queries reales.

**Cierre**
- Revisar `git diff --staged` (M4): sin secrets, sin `print()`/`console.log()`, sin archivos fuera de
  scope, `.env` no incluido.
- Correr `ruff check . --fix && ruff format .` y los tests de la sesión.
- Commit con formato convencional (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).
- Actualizar `CHANGELOG.md` y el estado de fases en `CLAUDE.md`.

---

## Las fases

| Fase | Sesiones | Qué deja lista |
|---|---|---|
| Fundación | 1 – 4 | Estructura, config, auth y usuarios |
| Input | 5 – 8 | Carga de cartera, formulario, frontend base |
| Agentes | 9 – 16 | La cadena de 4 agentes, loop, ejecución async y programada |
| Documentos | 17 – 18 | Generación Word y PDF |
| Entrega | 19 – 20 | Gmail OAuth y envío |
| Logging | 21 | Trazabilidad por corrida |
| Testing / local | 22 | Tests críticos + Docker punta a punta |

> La franja de agentes (9–16) es la más iterativa: afinar los prompts puede sumar sesiones extra.

---

## Sesiones en detalle

### Fase — Fundación

**Sesión 1 · Cáscara y fundación**
- *Tarea:* estructura de carpetas (capas backend + frontend), `config/settings.py`, `.env.example`,
  `.gitignore`, `requirements.txt` con versiones exactas, `AppError` + handler global, logger JSON,
  `main.py` con middlewares (security headers, CORS whitelist, límite de payload), `docker-compose.yml`,
  `README.md` / `ARCHITECTURE.md` / `CHANGELOG.md` base.
- *Hecho cuando:* el backend levanta con `uvicorn`, `/health` responde, `ruff` pasa limpio.

**Sesión 2 · Migraciones (archivos, sin aplicar)**
- *Tarea:* las 8 migraciones SQL 001–008 (`users`, `refresh_tokens`, `gmail_tokens`, `portfolio_files`,
  `executions`, `execution_logs`, `scheduled_runs`, seed admin), con RLS habilitado y comentarios del *por qué*.
- *Hecho cuando:* los archivos existen, numerados y comentados. **No se aplican** a ninguna DB.

**Sesión 3 · Autenticación**
- *Tarea:* JWT access + refresh con rotación, hash bcrypt del refresh, middleware de auth + `PUBLIC_ROUTES`,
  endpoints register / login / refresh / logout, rate limiting en login.
- *Hecho cuando:* pasan los tests de registro, login, login fallido y endpoint protegido sin token.

**Sesión 4 · Usuarios y roles**
- *Tarea:* CRUD de usuarios, enforcement del rol admin, verificación de ownership.
- *Hecho cuando:* un no-admin no puede gestionar usuarios y un usuario no accede a recursos de otro (tests).

### Fase — Input

**Sesión 5 · Carga de cartera**
- *Tarea:* endpoint de upload (CSV/XLSX/PDF), validación de tipo y tamaño, repository, parser que extrae
  los **agregados** del segmento.
- *Hecho cuando:* se sube un archivo de prueba y el parser devuelve los totales agregados esperados (tests).
- ⚠️ *Depende de:* tener definidas las columnas reales del archivo de cartera (ver riesgos).

**Sesión 6 · Formulario de análisis**
- *Tarea:* schema de las tres dimensiones (cartera, dureza, período) con selección única, validación,
  creación del registro de ejecución en estado "pendiente".
- *Hecho cuando:* una combinación válida crea una ejecución; una inválida devuelve 422 (tests).

**Sesión 7 · Frontend base**
- *Tarea:* Next.js, `styles/design-system.ts`, cliente API con interceptors, auth store, página de login
  con sus estados (cargando / error).
- *Hecho cuando:* el login funciona contra el backend y maneja el token.

**Sesión 8 · Frontend del input**
- *Tarea:* página del formulario + carga de archivo, con estados cargando / vacío / error según `UX-UI.md`.
- *Hecho cuando:* se sube la cartera y se dispara una ejecución desde la interfaz.

### Fase — Agentes

**Sesión 9 · Integración Perplexity**
- *Tarea:* `perplexity_client.py` (wrapper), manejo de errores y health check, con mock para tests.
- *Hecho cuando:* el wrapper responde con datos mockeados y el health check detecta caída.

**Sesión 10 · Agente 1 — Gestión de Deuda**
- *Tarea:* service + system prompt separado del input; recibe agregados, devuelve escenario optimista y
  pesimista con riesgos.
- *Hecho cuando:* dado un segmento agregado de prueba, produce una estrategia con ambos escenarios.

**Sesión 11 · Agente 2 — Director de Rentas**
- *Tarea:* critica y mejora la estrategia del Agente 1 con criterio administrativo.

**Sesión 12 · Agente 3 — Economista**
- *Tarea:* integra el contexto de Perplexity + las estrategias previas y reevalúa.

**Sesión 13 · Agente 4 — Ejecutivo**
- *Tarea:* síntesis final consolidada de las tres miradas.

**Sesión 14 · Orquestador + loop**
- *Tarea:* `chain_orchestrator.py`: corre la cadena en orden + el loop de revisión de **una** iteración.
- *Hecho cuando:* una corrida completa produce una estrategia final consolidada (con agentes mockeables).

**Sesión 15 · Ejecución asincrónica + polling**
- *Tarea:* disparo async, manejo de estados (pendiente / corriendo / listo / error), endpoint de status.
- *Hecho cuando:* se dispara una corrida y el endpoint de status refleja el avance.

**Sesión 16 · Corridas programadas**
- *Tarea:* `scheduled_runs` con expresiones cron en `America/Argentina/Buenos_Aires`.
- *Hecho cuando:* una corrida programada se dispara en el horario correcto.

### Fase — Documentos

**Sesión 17 · Word**
- *Tarea:* generación del informe ejecutivo en `.docx`.

**Sesión 18 · PDF**
- *Tarea:* generación del informe en `.pdf`.

### Fase — Entrega

**Sesión 19 · Gmail OAuth**
- *Tarea:* flujo OAuth por usuario + almacenamiento de tokens en DB.

**Sesión 20 · Envío**
- *Tarea:* envío por Gmail en CC con selección de destinatarios + aviso de degradación ante falla de API.
- *Hecho cuando:* el informe llega a los destinatarios elegidos; ante falla de API el envío sale con la salvedad.

### Fase — Logging

**Sesión 21 · Trazabilidad**
- *Tarea:* wiring de `execution_logs` por corrida + endpoint de historial / estado de ejecuciones.
- *Hecho cuando:* cada corrida deja su rastro consultable (qué pasó, cuándo, en qué ejecución).

### Fase — Testing / local

**Sesión 22 · Cierre del core**
- *Tarea:* tests de flujos críticos punta a punta + Docker corriendo todo junto + fixes de integración.
- *Hecho cuando:* los tests críticos pasan y el sistema corre completo en local.

---

## Riesgos y notas de alcance

- **Riesgo principal — datos de la cartera:** la calidad de la estrategia depende enteramente de qué
  tan completo sea el agregado que recibe el Agente 1. Hay que **definir las columnas reales** del
  archivo de cartera antes (o durante) la Sesión 5. Cuanto más rico el agregado (distribución por
  antigüedad, recupero histórico, intentos previos, estacionalidad), mejor la estrategia.
- **Agentes (9–16):** afinar los prompts es iterativo; sumar sesiones de ajuste sin culpa.
- **Fuera de alcance actual:** AWS, WhatsApp Business API, **ejecución operativa de cobranza**
  (el sistema genera estrategia, no ejecuta campañas), integración BCRA/INDEC.

---

## Leyenda de estado

`⬜ pendiente` · `🟡 en curso` · `✅ hecha`

El estado vivo de cada sesión se lleva en la tabla del `CLAUDE.md`.

---

*Proyecto interno — Municipalidad de Berazategui · 2026*
*Plan de trabajo siguiendo las bases de desarrollo de la agencia v1.0*
