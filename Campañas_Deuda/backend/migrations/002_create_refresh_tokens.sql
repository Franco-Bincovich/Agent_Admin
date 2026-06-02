-- ─────────────────────────────────────────────────────────────────────────────
-- 002_create_refresh_tokens.sql
-- Almacenamiento de refresh tokens hasheados.
--
-- Por qué:
--   - Los refresh tokens no se guardan en texto plano (SEGURIDAD-PENTEST §2.5).
--     Se guarda el hash bcrypt; al verificar, se compara con verify_hash().
--   - Rotación obligatoria: al hacer refresh, el registro anterior se elimina
--     y se crea uno nuevo. Un token viejo que llega = intento sospechoso → revocar.
--   - expires_at permite limpiar tokens vencidos sin depender del cliente.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT        NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id   ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Solo el propio usuario ve sus tokens (el backend usa service_key de todas formas)
CREATE POLICY "users_own_refresh_tokens" ON refresh_tokens
    FOR ALL
    USING (auth.uid() = user_id);
