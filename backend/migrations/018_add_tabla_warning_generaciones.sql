-- migrations/018_add_tabla_warning_generaciones.sql
-- Agrega tabla_warning a generaciones para avisar que el documento traía tablas
-- como imagen (EMF/WMF). En esos casos la cobertura de filas es mitigación fuerte,
-- no garantía: la advertencia se guarda junto al resultado y se retorna en
-- GenerationResponse para que el frontend sugiera revisar que todas las filas
-- estén en la presentación. NULL indica que no hubo tablas en imagen (caso normal).

ALTER TABLE generaciones ADD COLUMN tabla_warning TEXT;
