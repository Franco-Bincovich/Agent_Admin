-- Plantillas de estructura de documentos por usuario.
-- Permite a cada usuario guardar combinaciones de secciones
-- reutilizables para el flujo de creación de documentos.

CREATE TABLE IF NOT EXISTS document_templates (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id  UUID        NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre      TEXT        NOT NULL CHECK (char_length(nombre) BETWEEN 1 AND 100),
    secciones   JSONB       NOT NULL DEFAULT '[]',
    is_default  BOOLEAN     NOT NULL DEFAULT FALSE,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE document_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "usuario_ve_propias_plantillas" ON document_templates
    FOR ALL
    USING (auth.uid() = usuario_id);

CREATE INDEX idx_document_templates_usuario
    ON document_templates(usuario_id);

CREATE TRIGGER trg_document_templates_actualizado_en
    BEFORE UPDATE ON document_templates
    FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
