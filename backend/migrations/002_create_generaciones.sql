-- migrations/002_create_generaciones.sql
-- Tabla de generaciones de presentaciones.
-- Cada fila representa un pipeline completo: desde el objetivo del usuario
-- hasta la presentación final en PPTX y/o Gamma.
-- archivos y parametros son JSONB para flexibilidad: los archivos adjuntos
-- y los parámetros de configuración pueden variar sin requerir migraciones adicionales.
-- outline y el estado permiten reanudar o reintentar generaciones fallidas.
-- ON DELETE CASCADE asegura que al eliminar un usuario sus generaciones se limpien
-- automáticamente, cumpliendo GDPR y manteniendo integridad referencial.

CREATE TABLE generaciones (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id  UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    objetivo    TEXT        NOT NULL,
    archivos    JSONB       DEFAULT '[]',
    parametros  JSONB       DEFAULT '{}',
    outline     JSONB       DEFAULT '{}',
    pptx_url    TEXT,
    gamma_url   TEXT,
    estado      TEXT        CHECK (estado IN ('procesando', 'listo', 'error')) DEFAULT 'procesando',
    slides_count INTEGER    DEFAULT 0,
    creado_en   TIMESTAMPTZ DEFAULT NOW()
);

-- Filtrar generaciones por usuario es la query más frecuente (historial personal).
CREATE INDEX idx_generaciones_usuario_id ON generaciones (usuario_id);

-- El panel de administración y el historial ordenan siempre por fecha descendente.
CREATE INDEX idx_generaciones_creado_en ON generaciones (creado_en DESC);

ALTER TABLE generaciones ENABLE ROW LEVEL SECURITY;

-- Cada usuario solo puede ver y operar sobre sus propias generaciones.
-- usuario_id referencia usuarios.id, que es el mismo UUID que auth.uid() en Supabase.
CREATE POLICY "usuario_ve_propias_generaciones" ON generaciones
    FOR ALL
    USING (auth.uid() = usuario_id);

-- Los administradores necesitan acceso a todas las generaciones
-- para soporte, monitoreo y análisis de uso del sistema.
CREATE POLICY "administrador_ve_todas_generaciones" ON generaciones
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );
