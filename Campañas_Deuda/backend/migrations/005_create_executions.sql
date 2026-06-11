-- ─────────────────────────────────────────────────────────────────────────────
-- 005_create_executions.sql
-- Corridas de análisis (ejecuciones de la cadena de agentes).
--
-- Por qué:
--   - Cada corrida es asincrónica. El estado avanza de 'pendiente' → 'corriendo'
--     → 'listo' | 'error'. El frontend hace polling del estado.
--   - resultado_url apunta al .docx generado en Supabase Storage.
--   - La selección de dimensiones es única por dimensión (una cartera,
--     una dureza, un período — o 'todas' para cada uno).
--   - Las ejecuciones programadas (cron) también crean registros aquí.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS executions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by          UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_file_id   UUID        NOT NULL REFERENCES portfolio_files(id) ON DELETE RESTRICT,
    cartera             TEXT        NOT NULL CHECK (cartera IN ('servicios_generales', 'servicio_sanitario', 'automotor', 'todas')),
    dureza              TEXT        NOT NULL CHECK (dureza IN ('blanda', 'intermedia', 'dura', 'todas')),
    periodo             TEXT        NOT NULL,
    estado              TEXT        NOT NULL DEFAULT 'pendiente'
                            CHECK (estado IN ('pendiente', 'corriendo', 'listo', 'error')),
    resultado_url       TEXT,       -- URL del .docx en Supabase Storage
    error_message       TEXT,
    started_at          TIMESTAMPTZ,
    finished_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_executions_user    ON executions(created_by);
CREATE INDEX IF NOT EXISTS idx_executions_estado  ON executions(estado);
CREATE INDEX IF NOT EXISTS idx_executions_created ON executions(created_at DESC);

ALTER TABLE executions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_executions" ON executions
    FOR ALL
    USING (auth.uid() = created_by);

CREATE POLICY "admins_see_all_executions" ON executions
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin'));
