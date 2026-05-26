-- Agrega columna pptx_gamma_url a la tabla generaciones.
-- Esta columna fue usada por generation_repo.update_resultado
-- pero nunca fue incluida en las migraciones anteriores.

ALTER TABLE generaciones
ADD COLUMN IF NOT EXISTS pptx_gamma_url TEXT;
