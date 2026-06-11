-- migrations/017_create_planificacion.sql
-- Módulo Planificación: gestión de cronogramas de proyectos de licitación.
-- Importa archivos de origen (Excel/CSV de Project, .mpp, PDF) y los normaliza
-- en tres tablas jerárquicas: proyecto → área → tarea.
-- El módulo es paralelo e independiente; solo comparte la FK a usuarios.


-- ─────────────────────────────────────────────────────────────────────────────
-- TABLA 1: planificacion_proyectos
-- Representa un proyecto de licitación completo importado por un usuario.
-- Reutiliza el mismo patrón async de generaciones: el endpoint POST retorna 202
-- con estado='procesando', el pipeline corre en background y actualiza el estado
-- a 'listo' o 'error' cuando termina.
-- actualizado_en se gestiona con el trigger set_actualizado_en() (definido en 015).
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE planificacion_proyectos (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id      UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre          TEXT        NOT NULL,
    expediente      TEXT,
    prioridad       TEXT        CHECK (prioridad IN ('alta', 'media', 'baja')) DEFAULT 'media',
    origen          TEXT        CHECK (origen IN ('excel', 'mpp', 'pdf')),
    archivo_url     TEXT,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    estado          TEXT        CHECK (estado IN ('procesando', 'listo', 'error')) DEFAULT 'procesando',
    error_detalle   TEXT,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ DEFAULT NOW()
);

-- Historial de proyectos por usuario, filtrado frecuente en la UI.
CREATE INDEX idx_planificacion_proyectos_usuario_id
    ON planificacion_proyectos (usuario_id);

-- El historial ordena por fecha descendente en todos los módulos del sistema.
CREATE INDEX idx_planificacion_proyectos_creado_en
    ON planificacion_proyectos (creado_en DESC);

ALTER TABLE planificacion_proyectos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "usuario_ve_propios_proyectos_planificacion" ON planificacion_proyectos
    FOR ALL
    USING (auth.uid() = usuario_id);

CREATE POLICY "administrador_ve_todos_proyectos_planificacion" ON planificacion_proyectos
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );

-- Mantiene actualizado_en al mismo valor que NOW() en cada UPDATE.
-- set_actualizado_en() fue definido en la migración 015.
CREATE TRIGGER trg_planificacion_proyectos_actualizado_en
    BEFORE UPDATE ON planificacion_proyectos
    FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();


-- ─────────────────────────────────────────────────────────────────────────────
-- TABLA 2: planificacion_areas
-- Agrupa las tareas de un proyecto por capítulo WBS de nivel 2 (ej. "1.2 Obra Civil").
-- El responsable se guarda como texto libre porque en V1 no es un usuario del sistema:
-- es un dato de contacto externo (nombre, teléfono, email) que viene del proyecto.
-- disponibilidad_horas y cantidad_empleados son opcionales y salen de la sección
-- de recursos del archivo de origen, si está presente.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE planificacion_areas (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proyecto_id           UUID        NOT NULL REFERENCES planificacion_proyectos(id) ON DELETE CASCADE,
    nombre                TEXT        NOT NULL,
    cap_wbs               TEXT,
    color                 TEXT,
    responsable_nombre    TEXT,
    responsable_telefono  TEXT,
    responsable_email     TEXT,
    disponibilidad_horas  INTEGER,
    cantidad_empleados    INTEGER,
    creado_en             TIMESTAMPTZ DEFAULT NOW()
);

-- FK más consultada: todas las áreas de un proyecto.
CREATE INDEX idx_planificacion_areas_proyecto_id
    ON planificacion_areas (proyecto_id);

ALTER TABLE planificacion_areas ENABLE ROW LEVEL SECURITY;

-- Ownership se verifica a través del proyecto padre.
CREATE POLICY "usuario_ve_propias_areas_planificacion" ON planificacion_areas
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM planificacion_proyectos p
            WHERE p.id = proyecto_id
              AND p.usuario_id = auth.uid()
        )
    );

CREATE POLICY "administrador_ve_todas_areas_planificacion" ON planificacion_areas
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );


-- ─────────────────────────────────────────────────────────────────────────────
-- TABLA 3: planificacion_tareas
-- Cada fila es una tarea (o resumen de tareas) del cronograma.
-- fecha_estimada=true + confianza indica que la fecha no vino como dato explícito
-- en el archivo de origen (caso típico: PDF de barras donde se infiere la duración
-- pero no la fecha exacta de inicio). Esto permite distinguir datos confiables
-- de estimaciones y mostrarlos diferenciado en la UI.
-- predecesoras se guarda como texto si el archivo las trae (ej. "3,4FS") pero
-- no se usa en V1; se reserva para futura visualización de dependencias.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE planificacion_tareas (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proyecto_id     UUID        NOT NULL REFERENCES planificacion_proyectos(id) ON DELETE CASCADE,
    area_id         UUID        REFERENCES planificacion_areas(id) ON DELETE SET NULL,
    -- wbs identifica la tarea dentro del proyecto (ej. "1.2.3").
    -- El UNIQUE al final de esta tabla garantiza identidad estable:
    -- al reimportar el mismo proyecto, el UPSERT por (proyecto_id, wbs) preserva
    -- el estado completada/completada_en/completada_por ya marcado por el usuario.
    -- Sin esa unicidad, cada reimportación generaría duplicados y se perdería el progreso.
    wbs             TEXT        NOT NULL,
    nombre          TEXT        NOT NULL,
    nivel           INTEGER     NOT NULL,
    es_resumen      BOOLEAN     DEFAULT FALSE,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    fecha_estimada  BOOLEAN     DEFAULT FALSE,
    confianza       TEXT        CHECK (confianza IN ('alta', 'media', 'baja')) DEFAULT 'alta',
    predecesoras    TEXT,
    completada      BOOLEAN     DEFAULT FALSE,
    completada_en   TIMESTAMPTZ,
    -- ON DELETE SET NULL: si se elimina el usuario que marcó la tarea,
    -- la tarea sigue registrada como completada; solo se pierde el "quién".
    completada_por  UUID        REFERENCES usuarios(id) ON DELETE SET NULL,
    creado_en       TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT planificacion_tareas_proyecto_wbs_key UNIQUE (proyecto_id, wbs)
);

-- FK más consultadas: todas las tareas de un proyecto y de un área específica.
CREATE INDEX idx_planificacion_tareas_proyecto_id
    ON planificacion_tareas (proyecto_id);

CREATE INDEX idx_planificacion_tareas_area_id
    ON planificacion_tareas (area_id);

ALTER TABLE planificacion_tareas ENABLE ROW LEVEL SECURITY;

-- Ownership se verifica a través del proyecto padre.
CREATE POLICY "usuario_ve_propias_tareas_planificacion" ON planificacion_tareas
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM planificacion_proyectos p
            WHERE p.id = proyecto_id
              AND p.usuario_id = auth.uid()
        )
    );

CREATE POLICY "administrador_ve_todas_tareas_planificacion" ON planificacion_tareas
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );
