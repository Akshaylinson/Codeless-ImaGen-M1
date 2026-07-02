from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.config import settings
from ..core.security import create_access_token, get_current_user
from ..database.sqlite import db_session
from ..schemas.auth import LoginRequest, LoginResponse, MeResponse


router = APIRouter(prefix=f"{settings.api_prefix}/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    with db_session() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (payload.username, payload.password),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"user_id": row["id"], "username": row["username"], "role": row["role"]})
    return LoginResponse(
        access_token=token,
        user_id=row["id"],
        username=row["username"],
        role=row["role"],
    )


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/me", response_model=MeResponse)
def me(current_user: dict = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        user_id=int(current_user["user_id"]),
        username=str(current_user["username"]),
        role=str(current_user["role"]),
    )
