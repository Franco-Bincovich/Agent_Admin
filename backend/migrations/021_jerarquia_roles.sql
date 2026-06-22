-- migrations/021_jerarquia_roles.sql
-- Jerarquía del modelo de roles (administrador / gerente / lider, fijado en la 020).
--
-- PORQUÉ:
-- El modelo de permisos de escritura necesita dos vínculos de jerarquía que hasta
-- ahora no existían en la base:
--   A) usuarios.manager_id          → el gerente del que cuelga un lider
--                                      (vínculo usuario↔usuario).
--   B) planificacion_areas.gerente_id → el gerente dueño de un área
--                                      (vínculo usuario↔área), que gobierna qué
--                                      lideres pueden operar sobre sus tareas.
-- Ambas columnas son NULLABLE a propósito:
--   - manager_id es nulo para administrador y gerente (no cuelgan de nadie); solo
--     los lideres apuntan a su gerente.
--   - gerente_id arranca en NULL para TODAS las áreas existentes: las áreas nacen
--     sin dueño y la asignación es manual desde la plataforma (sesión futura, sin
--     UI ni endpoints en esta migración).
--
-- ON DELETE SET NULL en ambas FK es deliberado (mismo patrón que completada_por en
-- la 017): borrar un gerente NO debe borrar a sus lideres ni a sus áreas; estos
-- solo quedan "sin asignar" / "sin dueño".
--
-- NOTA: no se agrega validación "quién puede colgar de quién" a nivel DB; esa
-- regla vive en el código (sesión futura).

-- ─────────────────────────────────────────────────────────────────────────────
-- A) usuarios.manager_id — gerente del que cuelga un lider.
--    Nulo para administrador/gerente (no cuelgan de nadie).
--    ON DELETE SET NULL: si se borra el gerente, sus lideres no se borran; quedan
--    sin asignar.
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS manager_id UUID REFERENCES usuarios(id) ON DELETE SET NULL;

-- Se resuelve en cada request de escritura para chequear permisos de un lider,
-- por eso se indexa.
CREATE INDEX IF NOT EXISTS idx_usuarios_manager_id
    ON usuarios (manager_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- B) planificacion_areas.gerente_id — gerente dueño del área.
--    Gobierna qué lideres pueden operar sobre las tareas del área.
--    Arranca en NULL para todas las filas existentes (asignación manual futura).
--    ON DELETE SET NULL: si se borra el gerente, el área no se borra; queda sin
--    dueño.
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE planificacion_areas
ADD COLUMN IF NOT EXISTS gerente_id UUID REFERENCES usuarios(id) ON DELETE SET NULL;

-- Resolver permisos de escritura sobre tareas exige ubicar el dueño del área,
-- por eso se indexa.
CREATE INDEX IF NOT EXISTS idx_planificacion_areas_gerente_id
    ON planificacion_areas (gerente_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Vínculos líder→gerente ya conocidos. Se resuelven los id por email (estable),
-- nunca por UUID hardcodeado.
--   - Jimena (mmurina@karstec.com.ar)  → Hernan (hernan.bincovich@gmail.com)
--   - Magali (mmocciaro@karstec.com.ar) → Miguel (msottile@karstec.com.ar)
-- gerente_id de las áreas NO se setea aquí: queda todo en NULL.
-- ─────────────────────────────────────────────────────────────────────────────
UPDATE usuarios
SET manager_id = (SELECT id FROM usuarios WHERE email = 'hernan.bincovich@gmail.com')
WHERE email = 'mmurina@karstec.com.ar';

UPDATE usuarios
SET manager_id = (SELECT id FROM usuarios WHERE email = 'msottile@karstec.com.ar')
WHERE email = 'mmocciaro@karstec.com.ar';

-- ─────────────────────────────────────────────────────────────────────────────
-- VERIFICACIÓN (correr manualmente después de aplicar).
--
-- 1. Vínculo líder→gerente legible en una sola fila (self-join por manager_id).
--    Esperado:
--      lider_email              | lider_nombre | manager_email                | manager_nombre
--      mmurina@karstec.com.ar   | Jimena       | hernan.bincovich@gmail.com   | Hernan
--      mmocciaro@karstec.com.ar | Magali       | msottile@karstec.com.ar      | Miguel
--    Si algún manager_email/manager_nombre sale NULL, el email del gerente no
--    matcheó y el vínculo quedó sin setear.
--
-- SELECT l.email  AS lider_email,
--        l.nombre AS lider_nombre,
--        m.email  AS manager_email,
--        m.nombre AS manager_nombre
-- FROM usuarios l
-- LEFT JOIN usuarios m ON m.id = l.manager_id
-- WHERE l.email IN ('mmurina@karstec.com.ar', 'mmocciaro@karstec.com.ar')
-- ORDER BY l.email;
--
-- 2. Áreas con dueño asignado: debe ser 0 tras esta migración.
--
-- SELECT COUNT(*) AS areas_con_gerente
-- FROM planificacion_areas
-- WHERE gerente_id IS NOT NULL;
