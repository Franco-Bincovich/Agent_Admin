-- ─────────────────────────────────────────────────────────────────────────────
-- 006_create_execution_logs.sql
-- Trazabilidad de cada paso de una corrida.
--
-- Por qué:
--   - Cada evento de la cadena de agentes (inicio agente, fin agente, error,
--     degradación de servicio externo) se registra aquí.
--   - Permite diagnosticar qué pasó, cuándo y en qué agente ante un fallo.
--   - El campo 'nivel' sigue los mismos niveles del logger central.
--   - 'agente' indica cuál de los 4 agentes (o el orquestador) generó el log.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS execution_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id    UUID        NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    agente          TEXT        NOT NULL CHECK (agente IN (
                        'orquestador',
                        'agente_1_gestion_deuda',
                        'agente_2_director_rentas',
                        'agente_3_economista',
                        'agente_4_ejecutivo',
                        'perplexity',
                        'gmail',
                        'documento'
                    )),
    nivel           TEXT        NOT NULL CHECK (nivel IN ('info', 'warning', 'error')),
    mensaje         TEXT        NOT NULL,
    detalle         JSONB,      -- datos adicionales para diagnóstico
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exec_logs_execution ON execution_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_exec_logs_created   ON execution_logs(created_at DESC);

ALTER TABLE execution_logs ENABLE ROW LEVEL SECURITY;

-- Los logs se ven junto con la ejecución a la que pertenecen
CREATE POLICY "users_see_own_exec_logs" ON execution_logs
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM executions e
            WHERE e.id = execution_id AND e.created_by = auth.uid()
        )
    );

CREATE POLICY "admins_see_all_exec_logs" ON execution_logs
    FOR SELECT
    USING (EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.rol = 'admin'));
