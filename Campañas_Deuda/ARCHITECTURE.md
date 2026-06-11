# Arquitectura — Campañas de Deuda

## Stack elegido y por qué

- **FastAPI** sobre Django: producto interno, necesitamos velocidad de desarrollo,
  tipado estricto con Pydantic y async nativo para la cadena de agentes.
- **Supabase** sobre RDS: RLS nativo (protección de datos por usuario sin código extra),
  Storage integrado para archivos de cartera y documentos generados, Admin UI útil.
- **Anthropic Claude** (claude-sonnet-4-6): la cadena de 4 agentes requiere contexto
  extenso entre pasadas; Claude maneja bien los documentos largos.
- **Perplexity** para contexto económico externo: BCRA e INDEC descartados por
  disponibilidad/estabilidad de API.

## Arquitectura por capas

```
request → Router → Controller → Service → Repository → Supabase
                            ↘ Integration → Anthropic / Perplexity / Gmail
```

Reglas estrictas:
- Los routers no tienen lógica de negocio.
- Los controllers orquestan el flujo entre services y schemas.
- Los services no conocen HTTP (no manejan status codes ni headers).
- Los repositories son el único punto de acceso a la DB.
- Las integrations son wrappers de servicios externos.

## Decisiones de diseño

- **Ejecución asincrónica con polling**: la cadena de 4 agentes puede tardar varios
  minutos. La corrida se dispara en background; el frontend hace polling del estado.
  No se usó WebSocket para mantener la infraestructura simple en v1.
- **Loop de revisión: una sola iteración**: tras la pasada inicial, cada agente revisa
  las tres estrategias. Sin loops abiertos — control de costos y estabilidad.
- **Degradación elegante**: si Perplexity falla, el Agente 3 continúa sin contexto
  externo y lo documenta en el informe. Nunca se aborta la entrega.
- **Datos siempre agregados**: los agentes nunca reciben registros individuales.
  Trabajan sobre totales y segmentos. Privacidad por diseño.
- **OAuth por usuario para Gmail**: cada usuario autoriza con su cuenta. Los
  tokens se almacenan en DB (no texto plano). Envío siempre en CC.
- **Multi-tenancy por user_id**: cada tabla con datos de usuario tiene FK a users
  y RLS habilitado. Un analista no accede a datos de otro.

## Deuda técnica conocida

- **Columnas reales de la cartera sin definir**: la calidad de la estrategia depende
  de qué tan ricos sean los agregados que recibe el Agente 1. Hay que definir las
  columnas reales del archivo del municipio antes de Sesión 5.
- **Sin deploy en AWS todavía**: la infraestructura de producción está fuera del
  alcance de las primeras sesiones. Primero local.
- **Cifrado de tokens Gmail**: el esquema exacto de cifrado/almacenamiento de tokens
  OAuth se define en Sesión 19.
