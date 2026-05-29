ALTER TABLE generaciones
  ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ DEFAULT NOW();

ALTER TABLE documentos
  ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ DEFAULT NOW();

CREATE OR REPLACE FUNCTION set_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
  NEW.actualizado_en = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generaciones_actualizado_en
  BEFORE UPDATE ON generaciones
  FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();

CREATE TRIGGER trg_documentos_actualizado_en
  BEFORE UPDATE ON documentos
  FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
