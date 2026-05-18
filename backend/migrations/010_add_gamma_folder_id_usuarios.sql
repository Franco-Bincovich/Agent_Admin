-- migrations/010_add_gamma_folder_id_usuarios.sql
-- Agrega gamma_folder_id a usuarios para cachear el ID de carpeta Gamma por usuario.
-- Nullable: los usuarios existentes no tienen carpeta asignada hasta su próxima generación.
-- El valor se resuelve en runtime (busca por email en la API de Gamma) y se cachea aquí
-- para evitar llamadas repetidas al endpoint GET /v1.0/folders en cada generación.

ALTER TABLE usuarios ADD COLUMN gamma_folder_id TEXT;
