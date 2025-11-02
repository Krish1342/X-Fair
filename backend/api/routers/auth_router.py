"""
Auth Router - DB-backed authentication endpoints (login/register/verify)
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from db import models as dbm
from api.deps import verify_password, hash_password

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(dbm.User).filter(dbm.User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = f"token_{user.id}"
        return {
            "message": "Login successful",
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "token": token,
            "workflow_stage": "Started",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        existing = db.query(dbm.User).filter(dbm.User.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user = dbm.User(
            email=request.email,
            name=request.name or request.email.split("@")[0].title(),
            password_hash=hash_password(request.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = f"token_{user.id}"
        return {
            "message": "Registration successful",
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "token": token,
            "workflow_stage": "Started",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.get("/verify")
async def verify_token(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    try:
        token: Optional[str] = None
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise HTTPException(status_code=401, detail="Missing token")

        if not token.startswith("token_"):
            raise HTTPException(status_code=401, detail="Invalid token format")

        id_part = token.split("_", 1)[1]
        try:
            uid = int(id_part)
        except Exception:
            # Non-integer token id
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user = db.query(dbm.User).filter(dbm.User.id == uid).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return {"user": {"id": user.id, "name": user.name, "email": user.email}, "workflow_stage": "Started"}
    except HTTPException:
        # Bubble up intended auth errors
        raise
    except Exception as e:
        logger.error(f"Verify error: {e}")
        # Default to unauthorized on unexpected errors during verification
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}