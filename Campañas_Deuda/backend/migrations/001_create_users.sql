-- ─────────────────────────────────────────────────────────────────────────────
-- 001_create_users.sql
-- Tabla principal de usuarios del sistema.
--
-- Por qué:
--   - Sistema interno con dos roles (admin y analista). El admin crea usuarios;
--     no hay registro público (onboarding autónomo no aplica — uso interno).
--   - created_by es nullable para permitir que el primer admin no tenga creador
--     (se siembra vía seed, ver 008_seed_admin.sql).
--   - activo implementa soft-delete para preservar la trazabilidad de ejecuciones
--     históricas sin perder la FK usuario-ejecución.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT        UNIQUE NOT NULL,
    password_hash TEXT      NOT NULL,
    nombre      TEXT        NOT NULL CHECK (char_length(nombre) BETWEEN 2 AND 100),
    rol         TEXT        NOT NULL CHECK (rol IN ('admin', 'analista')),
    activo      BOOLEAN     NOT NULL DEFAULT TRUE,
    created_by  UUID        REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email  ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_activo ON users(activo);

-- RLS: habilitado. El backend usa service_key (bypassea RLS).
-- Las policies protegen si alguna consulta llega con anon_key por error.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_see_own_record" ON users
    FOR SELECT
    USING (
        auth.uid() = id
        OR EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin')
    );

CREATE POLICY "admins_manage_users" ON users
    FOR ALL
    USING (EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin'));
