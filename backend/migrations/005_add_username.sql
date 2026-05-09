-- Agrega columna username a usuarios para login sin exponer email.
-- UNIQUE garantizado a nivel DB; índice acelera búsqueda en login.

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS username TEXT UNIQUE;

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios (username);
