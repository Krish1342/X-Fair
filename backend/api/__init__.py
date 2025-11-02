from fastapi import APIRouter

# Minimal package init to avoid circular/broken imports during app startup.
# Routers are mounted directly in main.py.
router = APIRouter()

__all__ = ["router"]