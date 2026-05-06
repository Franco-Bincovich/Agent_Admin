-- migrations/004_create_documentos.sql
-- Tabla de historial de documentos Word (DOCX) generados por el pipeline de documentos.
-- Cada fila representa un documento completo: desde los archivos fuente hasta el DOCX final.
-- archivos, secciones y opciones son JSONB para flexibilidad sin migraciones adicionales.
-- outline almacena la estructura generada por IA antes de construir el documento.
-- ON DELETE CASCADE garantiza limpieza automática al eliminar un usuario (cumple GDPR).

CREATE TABLE documentos (
    -- Identificador único del documento generado.
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dueño del documento. Requerido; sin usuario no hay documento.
    usuario_id      UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,

    -- Título visible para el usuario en su historial.
    titulo          TEXT        NOT NULL,

    -- Lista de objetos con metadata de los archivos fuente (nombre, path, tipo).
    -- Formato: [{"nombre": "informe.pdf", "path": "...", "tipo": "pdf"}, ...]
    archivos        JSONB       DEFAULT '[]',

    -- Nombre de la plantilla Word usada (nullable si no se usó plantilla).
    plantilla_nombre TEXT,

    -- Secciones seleccionadas por el usuario para este documento.
    -- Formato: ["resumen_ejecutivo", "analisis", ...]
    secciones       JSONB       DEFAULT '[]',

    -- Instrucciones libres del usuario para personalizar el contenido.
    indicaciones    TEXT,

    -- Opciones booleanas de procesamiento elegidas por el usuario.
    -- Formato: {"homogeneizar": true, "deduplicar": false, "usar_imagenes": true}
    opciones        JSONB       DEFAULT '{}',

    -- Estructura de secciones generada por IA antes de construir el DOCX.
    -- Permite reintentar la construcción sin regenerar el outline si ya existe.
    outline         JSONB       DEFAULT '{}',

    -- URL pública del archivo DOCX generado (null mientras está procesando o si hubo error).
    docx_url        TEXT,

    -- Estado del pipeline de generación.
    -- 'procesando': en curso  |  'listo': disponible para descarga  |  'error': falló.
    estado          TEXT        CHECK (estado IN ('procesando', 'listo', 'error')) DEFAULT 'procesando',

    -- Fecha y hora de creación con zona horaria, para ordenar el historial.
    creado_en       TIMESTAMPTZ DEFAULT NOW()
);

-- Filtrar documentos por usuario es la query más frecuente (historial personal).
CREATE INDEX idx_documentos_usuario_id ON documentos (usuario_id);

-- El historial y el panel de administración ordenan siempre por fecha descendente.
CREATE INDEX idx_documentos_creado_en ON documentos (creado_en DESC);

ALTER TABLE documentos ENABLE ROW LEVEL SECURITY;

-- Cada usuario solo puede ver y operar sobre sus propios documentos.
-- usuario_id referencia usuarios.id, que es el mismo UUID que auth.uid() en Supabase.
CREATE POLICY "usuario_ve_propios_documentos" ON documentos
    FOR ALL
    USING (auth.uid() = usuario_id);

-- Los administradores necesitan acceso a todos los documentos
-- para soporte, monitoreo y análisis de uso del sistema.
CREATE POLICY "administrador_ve_todos_documentos" ON documentos
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );
