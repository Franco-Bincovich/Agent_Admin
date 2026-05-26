-- migrations/013_create_video_brand_config.sql
-- Tabla de configuración de marca por usuario para el agente de video.
-- Una fila por usuario (UNIQUE en usuario_id): upsert en lugar de insert.
-- Almacena logo, colores y fuente para aplicar branding automático a los videos.
-- Nullable en todos los campos de config: el usuario puede completar solo los que necesite.

CREATE TABLE video_brand_config (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id       UUID        UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    logo_url         TEXT,
    color_primario   TEXT,
    color_secundario TEXT,
    fuente           TEXT,
    actualizado_en   TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE video_brand_config ENABLE ROW LEVEL SECURITY;

-- Cada usuario solo puede ver y operar sobre su propia configuración de marca.
CREATE POLICY "usuario_ve_propia_video_brand_config" ON video_brand_config
    FOR ALL
    USING (auth.uid() = usuario_id);
