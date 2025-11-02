"""
FastAPI server bootstrap for Dynamic Personal Finance Agent.
Routers under backend/api/routers define all public endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# External integrations and DB boot
from core.groq_client import groq_client
from db.database import Base, engine

# Routers
from api.routers.chat_router import router as chat_router
from api.routers.auth_router import router as legacy_auth_router
from api.routers.transactions_router import router as transactions_router
from api.routers.goals_router import router as goals_router
from api.routers.budgets_router import router as budgets_router
from api.routers.recurring_router import router as recurring_router
from api.routers.workflow_router import router as workflow_router
from api.routers.system_router import router as system_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dynamic Personal Finance Agent API",
    description="LangGraph-based Personal Finance Agent with Groq Integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Create tables if not exist and seed demo data
Base.metadata.create_all(bind=engine)
try:
    from db.seed import seed_demo
    seed_demo()
except Exception as _e:
    logger.warning(f"Seeding skipped or failed: {_e}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(legacy_auth_router, prefix="/api/v1/auth", tags=["auth-legacy"])
app.include_router(system_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(budgets_router, prefix="/api/v1")
app.include_router(recurring_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Dynamic Personal Finance Agent API",
        "version": "2.0.0",
        "groq_status": "Connected" if groq_client.api_key else "API Key Missing",
        "docs": "/docs",
        "api_base": "/api/v1",
    }


@app.get("/health")
async def health_check():
    groq_status = "healthy" if groq_client.api_key else "missing_api_key"
    return {"status": "healthy", "service": "finance-agent-api", "groq_integration": groq_status}


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY not found in environment variables")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
