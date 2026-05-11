-- migrations/008_add_usuario_rol.sql
-- Agrega 'usuario' al check constraint de rol

ALTER TABLE usuarios
DROP CONSTRAINT IF EXISTS usuarios_rol_check;

ALTER TABLE usuarios
ADD CONSTRAINT usuarios_rol_check
CHECK (rol IN ('administrador', 'editor', 'viewer', 'usuario'));
