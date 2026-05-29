from repositories import user_mutations_repo, user_repo
from schemas.user import ChangePasswordRequest, ProfileResponse, UpdateProfileRequest
from services.auth_service import hash_password, verify_password
from utils.errors import AppError, ErrorCode


async def get_profile(current_user: dict) -> ProfileResponse:
    user = await user_repo.find_by_id(current_user["sub"])
    if not user:
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)
    return ProfileResponse(**user)


async def update_profile(payload: UpdateProfileRequest, current_user: dict) -> ProfileResponse:
    user_id = current_user["sub"]
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)

    fields: dict = {}
    if payload.nombre is not None:
        fields["nombre"] = payload.nombre
    if payload.email is not None:
        email_str = str(payload.email)
        if email_str != user["email"]:
            if await user_repo.find_by_email(email_str):
                raise AppError("El email ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
        fields["email"] = email_str
    if payload.username is not None:
        if payload.username != user.get("username"):
            if await user_repo.find_by_username(payload.username):
                raise AppError("El nombre de usuario ya está en uso.", ErrorCode.USER_ALREADY_EXISTS, 409)
        fields["username"] = payload.username

    if not fields:
        return ProfileResponse(**user)

    updated = await user_mutations_repo.update_profile(user_id, fields)
    return ProfileResponse(**updated)


async def change_password(payload: ChangePasswordRequest, current_user: dict) -> dict:
    user_id = current_user["sub"]
    user = await user_repo.find_by_id(user_id)
    if not user:
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)

    if not verify_password(payload.password_actual, user.get("password_hash", "")):
        raise AppError("Contraseña actual incorrecta.", ErrorCode.INVALID_PASSWORD, 400)

    await user_mutations_repo.update_profile(user_id, {"password_hash": hash_password(payload.password_nueva)})
    return {"message": "Contraseña actualizada correctamente."}
