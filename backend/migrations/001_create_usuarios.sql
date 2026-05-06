-- migrations/001_create_usuarios.sql
-- Tabla base de usuarios del sistema.
-- Centraliza identidad, credenciales y rol en un solo lugar para simplificar
-- la lógica de autorización: el rol vive aquí y no en una tabla separada
-- porque en este sistema los roles son fijos y no requieren permisos granulares.
-- RLS habilitado para que ningún usuario pueda leer datos de otro,
-- incluso si hay un bug de autorización en la aplicación (defensa en profundidad).

CREATE TABLE usuarios (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre       TEXT        NOT NULL,
    email        TEXT        UNIQUE NOT NULL,
    password_hash TEXT       NOT NULL,
    rol          TEXT        CHECK (rol IN ('administrador', 'editor', 'viewer')) DEFAULT 'editor',
    activo       BOOLEAN     DEFAULT TRUE,
    creado_en    TIMESTAMPTZ DEFAULT NOW()
);

-- Búsqueda por email es frecuente en login y validación de unicidad.
CREATE INDEX idx_usuarios_email ON usuarios (email);

ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Cada usuario autenticado solo puede ver su propio registro.
-- Usa auth.uid() de Supabase para comparar con el id de la fila.
CREATE POLICY "usuario_ve_propio_registro" ON usuarios
    FOR ALL
    USING (auth.uid() = id);

-- Los administradores necesitan acceso total para gestión de usuarios
-- desde el panel de administración.
CREATE POLICY "administrador_ve_todos" ON usuarios
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM usuarios u
            WHERE u.id = auth.uid()
              AND u.rol = 'administrador'
              AND u.activo = TRUE
        )
    );
