# Arquitectura — Agent Admin

## Stack elegido y por qué

- **FastAPI** sobre otras opciones — velocidad, tipado estricto, async nativo
- **Supabase** como DB — RLS nativo, auth integrado, Storage incluido
- **python-pptx** para generación PPTX — generación programática sin archivos template, control total del diseño
- **Gamma vía MCP** para presentaciones con IA — output visual de mayor calidad que PPTX puro
- **Vercel** para deploy inicial, AWS como objetivo de producción

## Decisiones de diseño

- **Arquitectura por capas estricta:** router → controller → service → repository. Límites de líneas por tipo de archivo enforceados.
- **Background tasks con polling** para generaciones largas — evita timeout en requests HTTP; el cliente hace polling cada 3 segundos hasta estado="listo".
- **Tres plantillas PPTX hardcodeadas** (`ejecutivo_oscuro`, `profesional_claro`, `corporativo_neutro`) — programáticas con python-pptx, sin archivos .pptx de referencia.
- **Motor único de layouts + paleta por template (2026-06-15):** los 8 layouts (portada, contenido, destacado, cierre, cards_3, timeline, split_2col, steps) tienen una sola implementación compartida — `pptx_geometry.py` (geometría/posiciones), `pptx_layouts.py` (layouts base + registro `BUILDERS`), `pptx_layouts_extra.py` (cards_3/timeline/split_2col/steps), con helpers en `utils/pptx_helpers.py`. La **estructura/geometría es única**; el template solo aporta **tokens de color/fuente** (`background`, `accent`, `surface`, `card_primary/secondary`, `text`, `text_secondary`, `on_accent`, `state_in_progress`, `state_done`, fuentes y tamaños). **Decisión consciente:** `profesional_claro` y `corporativo_neutro` perdieron sus layouts base propios (panel lateral navy, bullets numerados, etc.) y adoptaron la estructura de `ejecutivo_oscuro` recoloreada. Motivo: antes solo `oscuro` implementaba los 4 layouts nuevos y claro/neutro crasheaban (`AttributeError`) al usarlos; una sola lógica elimina la duplicación y el crash. Se eliminaron `pptx_builder_oscuro/claro/neutro.py` y el despacho `pptx_builders.py`.
- **Extracción de imágenes activable por toggle** — no forzada en todos los outputs para no romper presentaciones que no las necesitan.
- **Refresh tokens con storage en DB y rotación obligatoria** — al rotar se invalida el token anterior.
- **Split de servicios:** `auth_service` (identidad + JWT) separado de `token_service` (ciclo de vida de refresh tokens).

## Deuda técnica conocida

- `dropdown-menu.tsx` y `dialog.tsx` son componentes Shadcn copiados que superan el límite de líneas — excepción aceptada por ser código de librería.
- Gamma: integración funcional pero sin pruebas en entorno de producción con credenciales reales.
- `/auth/refresh` está en `PUBLIC_ROUTES` pero el endpoint ahora sí valida el refresh token en DB.

### Cobertura de contenido de tablas-imagen EMF (2026-06-15)

- **Parser de grilla EMF real (pendiente).** El extractor de tablas embebidas como imagen EMF (`image_extraction_service._leer_texto_utf16_emf`) entrega **celdas sueltas sin estructura de filas** (camino pragmático: recuperar UTF-16-LE con acentos + numerar celdas, pero sin reconstruir la grilla). **Por qué importa:** sin coordenadas de fila, la atribución celda→fila no está garantizada; una celda puede quedar asignada a la fila equivocada. Caso observado en el e2e de Capital Humano: "Analista Funcional" quedó atribuido a *Paysandú* en vez de a *Datos*. La cobertura de entidades queda **mitigada, no garantizada**. **Por qué se difirió:** el fix real (parsear records EMF `EMR_EXTTEXTOUTW` con sus coordenadas X/Y) es caro y frágil — el formato EMF varía por generador.
- **Validación de cobertura de tablas en modo WARNING.** `outline_validator.check_table_coverage` solo **loguea** entidades faltantes (`outline.table_coverage`); **no reintenta ni bloquea** la generación. **Por qué:** depende del extractor de arriba — no tiene sentido escalar a reintento mientras las filas no sean confiables (se generarían reintentos espurios). Además detecta **presencia** de entidades, no **atribución** correcta: no detecta el caso de fila mal asignada descrito arriba. Escalará a reintento dirigido recién cuando exista el parser de grilla.
- **Truncado del bloque de tablas a 8000 chars.** El texto EMF estructurado se concatena al **final** de `texto_extraido`, y `prompt_sanitizer.sanitize_for_prompt` trunca a 8000 caracteres. **Consecuencia:** con documentos fuente muy largos, el bloque `[TABLAS DEL DOCUMENTO]` puede recortarse y perder filas. **No resuelto:** requeriría reordenar para priorizar las tablas por delante del cuerpo, o subir/segmentar el límite.

### Archivos sobre el límite de 150 líneas (2026-06-15)

- `pptx_layouts_extra.py` (**210**) — por el split acordado base/nuevos del motor de layouts; los 4 layouts nuevos no entran en 150. Aceptado conscientemente (reemplaza un `pptx_builder_oscuro.py` de 346).
- `image_extraction_service.py` (**273**) — deuda pre-existente, agravada levemente por el extractor EMF. Split bloqueado mientras `generation_service` importe sus funciones.
- `ai_service.py` (**238**) y `generation_service.py` (**184**) — sobre 150 tras los cambios de cobertura de esta sesión (deuda pre-existente + adiciones mínimas). Pendiente de refactor por capas.
