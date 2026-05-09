-- Usuario de demo para Franco Bincovich y actualización del admin existente.
-- crypt() requiere la extensión pgcrypto (incluida en Supabase por defecto).

INSERT INTO usuarios (nombre, email, username, password_hash, rol, activo)
VALUES (
    'Franco Bincovich',
    'franbincovich@gmail.com',
    'franco',
    crypt('paltron89', gen_salt('bf', 12)),
    'administrador',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

UPDATE usuarios
SET username = 'admin'
WHERE email = 'admin@agentadmin.com';
