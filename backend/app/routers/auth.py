from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas import LoginRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(auth_service.get_db),
):
    user = auth_service.authenticate(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = auth_service.create_access_token(user.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user
