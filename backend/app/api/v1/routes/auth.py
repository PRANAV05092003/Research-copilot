import typing
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models import RefreshToken, User, Workspace
from app.schemas.auth import TokenPair, UserCreate, UserLogin, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> typing.Any:
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise AppError(status_code=409, title="Conflict", detail="Email already registered")

    # Create user
    hashed_pw = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_pw, full_name=user_in.full_name)
    db.add(user)
    await db.flush()

    # Create personal workspace
    workspace = Workspace(name="Personal Workspace", owner_id=user.id)
    db.add(workspace)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
async def login(
    user_in: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
) -> typing.Any:
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise AppError(status_code=401, title="Unauthorized", detail="Incorrect email or password")

    # Issue tokens
    ws_result = await db.execute(select(Workspace).where(Workspace.owner_id == user.id))
    workspace = ws_result.scalars().first()
    ws_id = workspace.id if workspace else None

    access_token = create_access_token(subject=user.id, workspace_id=ws_id)
    refresh_token = create_refresh_token()

    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
    db_token = RefreshToken(
        user_id=user.id, token_hash=hash_refresh_token(refresh_token), expires_at=expires_at
    )
    db.add(db_token)
    await db.commit()

    # Set httpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        secure=settings.ENVIRONMENT != "development",
        max_age=settings.REFRESH_TOKEN_TTL_DAYS * 24 * 3600,
        path="/api/v1/auth",
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token_endpoint(
    response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)
) -> typing.Any:
    if not refresh_token:
        raise AppError(status_code=401, title="Unauthorized", detail="Refresh token missing")

    hashed = hash_refresh_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == hashed))
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise AppError(status_code=401, title="Unauthorized", detail="Invalid refresh token")

    if db_token.revoked_at:
        # Replay detection: this token was already used or revoked!
        # Revoke ALL tokens for this user as a security measure
        from sqlalchemy import update

        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == db_token.user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        await db.commit()
        raise AppError(status_code=401, title="Unauthorized", detail="Refresh token revoked")

    if db_token.expires_at < datetime.now(UTC):
        raise AppError(status_code=401, title="Unauthorized", detail="Refresh token expired")

    # Valid token -> rotate
    db_token.revoked_at = datetime.now(UTC)

    # Get user
    user_result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise AppError(status_code=401, title="Unauthorized", detail="User not found or inactive")

    # Issue new tokens
    ws_result = await db.execute(select(Workspace).where(Workspace.owner_id == user.id))
    workspace = ws_result.scalars().first()
    ws_id = workspace.id if workspace else None

    new_access_token = create_access_token(subject=user.id, workspace_id=ws_id)
    new_refresh_token = create_refresh_token()

    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
    new_db_token = RefreshToken(
        user_id=user.id, token_hash=hash_refresh_token(new_refresh_token), expires_at=expires_at
    )
    db.add(new_db_token)
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="strict",
        secure=settings.ENVIRONMENT != "development",
        max_age=settings.REFRESH_TOKEN_TTL_DAYS * 24 * 3600,
        path="/api/v1/auth",
    )

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)
) -> typing.Any:
    if refresh_token:
        hashed = hash_refresh_token(refresh_token)
        result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == hashed))
        db_token = result.scalar_one_or_none()
        if db_token and not db_token.revoked_at:
            db_token.revoked_at = datetime.now(UTC)
            await db.commit()

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        samesite="strict",
        secure=settings.ENVIRONMENT != "development",
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)) -> typing.Any:
    return current_user
