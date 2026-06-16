-- migrations/019_add_progreso_reprogramacion_tareas.sql
-- Extiende planificacion_tareas con seguimiento de avance granular y registro
-- de reprogramaciones.
--
-- progreso: escala fija de cinco pasos (0, 25, 50, 75, 100) que reemplaza el
--   seguimiento binario que solo ofrecía completada. Convive con completada para
--   no romper el código existente que ya lo lee: el servicio mantiene ambos
--   sincronizados (completada = progreso == 100). Los pasos fijos evitan entradas
--   arbitrarias sin valor real de negocio y simplifican la lógica del frontend.
--
-- reprogramada: marca histórica e irreversible — la primera vez que las fechas de
--   una tarea cambian respecto al plan importado, el campo se pone en TRUE y no
--   vuelve a FALSE. El frontend la usa para pintar un borde diferenciado sin
--   necesidad de comparar fechas en cada render.
--
-- fecha_inicio_original / fecha_fin_original: capturan las fechas del cronograma
--   base (las que vinieron del archivo importado) antes de cualquier reprogramación.
--   Se llenan solo la primera vez que se reprograma una tarea; en reprogramaciones
--   posteriores no se tocan, preservando siempre la referencia al plan original.
--
-- No se agrega RLS: las policies existentes de planificacion_tareas cubren
-- automáticamente las columnas nuevas.

ALTER TABLE planificacion_tareas
    ADD COLUMN IF NOT EXISTS progreso INTEGER NOT NULL DEFAULT 0
        CHECK (progreso IN (0, 25, 50, 75, 100));

ALTER TABLE planificacion_tareas
    ADD COLUMN IF NOT EXISTS reprogramada BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE planificacion_tareas
    ADD COLUMN IF NOT EXISTS fecha_inicio_original DATE;

ALTER TABLE planificacion_tareas
    ADD COLUMN IF NOT EXISTS fecha_fin_original DATE;

-- Sincroniza progreso con el estado completada ya registrado antes de esta migración.
-- Las tareas que el usuario marcó como completadas reciben progreso = 100;
-- el resto queda en 0, que es el default de la columna nueva.
UPDATE planificacion_tareas
    SET progreso = 100
    WHERE completada = TRUE;
