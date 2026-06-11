from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime

from utils.errors import AppError

_NS = "http://schemas.microsoft.com/project"


def parse_xml(file_bytes: bytes) -> dict:
    """
    Parsea un cronograma MSPDI (.xml de Microsoft Project) con xml.etree.ElementTree.

    Sin dependencias externas — solo stdlib. Namespace {http://schemas.microsoft.com/project}
    prefijado en cada tag via _t(). Normalización de outline levels:
      ≤1: descartados como tareas; nivel 1 aporta nombre y fechas del proyecto.
        2: área (→ planificacion_areas). Sin area_id — lo asigna el service.
       3–5: tarea (→ planificacion_tareas). nivel normalizado = outline_level - 2.

    Returns:
        {"proyecto": {nombre, fecha_inicio, fecha_fin}, "areas": [...], "tareas": [...]}

    Raises:
        AppError: MPP_PARSE_ERROR/422 si el XML es inválido o no contiene tareas.
    """
    def _t(tag: str) -> str:
        return f"{{{_NS}}}{tag}"

    def _g(el: ET.Element, tag: str) -> str | None:
        child = el.find(_t(tag))
        return child.text if child is not None else None

    def _date(raw: str | None) -> str | None:
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw).strftime("%Y-%m-%d")
        except ValueError:
            return None

    try:
        root = ET.fromstring(file_bytes)
    except ET.ParseError as exc:
        raise AppError(f"XML inválido: {exc}", "MPP_PARSE_ERROR", 422)

    tasks_el = root.find(_t("Tasks"))
    if tasks_el is None:
        raise AppError("El archivo XML no contiene tareas.", "MPP_PARSE_ERROR", 422)

    pnombre: str = ""
    pini: str | None = None
    pfin: str | None = None
    areas: list[dict] = []
    tareas: list[dict] = []
    cap_wbs: str | None = None

    for task in tasks_el.findall(_t("Task")):
        wbs = _g(task, "WBS") or ""
        lvl_text = _g(task, "OutlineLevel")
        if lvl_text is None:
            continue
        lvl = int(lvl_text)
        name = _g(task, "Name") or ""
        fi = _date(_g(task, "Start"))
        ff = _date(_g(task, "Finish"))
        summ = _g(task, "Summary") == "1"

        if lvl <= 1:
            if lvl == 1:
                pnombre, pini, pfin = name, fi, ff
            continue

        if lvl == 2:
            cap_wbs = wbs
            areas.append({"wbs": wbs, "nombre": name})
            continue

        preds = [_g(pl, "PredecessorUID") for pl in task.findall(_t("PredecessorLink"))]
        predstr = ",".join(filter(None, preds)) or None

        tareas.append({
            "wbs": wbs, "nombre": name, "nivel": lvl - 2,
            "es_resumen": summ, "fecha_inicio": fi, "fecha_fin": ff,
            "fecha_estimada": False, "confianza": "alta",
            "predecesoras": predstr, "cap_wbs": cap_wbs,
        })

    return {
        "proyecto": {"nombre": pnombre, "fecha_inicio": pini, "fecha_fin": pfin},
        "areas": areas,
        "tareas": tareas,
    }
