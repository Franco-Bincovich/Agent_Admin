-- ─────────────────────────────────────────────────────────────────────────────
-- 008_seed_admin.sql
-- Script de seed: crea el primer usuario administrador.
--
-- Por qué:
--   - El sistema no tiene registro público. El primer admin debe existir en DB
--     para poder crear otros usuarios vía la interfaz de administración.
--   - Este script se corre UNA SOLA VEZ al inicializar la DB en producción.
--   - La contraseña del admin es temporal y DEBE cambiarse en el primer login.
--   - El hash de ejemplo corresponde a 'Admin1234!' generado con bcrypt rounds=12.
--     Reemplazar por un hash real antes de aplicar en producción.
--
-- ⚠️  NO COMMITEAR con una contraseña real. El hash de abajo es de ejemplo.
--     Generar uno nuevo con:
--       python -c "from passlib.hash import bcrypt; print(bcrypt.hash('TuPasswordReal'))"
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO users (
    id,
    email,
    password_hash,
    nombre,
    rol,
    activo,
    created_by
)
VALUES (
    gen_random_uuid(),
    'admin@berazategui.gob.ar',
    '$2b$12$HASH_DE_EJEMPLO_REEMPLAZAR_ANTES_DE_PRODUCCION_xxxxxxxxxx',
    'Administrador del Sistema',
    'admin',
    TRUE,
    NULL   -- el primer admin no tiene created_by
)
ON CONFLICT (email) DO NOTHING;  -- idempotente: no falla si ya existe
