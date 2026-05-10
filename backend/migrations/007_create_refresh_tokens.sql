-- migrations/007_create_refresh_tokens.sql
-- Almacena refresh tokens hasheados para rotación obligatoria (SEGURIDAD-PENTEST 2.5).
-- El token en texto plano nunca se guarda — solo su hash bcrypt.
-- ON DELETE CASCADE garantiza limpieza automática al eliminar un usuario.

CREATE TABLE refresh_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token_hash  TEXT        NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    expires_at  TIMESTAMPTZ NOT NULL
);

ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
