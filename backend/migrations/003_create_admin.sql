-- migrations/003_create_admin.sql
-- Seed del primer usuario administrador del sistema.
-- Necesario para poder ingresar al panel de administración desde el primer deploy.
--
-- SEGURIDAD — LEER ANTES DE EJECUTAR EN PRODUCCIÓN:
-- El password 'Admin1234!' es solo para desarrollo local y staging inicial.
-- DEBE cambiarse inmediatamente después del primer login en cualquier entorno
-- que no sea desarrollo local. En producción, generar un password único con al
-- menos 20 caracteres (mayúsculas, minúsculas, números y símbolos).
--
-- pgcrypto debe estar habilitada en la base de datos:
--   CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO usuarios (nombre, email, password_hash, rol, activo)
VALUES (
    'Administrador',
    'admin@agentadmin.com',
    -- crypt() usa bcrypt con work factor 12 (balance seguridad/rendimiento).
    -- El salt aleatorio se genera automáticamente dentro de gen_salt.
    crypt('Admin1234!', gen_salt('bf', 12)),
    'administrador',
    TRUE
)
ON CONFLICT (email) DO NOTHING;
-- ON CONFLICT evita error si se ejecuta la migración más de una vez.
