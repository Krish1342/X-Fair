from typing import Optional
from datetime import date, datetime, timedelta
import hashlib
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Header
from db import models as dbm
from db.database import SessionLocal

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def safe_uid(user_id: str) -> int:
    try:
        return int(user_id)
    except Exception:
        h = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
        return int(h[:8], 16)

def get_user_or_404(db: Session, uid: int) -> dbm.User:
    user = db.query(dbm.User).filter(dbm.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> dbm.User:
    """Get current authenticated user - simplified for testing"""
    # For testing purposes, create or get a default user
    # In production, this would parse JWT tokens and validate authentication
    
    # Try to get user with ID 1, or create if doesn't exist
    user = db.query(dbm.User).filter(dbm.User.id == 1).first()
    
    if not user:
        # Create default test user
        user = dbm.User(
            id=1,
            email="test@example.com",
            name="Test User",
            password_hash=hash_password("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

# Date helpers for recurring

def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date(y, m, day)

def advance(d: date, frequency: str, interval: int) -> date:
    if frequency == "daily":
        return d + timedelta(days=interval)
    if frequency == "weekly":
        return d + timedelta(weeks=interval)
    if frequency == "monthly":
        return add_months(d, interval)
    if frequency == "yearly":
        return add_months(d, interval * 12)
    return add_months(d, interval)
