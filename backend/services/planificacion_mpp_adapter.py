from __future__ import annotations

import asyncio
import glob
import os
import tempfile
from pathlib import Path

from services.planificacion_xml_adapter import parse_xml as _parse_xml
from utils.errors import AppError
from utils.logger import log


def _normalize(raw_tasks: list[dict]) -> dict:
    """Aplica la normalización de outline levels al resultado raw del sandbox MPXJ."""
    def _ds(raw: str | None) -> str | None:
        # Toma los primeros 10 chars de "YYYY-MM-DDTHH:MM:SS" → "YYYY-MM-DD"
        return raw[:10] if raw else None

    pnombre: str = ""
    pini: str | None = None
    pfin: str | None = None
    areas: list[dict] = []
    tareas: list[dict] = []
    cap_wbs: str | None = None

    for t in raw_tasks:
        lvl = int(t.get("nivel_outline", 0))
        wbs = t.get("wbs", "")
        name = t.get("nombre", "")
        fi = _ds(t.get("inicio"))
        ff = _ds(t.get("fin"))

        if lvl <= 1:
            if lvl == 1:
                pnombre, pini, pfin = name, fi, ff
            continue

        if lvl == 2:
            cap_wbs = wbs
            areas.append({"wbs": wbs, "nombre": name})
            continue

        tareas.append({
            "wbs": wbs, "nombre": name, "nivel": lvl - 2,
            "es_resumen": bool(t.get("es_resumen")), "fecha_inicio": fi, "fecha_fin": ff,
            "fecha_estimada": False, "confianza": "alta",
            "predecesoras": t.get("predecesoras"), "cap_wbs": cap_wbs,
        })

    return {
        "proyecto": {"nombre": pnombre, "fecha_inicio": pini, "fecha_fin": pfin},
        "areas": areas,
        "tareas": tareas,
    }


def _run_mpxj_sync(file_bytes: bytes) -> list[dict]:
    """Parsea un .mpp con MPXJ/JPype en el hilo actual (operación síncrona/bloqueante)."""
    import jpype
    import jpype.imports
    import mpxj as _mpxj_mod

    mpxj_dir = str(Path(_mpxj_mod.__file__).parent)
    jars = glob.glob(f"{mpxj_dir}/**/*.jar", recursive=True)
    if not jars:
        raise AppError("No se encontraron JARs de mpxj.", "MPP_EXECUTION_ERROR", 502)

    try:
        jvm_path = jpype.getDefaultJVMPath()
    except Exception:
        raise AppError(
            "El formato .mpp requiere Java instalado. Exportá el archivo como .xml desde MS Project e importalo nuevamente.",
            "MPP_JAVA_NOT_AVAILABLE",
            422,
        )

    if not jpype.isJVMStarted():
        jpype.startJVM(
            jvm_path,
            f"-Djava.class.path={os.pathsep.join(jars)}",
            convertStrings=False,
        )

    from jpype import JClass
    UniversalProjectReader = JClass("net.sf.mpxj.reader.UniversalProjectReader")

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mpp", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        project = UniversalProjectReader().read(tmp_path)
        tasks: list[dict] = []
        for t in project.getTasks():
            lvl = t.getOutlineLevel()
            if lvl is None:
                continue
            pred_ids = []
            preds = t.getPredecessors()
            if preds:
                for rel in preds:
                    try:
                        pred_ids.append(str(rel.getPredecessorTask().getID()))
                    except Exception:
                        pass
            tasks.append({
                "wbs": str(t.getWBS() or ""),
                "nivel_outline": int(lvl),
                "nombre": str(t.getName() or ""),
                "es_resumen": bool(t.getSummary()),
                "inicio": str(t.getStart())[:10] if t.getStart() else None,
                "fin": str(t.getFinish())[:10] if t.getFinish() else None,
                "predecesoras": ",".join(pred_ids) if pred_ids else None,
            })
        return tasks
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


async def _parse_mpp(file_bytes: bytes) -> dict:
    """
    Parsea un .mpp localmente con JPype + MPXJ (Java en proceso).

    Escribe los bytes a un tempfile, arranca la JVM con los JARs bundleados del
    paquete mpxj (si aún no está corriendo) y usa UniversalProjectReader para
    extraer las tareas. El trabajo Java es síncrono y corre en un thread separado
    para no bloquear el event loop.

    Raises:
        AppError: MPP_EXECUTION_ERROR/502 si la JVM falla o MPXJ no puede parsear el archivo.
    """
    try:
        raw_tasks = await asyncio.to_thread(_run_mpxj_sync, file_bytes)
        return _normalize(raw_tasks)
    except AppError:
        raise
    except Exception as exc:
        log.error(f"mpp.error | {exc}")
        raise AppError(f"Error parseando MPP con MPXJ: {exc}", "MPP_EXECUTION_ERROR", 502)


async def parse_cronograma(filename: str, file_bytes: bytes) -> dict:
    """
    Detecta la estrategia de parseo por extensión y retorna el cronograma normalizado.

    .xml → _parse_xml (síncrona, stdlib, sin Java): envuelta en asyncio.to_thread
           para no bloquear el event loop — ElementTree es CPU-bound y no es async.
    .mpp → _parse_mpp (async, JPype+MPXJ local): corre el parsing Java en un thread
           separado vía asyncio.to_thread para no bloquear el event loop.

    Returns:
        {"proyecto": {nombre, fecha_inicio, fecha_fin},
         "areas": [{wbs, nombre}, ...],
         "tareas": [{wbs, nombre, nivel, es_resumen, fecha_inicio, fecha_fin,
                     fecha_estimada, confianza, predecesoras, cap_wbs}, ...]}

    Raises:
        AppError: MPP_UNSUPPORTED_FORMAT/400 si la extensión no es .xml ni .mpp.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".xml":
        return await asyncio.to_thread(_parse_xml, file_bytes)
    if ext == ".mpp":
        return await _parse_mpp(file_bytes)
    raise AppError(
        f"Formato no soportado: '{ext}'. Formatos válidos: .xml, .mpp.",
        "MPP_UNSUPPORTED_FORMAT",
        400,
    )
