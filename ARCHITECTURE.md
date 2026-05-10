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
- **Extracción de imágenes activable por toggle** — no forzada en todos los outputs para no romper presentaciones que no las necesitan.
- **Refresh tokens con storage en DB y rotación obligatoria** — al rotar se invalida el token anterior.
- **Split de servicios:** `auth_service` (identidad + JWT) separado de `token_service` (ciclo de vida de refresh tokens).

## Deuda técnica conocida

- `dropdown-menu.tsx` y `dialog.tsx` son componentes Shadcn copiados que superan el límite de líneas — excepción aceptada por ser código de librería.
- Gamma: integración funcional pero sin pruebas en entorno de producción con credenciales reales.
- `/auth/refresh` está en `PUBLIC_ROUTES` pero el endpoint ahora sí valida el refresh token en DB.
