-- migrations/012_create_video_jobs.sql
-- Tabla de jobs de edición de video.
-- Cada fila representa un trabajo de procesamiento: desde el video original
-- hasta el video editado final. parametros es JSONB para flexibilidad en
-- opciones de edición sin requerir migraciones adicionales.
-- ON DELETE CASCADE asegura limpieza automática al eliminar un usuario.

CREATE TABLE video_jobs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id      UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo          TEXT,
    estado          TEXT        CHECK (estado IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
    video_input_url TEXT,
    output_url      TEXT,
    parametros      JSONB       DEFAULT '{}',
    error_message   TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

-- Filtrar jobs por usuario es la query más frecuente (historial personal).
CREATE INDEX idx_video_jobs_usuario_id ON video_jobs (usuario_id);

-- El historial y el panel admin ordenan siempre por fecha descendente.
CREATE INDEX idx_video_jobs_creado_en ON video_jobs (creado_en DESC);

ALTER TABLE video_jobs ENABLE ROW LEVEL SECURITY;

-- Cada usuario solo puede ver y operar sobre sus propios jobs.
CREATE POLICY "usuario_ve_propios_video_jobs" ON video_jobs
    FOR ALL
    USING (auth.uid() = usuario_id);
