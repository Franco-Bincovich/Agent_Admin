# Changelog — Campañas de Deuda

## [0.2.0] — 2026-06-02 · Sesión 1B — Cáscara visual del frontend

### Implementado

- **Next.js 14 + App Router** con TypeScript estricto + Tailwind 3 + Sonner
- **`styles/design-system.ts`**: tokens del producto (paleta ejecutiva azul navy + dorado)
- **`tailwind.config.ts`**: integración de tokens en clases de Tailwind
- **UI base**: `Button` (variantes + loading + disabled + touch 44px), `Input` (label/error/helper),
  `EmptyState`, `ErrorState`, `Skeleton`, `ConfirmDialog`, `Badge`
- **Layout**: `Sidebar` (desktop + hamburger mobile), `PageLayout`, `UserMenu`
- **Mock auth**: `authStore` con Zustand — login simula latencia, "error@test.com" dispara error
- **`lib/mockData.ts`**: datos realistas de Berazategui para todas las pantallas
- **Pantalla 1 — Login**: estados normal / cargando / error, accesibilidad completa
- **Pantalla 2 — Inicio**: 4 StatCards + 3 corridas recientes con link a detalle
- **Pantalla 3 — Nueva campaña**: FileUpload (drag&drop + 5 estados) + 3 DimensionSelectors
  (selección única por radio), validación antes de habilitar el submit
- **Pantalla 4 — Ejecuciones**: lista con los 4 estados (loading/empty/error/data),
  variable `MOCK_STATE` para previsualizar cada estado
- **Pantalla 5 — Detalle de ejecución**: timeline, downloads Word/PDF (disabled si no listo),
  destinatarios CC, botón envío por email
- **Pantalla 6 — Configuración**: placeholder para sesiones futuras
- `npm run build` pasa · ESLint ✓ · Prettier ✓

### Próxima sesión

- **Sesión 2**: Auth completo (JWT, refresh con rotación, middleware, tests)

---

## [0.1.0] — 2026-06-02 · Sesión 1 — Cáscara y fundación

### Implementado (funciona en esta versión)

- **Estructura completa del backend** siguiendo arquitectura por capas:
  `router → controller → service → repository → integration`
- **`config/settings.py`**: única fuente de configuración vía `pydantic-settings`.
  Ningún otro módulo toca `os.environ`.
- **`utils/errors.py`**: clase `AppError(message, code, status_code)`.
- **`utils/logger.py`**: logger JSON centralizado. Sin `print()` en todo el proyecto.
- **`middleware/error_handler.py`**: handler global con formato de error estándar
  `{ "error", "message", "code" }`.
- **`middleware/security.py`**: `SecurityHeadersMiddleware` y `PayloadLimitMiddleware`.
- **`middleware/auth.py`**: stub de autenticación (implementación real en Sesión 3).
- **`main.py`**: FastAPI app con security headers, CORS whitelist, payload limit,
  error handler global y `GET /health` que responde `{"status": "ok"}`.
- **`requirements.txt`** con versiones exactas.
- **`.env.example`** completo con todas las variables.
- **`.gitignore`** con `.env` bloqueado.
- **`docker-compose.yml`** base.
- **`README.md`**, **`ARCHITECTURE.md`**, **`CHANGELOG.md`**.

### Stubs (firmas + docstrings, devuelven 501 NOT_IMPLEMENTED)

- Routers: `auth`, `users`, `portfolio`, `executions`
- Controllers: `auth`, `user`, `portfolio`, `execution`
- Services: `auth`, `user`, `portfolio`, `execution`
- Agents: `debt_management`, `revenue_director`, `economist`, `executive`, `chain_orchestrator`
- Repositories: `user_repo`, `portfolio_repo`, `execution_repo`
- Integrations: `anthropic_client`, `perplexity_client`, `gmail_client`, `supabase_client`
- Schemas: `auth`, `user`, `portfolio`, `execution`

### Migraciones SQL (archivos creados, sin aplicar)

- `001_create_users.sql` — tabla de usuarios con RLS
- `002_create_refresh_tokens.sql` — refresh tokens hasheados con RLS
- `003_create_gmail_tokens.sql` — tokens OAuth Gmail por usuario con RLS
- `004_create_portfolio_files.sql` — archivos de cartera con agregados y RLS
- `005_create_executions.sql` — corridas de análisis con estados y RLS
- `006_create_execution_logs.sql` — trazabilidad por corrida con RLS
- `007_create_scheduled_runs.sql` — corridas programadas por cron con RLS
- `008_seed_admin.sql` — seed del primer usuario administrador

### Verificado

- `uvicorn main:app` levanta sin DB ni claves reales configuradas
- `GET /health` responde `{"status": "ok"}`
- `ruff check . --fix && ruff format .` pasa sin errores
- `test_health_check` pasa

### Siguiente sesión

- **Sesión 2**: Auth completo (JWT, refresh con rotación, middleware, tests)
