import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()


class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./finance_agent.db")

    # Application
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    api_host: str = os.getenv("API_HOST", "localhost")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Paths
    data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")
    transactions_file: str = os.path.join(data_dir, "transactions.csv")
    investments_file: str = os.path.join(data_dir, "investments.json")
    goals_file: str = os.path.join(data_dir, "goals.json")
    budget_file: str = os.path.join(data_dir, "budget.json")

    class Config:
        env_file = ".env"


settings = Settings()
