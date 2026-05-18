-- migrations/011_add_gamma_warning_generaciones.sql
-- Agrega gamma_warning a generaciones para persistir advertencias de organización en Gamma.
-- Se usa cuando el pipeline no encuentra carpeta Gamma para el usuario: la advertencia
-- se guarda junto con el resultado y se retorna en GenerationResponse al frontend.
-- NULL indica que no hubo advertencia (caso normal).

ALTER TABLE generaciones ADD COLUMN gamma_warning TEXT;
