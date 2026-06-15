# Changelog — Agent Admin

## [1.1.0] — 2026-06-15

> ⚠️ **ACCIÓN DE DEPLOY OBLIGATORIA:** aplicar manualmente la migración
> **`backend/migrations/018_add_tabla_warning_generaciones.sql`** en Supabase **antes o junto**
> con este deploy. Agrega la columna `tabla_warning` a `generaciones`. Si el código que lee
> `tabla_warning` (repository + `GenerationResponse`) se sube **sin** la columna creada, **rompe
> el endpoint de polling** `GET /generations/{id}` (la lectura de la fila falla). Las migraciones
> son manuales y numeradas; no hay autoaplicación.

### Cobertura de contenido (tablas-imagen EMF)
- Extractor EMF mejorado: recupera texto UTF-16-LE **con acentos/ñ** (antes filtraba a ASCII y
  rompía "Paysandú", "Médicas", etc.) y emite el contenido como **celdas numeradas** con
  encabezado `[TABLA: N celdas detectadas]`, una celda por línea (conteo contable, no filas exactas).
- Regla de cobertura en `prompt_builder`: instruye a no omitir ninguna **entidad nombrada** de las
  tablas (proyectos/áreas, roles, responsables), usando el texto estructurado como fuente primaria.
- `check_table_coverage` (`outline_validator`): mide cobertura de entidades de tabla en **modo
  WARNING** (loguea `outline.table_coverage`, no bloquea), con matching tolerante al ruido del extractor.
- Advertencia al usuario: nuevo campo **`tabla_warning`** en `generaciones` / `GenerationResponse` —
  cuando el documento traía tablas como imagen, avisa "revisá que todas las filas estén en la presentación".

### Unificación de templates + contraste
- **Motor único de layouts** (`pptx_geometry`, `pptx_layouts`, `pptx_layouts_extra` + helpers en
  `pptx_helpers`): una sola implementación de los 8 layouts; el template solo aporta **tokens de
  color/fuente**. `profesional_claro` y `corporativo_neutro` adoptan la estructura de `ejecutivo_oscuro`
  recoloreada. Resuelve el crash (`AttributeError`) de claro/neutro con cards_3/timeline/split_2col/steps.
- Eliminados `pptx_builder_oscuro/claro/neutro.py` y el despacho `pptx_builders.py`.
- Tokens de paleta normalizados; `ejecutivo_oscuro` tokenizado sin cambio visual (XML idéntico).
- **Contraste WCAG (AA):** en los temas claros, `state_in_progress` → `9A4A06` y `state_done` →
  `21618C` (claro) / `0D6E63` (neutro); los badges "→ En curso" / "✓ Completado" pasaron de ~2:1 a ≥4.5:1
  sobre las cards claras. `ejecutivo_oscuro` sin cambios.

### Fixes de saneamiento
- `cantidad_slides` se propaga a `validate_outline` — antes usaba siempre el default 10 (tope 15) y
  rechazaba outlines válidos cuando el usuario pedía más slides.
- DOCX **EMF-puro** ya no muere con `EMPTY_FILE`: si el `.docx` tiene poco texto pero trae imágenes en
  `word/media/`, se deja pasar para que entre por el canal de visión.

### Infraestructura
- Migración **018**: columna `tabla_warning` en `generaciones` (ver acción de deploy arriba).
- `.gitignore`: reglas para artefactos de QA/scratch (`scratch/`, `backend/test_*.py`,
  `backend/test_*.pptx`, etc.).

## [1.0.0] — 2026-05-10

### Módulo de Presentaciones
- Pipeline completo: extracción de texto (PDF, DOCX, TXT, XLSX) → outline con Claude → PPTX con python-pptx → Supabase Storage
- 3 plantillas visuales: `ejecutivo_oscuro`, `profesional_claro`, `corporativo_neutro`
- Toggle de imágenes del documento en slides
- Upload de logo con inserción en portada
- Integración Gamma con exportación PPTX
- Configuración avanzada de Gamma: tema, estilo de imágenes, paleta, cantidad de slides

### Módulo de Documentos
- Pipeline completo: extracción → outline con Claude → DOCX con docx-js → Supabase Storage
- Estilo de consultoría profesional (Karstec)
- Upload de logo con inserción en encabezado

### Seguridad
- `.gitignore` en raíz del proyecto — `backend/.env` removido del tracking de git
- JWT field estandarizado: `"role"` en generación y lectura en todos los controllers
- Rate limiting: 5/min en login, 20/min en generación y documentos (slowapi)
- `SecurityHeadersMiddleware`: X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy
- CORS: `allow_methods` y `allow_headers` explícitos
- Logger bajado de DEBUG a INFO — eliminados `log.debug` con PII
- Refresh tokens con storage en DB, hash bcrypt y rotación obligatoria

### Fixes
- FormData mismatch: `files→archivos`, `info_adicional→informacion_adicional`
- Parámetro `output` ignorado en el pipeline — ahora se respeta `pptx`/`gamma`/`ambos`
- `xlsx` type mismatch en extracción de imágenes
- Tipos frontend incompletos en `GenerationParametros`

### Refactor
- `docx_service.py` dividido en `docx_service` + `docx_template`
- `auth_service.py` dividido en `auth_service` + `token_service`
- `user_repo.py` dividido en `user_repo` + `user_mutations_repo`
- `documento_repo.py` dividido en `documento_repo` + `documento_mutations_repo`
- `GeneratorForm.tsx` dividido en `GeneratorForm` + `BaseConfigFields` + `LogoPicker`
- `CreateUserModal.tsx` dividido en `CreateUserModal` + `useCreateUserForm`
- `profile/page.tsx` dividido en `page` + `PersonalSection` + `PasswordSection`
- `gamma_service.py` implementado (era stub vacío)

### Tests
- 12/12 tests pasando
- Nuevos: `test_generation_pptx_success`, `test_generation_pptx_invalid_file`, `test_download_output_as_owner`, `test_download_output_as_other_user`

### Infraestructura
- Migración 007: tabla `refresh_tokens` con RLS
- Migración ejecutada: `pptx_gamma_url` en tabla `generaciones`
- `requirements-dev.txt` separado de `requirements.txt`
- `package.json` con versiones exactas (sin `^`)
