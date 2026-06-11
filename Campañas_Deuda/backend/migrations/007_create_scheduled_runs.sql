-- ─────────────────────────────────────────────────────────────────────────────
-- 007_create_scheduled_runs.sql
-- Configuración de corridas programadas por cron.
--
-- Por qué:
--   - Los ejecutivos quieren corridas automáticas sin intervención manual.
--   - La expresión cron se evalúa en America/Argentina/Buenos_Aires (no UTC)
--     para que "lunes a las 8 AM" signifique lo que dice.
--   - activo permite pausar una corrida programada sin borrarla.
--   - last_run_at y next_run_at permiten al scheduler saber cuándo disparar
--     sin necesidad de recalcular el cron en cada tick.
--   - Los parámetros (cartera, dureza, período) se almacenan para que la
--     corrida programada use la misma configuración siempre.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scheduled_runs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by          UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    nombre              TEXT        NOT NULL,
    cron_expression     TEXT        NOT NULL,    -- ej: "0 8 * * 1" = lunes a las 8
    timezone            TEXT        NOT NULL DEFAULT 'America/Argentina/Buenos_Aires',
    cartera             TEXT        NOT NULL CHECK (cartera IN ('servicios_generales', 'servicio_sanitario', 'automotor', 'todas')),
    dureza              TEXT        NOT NULL CHECK (dureza IN ('blanda', 'intermedia', 'dura', 'todas')),
    periodo             TEXT        NOT NULL,
    activo              BOOLEAN     NOT NULL DEFAULT TRUE,
    last_run_at         TIMESTAMPTZ,
    next_run_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_runs_user        ON scheduled_runs(created_by);
CREATE INDEX IF NOT EXISTS idx_scheduled_runs_activo      ON scheduled_runs(activo);
CREATE INDEX IF NOT EXISTS idx_scheduled_runs_next_run_at ON scheduled_runs(next_run_at);

ALTER TABLE scheduled_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_scheduled_runs" ON scheduled_runs
    FOR ALL
    USING (auth.uid() = created_by);

CREATE POLICY "admins_see_all_scheduled_runs" ON scheduled_runs
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin'));
