-- ─────────────────────────────────────────────────────────────────────────────
-- 004_create_portfolio_files.sql
-- Archivos de cartera subidos por los usuarios.
--
-- Por qué:
--   - La cartera se sube como archivo antes de cada corrida (sin conexión en
--     vivo a la base municipal). Se almacenan metadatos + agregados parseados.
--   - Los agregados (monto_total, cantidad_partidas) se extraen del archivo y
--     se guardan para que los agentes los reciban sin tener que re-parsear.
--   - file_path apunta al storage de Supabase (bucket 'portfolios').
--   - Los agentes nunca ven datos individuales de deudores — solo los agregados
--     de las columnas definidas en la Sesión 5.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS portfolio_files (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename            TEXT        NOT NULL,
    file_path           TEXT        NOT NULL,  -- path en Supabase Storage
    mime_type           TEXT        NOT NULL,
    size_bytes          BIGINT      NOT NULL,
    cartera             TEXT        NOT NULL CHECK (cartera IN ('servicios_generales', 'servicio_sanitario', 'automotor', 'todas')),
    dureza              TEXT        NOT NULL CHECK (dureza IN ('blanda', 'intermedia', 'dura', 'todas')),
    periodo             TEXT        NOT NULL,
    -- Agregados parseados (se completan en Sesión 5 según columnas reales del municipio)
    monto_total         NUMERIC,
    cantidad_partidas   INTEGER,
    agregados_json      JSONB,      -- campo flexible para agregados adicionales
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_files_user     ON portfolio_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_portfolio_files_cartera  ON portfolio_files(cartera);

ALTER TABLE portfolio_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_portfolios" ON portfolio_files
    FOR ALL
    USING (auth.uid() = uploaded_by);

CREATE POLICY "admins_see_all_portfolios" ON portfolio_files
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin'));
