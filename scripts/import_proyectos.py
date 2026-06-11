"""
import_proyectos.py — importa archivos .mpp a la API de planificación.

Uso:
    IMPORT_EMAIL=admin IMPORT_PASSWORD=secreto python scripts/import_proyectos.py archivo1.mpp archivo2.mpp

Variables de entorno requeridas:
    IMPORT_EMAIL      usuario (campo 'username' en la API)
    IMPORT_PASSWORD   contraseña

Argumentos posicionales:
    uno o más paths absolutos o relativos a archivos .mpp
"""

import os
import sys
import time

import requests

BASE_URL = os.environ.get("IMPORT_BASE_URL", "http://localhost:8000")
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
PROYECTOS_URL = f"{BASE_URL}/api/v1/planificacion"
POLL_INTERVAL = 3   # segundos entre polls
POLL_TIMEOUT = 120  # segundos máximos esperando por proyecto


def _get_credentials() -> tuple[str, str]:
    email = os.environ.get("IMPORT_EMAIL", "").strip()
    password = os.environ.get("IMPORT_PASSWORD", "").strip()
    if not email or not password:
        print("Error: IMPORT_EMAIL e IMPORT_PASSWORD deben estar definidos como variables de entorno.")
        sys.exit(1)
    return email, password


def _login(session: requests.Session, username: str, password: str) -> None:
    resp = session.post(LOGIN_URL, json={"username": username, "password": password}, timeout=15)
    if resp.status_code != 200:
        print(f"Error al autenticarse ({resp.status_code}): {resp.text}")
        sys.exit(1)
    # El access_token queda guardado en session.cookies automáticamente.
    print(f"Autenticado como '{username}'.")


def _importar_archivo(session: requests.Session, path: str) -> dict:
    nombre = os.path.splitext(os.path.basename(path))[0]
    with open(path, "rb") as f:
        resp = session.post(
            PROYECTOS_URL,
            files={"archivo": (os.path.basename(path), f, "application/octet-stream")},
            data={"nombre": nombre, "prioridad": "media"},
            timeout=30,
        )
    if resp.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    return resp.json()


def _poll_hasta_listo(session: requests.Session, proyecto_id: str) -> dict:
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        resp = session.get(f"{PROYECTOS_URL}/{proyecto_id}", timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Error al consultar proyecto {proyecto_id}: HTTP {resp.status_code}")
        data = resp.json()
        if data["estado"] != "procesando":
            return data
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Proyecto {proyecto_id} sigue en 'procesando' después de {POLL_TIMEOUT}s.")


def _validar_archivos(paths: list[str]) -> None:
    errores = []
    for p in paths:
        if not os.path.isfile(p):
            errores.append(f"  No encontrado: {p}")
        elif not p.lower().endswith(".mpp"):
            errores.append(f"  No es .mpp: {p}")
    if errores:
        print("Archivos inválidos:\n" + "\n".join(errores))
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/import_proyectos.py archivo1.mpp [archivo2.mpp ...]")
        sys.exit(1)

    paths = sys.argv[1:]
    _validar_archivos(paths)

    username, password = _get_credentials()

    session = requests.Session()
    _login(session, username, password)

    total = len(paths)
    exitosos = 0
    fallidos = 0

    for i, path in enumerate(paths, 1):
        nombre = os.path.splitext(os.path.basename(path))[0]
        print(f"\n[{i}/{total}] Importando '{nombre}'...")

        try:
            proyecto = _importar_archivo(session, path)
            proyecto_id = proyecto["id"]
            print(f"  Creado con id={proyecto_id}, estado={proyecto['estado']}")

            if proyecto["estado"] == "procesando":
                print(f"  Esperando procesamiento (máx {POLL_TIMEOUT}s)...")
                proyecto = _poll_hasta_listo(session, proyecto_id)

            estado = proyecto["estado"]
            if estado == "listo":
                print(f"  OK  id={proyecto_id}  nombre={proyecto['nombre']}  estado={estado}")
                exitosos += 1
            else:
                detalle = proyecto.get("error_detalle") or "sin detalle"
                print(f"  ERROR  id={proyecto_id}  nombre={proyecto['nombre']}  estado={estado}  detalle={detalle}")
                fallidos += 1

        except (RuntimeError, TimeoutError, OSError) as exc:
            print(f"  FALLA  {exc}")
            fallidos += 1

    print(f"\nResumen: {exitosos} exitosos, {fallidos} fallidos de {total} archivos.")
    sys.exit(0 if fallidos == 0 else 1)


if __name__ == "__main__":
    main()
