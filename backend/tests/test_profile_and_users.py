"""
Tests de gestión de perfil y administración de usuarios.
"""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from services.auth_service import create_access_token, hash_password

_PASSWORD = "TestPass123!"
_USER_ID = str(uuid.uuid4())
_OTHER_USER_ID = str(uuid.uuid4())
_ADMIN_ID = str(uuid.uuid4())
_EMAIL = "test@example.com"

_USER = {
    "id": _USER_ID,
    "nombre": "Test User",
    "email": _EMAIL,
    "username": "testuser",
    "password_hash": hash_password(_PASSWORD),
    "rol": "gerente",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}

_OTHER_USER = {
    "id": _OTHER_USER_ID,
    "nombre": "Otro",
    "email": "otro@example.com",
    "username": "otrouser",
    "password_hash": hash_password(_PASSWORD),
    "rol": "gerente",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}

_ADMIN_USER = {
    "id": _ADMIN_ID,
    "nombre": "Admin",
    "email": "admin@example.com",
    "username": "admin",
    "password_hash": hash_password(_PASSWORD),
    "rol": "administrador",
    "activo": True,
    "creado_en": datetime.utcnow().isoformat(),
}


@pytest.fixture
async def client():
    """Cliente httpx que habla directamente con la app FastAPI sin red real."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ── Perfil ───────────────────────────────────────────────────────────────────


async def test_get_profile_authenticated(client):
    """GET /profile devuelve el perfil del usuario autenticado."""
    token = create_access_token(_USER_ID, "gerente")
    with patch("controllers.profile_controller.user_repo.find_by_id", return_value=_USER):
        resp = await client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == _USER_ID
    assert body["email"] == _EMAIL


async def test_get_profile_without_token(client):
    """GET /profile sin token devuelve 401."""
    resp = await client.get("/api/v1/profile")
    assert resp.status_code == 401
    assert resp.json()["error"] is True


async def test_update_profile_name_success(client):
    """PUT /profile con nombre nuevo devuelve perfil actualizado."""
    token = create_access_token(_USER_ID, "gerente")
    updated = {**_USER, "nombre": "Nombre Actualizado"}
    with patch("controllers.profile_controller.user_repo.find_by_id", return_value=_USER), \
         patch("controllers.profile_controller.user_mutations_repo.update_profile",
               return_value=updated):
        resp = await client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"nombre": "Nombre Actualizado"},
        )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Nombre Actualizado"


async def test_update_profile_empty_name(client):
    """PUT /profile con nombre vacío debe rechazarse con 422 (min_length=2)."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.put(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"nombre": ""},
    )
    assert resp.status_code == 422


async def test_update_profile_invalid_email(client):
    """PUT /profile con email inválido debe rechazarse con 422."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.put(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "no-es-un-email"},
    )
    assert resp.status_code == 422


# ── Administración de usuarios ──────────────────────────────────────────────


async def test_list_users_as_non_admin_forbidden(client):
    """GET /users con un rol no-admin (gerente) devuelve 403."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "FORBIDDEN"


async def test_list_users_as_admin_success(client):
    """GET /users con rol administrador devuelve lista de usuarios con total_generaciones."""
    token = create_access_token(_ADMIN_ID, "administrador")
    with patch("services.user_service.user_repo.find_all", return_value=[_ADMIN_USER, _USER]), \
         patch("services.user_service.find_generaciones", return_value=[]), \
         patch("services.user_service.find_documentos", return_value=[]):
        resp = await client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["total_generaciones"] == 0


async def test_create_user_as_non_admin_forbidden(client):
    """POST /users con un rol no-admin (gerente) devuelve 403 en require_admin."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nombre": "Nuevo",
            "email": "nuevo@example.com",
            "username": "nuevouser",
            "password": "Password123!",
            "rol": "gerente",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


async def test_create_user_as_admin_success(client):
    """POST /users con rol administrador crea el usuario y devuelve 201."""
    token = create_access_token(_ADMIN_ID, "administrador")
    nuevo = {
        "id": str(uuid.uuid4()),
        "nombre": "Nuevo",
        "email": "nuevo@example.com",
        "username": "nuevouser",
        "rol": "gerente",
        "activo": True,
        "creado_en": datetime.utcnow().isoformat(),
    }
    with patch("services.user_service.user_repo.find_by_email", return_value=None), \
         patch("services.user_service.user_repo.find_by_username", return_value=None), \
         patch("services.user_service.user_mutations_repo.create_full", return_value=nuevo):
        resp = await client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nombre": "Nuevo",
                "email": "nuevo@example.com",
                "username": "nuevouser",
                "password": "Password123!",
                "rol": "gerente",
            },
        )
    assert resp.status_code == 201
    assert resp.json()["email"] == "nuevo@example.com"


async def test_patch_active_as_admin_can_modify_any_user(client):
    """PATCH /users/{id}/active con rol admin puede editar cualquier usuario."""
    token = create_access_token(_ADMIN_ID, "administrador")
    updated = {**_USER, "activo": False}
    with patch("services.user_service.user_mutations_repo.update_active",
               return_value=updated):
        resp = await client.patch(
            f"/api/v1/users/{_USER_ID}/active",
            headers={"Authorization": f"Bearer {token}"},
            json={"activo": False},
        )
    assert resp.status_code == 200
    assert resp.json()["activo"] is False


async def test_patch_active_as_non_admin_forbidden(client):
    """PATCH /users/{id}/active con un rol no-admin (gerente) devuelve 403 (DELETE-equivalente)."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.patch(
        f"/api/v1/users/{_OTHER_USER_ID}/active",
        headers={"Authorization": f"Bearer {token}"},
        json={"activo": False},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


async def test_patch_active_as_admin_success(client):
    """PATCH /users/{id}/active con rol admin permite desactivar a otro usuario."""
    token = create_access_token(_ADMIN_ID, "administrador")
    updated = {**_USER, "activo": False}
    with patch("services.user_service.user_mutations_repo.update_active",
               return_value=updated):
        resp = await client.patch(
            f"/api/v1/users/{_USER_ID}/active",
            headers={"Authorization": f"Bearer {token}"},
            json={"activo": False},
        )
    assert resp.status_code == 200


async def test_non_admin_cannot_view_other_user_profile(client):
    """GET /users/{id} de otro usuario con un rol no-admin (gerente) devuelve 404 (ownership)."""
    token = create_access_token(_USER_ID, "gerente")
    with patch("services.user_service.user_repo.find_by_id", return_value=_OTHER_USER):
        resp = await client.get(
            f"/api/v1/users/{_OTHER_USER_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"] is True
    assert body["code"] == "NOT_FOUND"


async def test_delete_user_as_non_admin_forbidden(client):
    """DELETE /users/{id} con un rol no-admin (gerente) → 403."""
    token = create_access_token(_USER_ID, "gerente")
    resp = await client.delete(
        f"/api/v1/users/{_OTHER_USER_ID}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


async def test_delete_user_as_admin_success(client):
    """DELETE /users/{id} con rol admin → 204."""
    token = create_access_token(_ADMIN_ID, "administrador")
    with patch("services.user_service.user_repo.find_by_id", return_value=_USER), \
         patch("services.user_service.user_mutations_repo.delete", return_value=None):
        resp = await client.delete(
            f"/api/v1/users/{_USER_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 204
