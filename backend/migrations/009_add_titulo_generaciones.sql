-- migrations/009_add_titulo_generaciones.sql
-- Agrega columna titulo a la tabla generaciones.

ALTER TABLE generaciones
ADD COLUMN IF NOT EXISTS titulo TEXT DEFAULT '';
