-- ─────────────────────────────────────────────────────────────────────────────
-- 003_create_gmail_tokens.sql
-- Tokens OAuth de Gmail por usuario.
--
-- Por qué:
--   - Cada usuario autoriza Gmail individualmente (OAuth por usuario, no shared).
--   - El access_token expira en ~1h; el refresh_token permite obtener uno nuevo
--     sin que el usuario tenga que re-autorizar.
--   - Los tokens se almacenan cifrados (o al menos no en texto plano visible en
--     logs/UI). La política exacta de cifrado se define en Sesión 19.
--   - scope registra los permisos que el usuario otorgó (solo 'gmail.send').
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS gmail_tokens (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    access_token    TEXT        NOT NULL,
    refresh_token   TEXT        NOT NULL,
    token_expiry    TIMESTAMPTZ NOT NULL,
    scope           TEXT        NOT NULL DEFAULT 'https://www.googleapis.com/auth/gmail.send',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE gmail_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_gmail_tokens" ON gmail_tokens
    FOR ALL
    USING (auth.uid() = user_id);
