# Changelog — Agent Admin

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
