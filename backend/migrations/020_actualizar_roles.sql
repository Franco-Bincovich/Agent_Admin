-- migrations/020_actualizar_roles.sql
-- Migración del modelo de roles a 3 roles fijos: administrador / gerente / lider.
--
-- PORQUÉ:
-- La plataforma pasa de un esquema de cuentas con roles genéricos
-- (editor/viewer/usuario, heredados de las migraciones 001 y 008) a un modelo
-- de una sola empresa con tres roles fijos:
--   - administrador: gestión total (usuarios, roles, todas las tareas).
--   - gerente: dueño de áreas, opera sobre las tareas de sus áreas.
--   - lider: opera sobre las tareas de las áreas de su gerente.
-- Se JUBILAN los roles 'editor', 'viewer' y 'usuario'.
--
-- Además, el rol pasa a ser OBLIGATORIO en cada alta:
--   - Se elimina el DEFAULT 'editor' para forzar asignación explícita del rol
--     en cada INSERT (un alta sin rol debe ser un error consciente, no un editor
--     silencioso).
--   - Se agrega NOT NULL como defensa en profundidad a nivel DB, de modo que la
--     garantía "rol obligatorio" no dependa solo del código de la aplicación.
--
-- ORDEN DE OPERACIONES (crítico — garantiza que ningún CHECK vigente sea violado
-- en ningún paso):
--   1. DROP del CHECK actual  → a partir de acá no hay constraint vigente sobre rol.
--   2. UPDATE de los usuarios  → corren sin CHECK activo, imposible violar nada.
--   3. ADD del CHECK nuevo      → Postgres revalida todas las filas; ya son válidas.
--   4. DROP DEFAULT             → altas futuras deben asignar rol explícitamente.
--   5. SET NOT NULL             → al final, cuando ya no hay (ni pueden quedar) NULLs.

-- 1. Quitar el CHECK viejo. A partir de aquí no hay constraint de rol vigente,
--    por lo que los UPDATE siguientes no pueden violar ninguna restricción.
ALTER TABLE usuarios
DROP CONSTRAINT IF EXISTS usuarios_rol_check;

-- 2. Reasignar los 14 usuarios de producción por email (identificador estable).
--    El seed 'admin@agentadmin.com' NO se toca: ya es 'administrador'.

-- administrador (3 usuarios reales + el seed = 4 en total)
UPDATE usuarios SET rol = 'administrador'
WHERE email IN (
    'jmaurino@serviciosyconsultoria.com',  -- Jorgelina
    'franbincovich@gmail.com',             -- Franco
    'nruolo@gmail.com'                     -- Natalia
);

-- gerente (8 usuarios)
UPDATE usuarios SET rol = 'gerente'
WHERE email IN (
    'hernan.bincovich@gmail.com',          -- Hernan
    'sergio.acland@gmail.com',             -- Sergio
    'msottile@karstec.com.ar',             -- Miguel
    'dsantillan@serviciosyconsultoria.com',-- Daniel
    'gonzalo.figueroa@hotmail.com',        -- Gonzalo
    'mcrespo@serviciosyconsultoria.com',   -- Alejandra
    'lofasoariel@gmail.com',               -- Ariel
    'mbertolotti@serviciosyconsultoria.com'-- Manuel
);

-- lider (2 usuarios)
UPDATE usuarios SET rol = 'lider'
WHERE email IN (
    'mmurina@karstec.com.ar',              -- Jimena
    'mmocciaro@karstec.com.ar'             -- Magali
);

-- 3. Agregar el CHECK nuevo con el conjunto final de roles. Postgres revalida
--    todas las filas existentes al crear el constraint: si quedara alguna fila
--    con un rol viejo sin mapear, este ADD falla a propósito (mejor abortar que
--    dejar datos inconsistentes).
ALTER TABLE usuarios
ADD CONSTRAINT usuarios_rol_check
CHECK (rol IN ('administrador', 'gerente', 'lider'));

-- 4. Quitar el DEFAULT 'editor': las altas futuras deben asignar rol de forma
--    explícita (un INSERT sin rol ahora fallará por el NOT NULL del paso 5).
ALTER TABLE usuarios
ALTER COLUMN rol DROP DEFAULT;

-- 5. Hacer rol obligatorio a nivel DB (defensa en profundidad).
--    SALVAGUARDA: si por algún motivo existiera una fila con rol IS NULL, este
--    SET NOT NULL fallará a propósito y abortará la migración completa (mejor
--    abortar que dejar datos inconsistentes). Tras los UPDATE del paso 2 los 14
--    usuarios tienen rol válido, así que no debería haber NULLs.
ALTER TABLE usuarios
ALTER COLUMN rol SET NOT NULL;

-- VERIFICACIÓN (correr manualmente después de aplicar; reparto esperado:
--   administrador | 4   (3 reales + seed admin@agentadmin.com)
--   gerente       | 8
--   lider         | 2
-- ):
-- SELECT rol, COUNT(*) FROM usuarios GROUP BY rol ORDER BY rol;
