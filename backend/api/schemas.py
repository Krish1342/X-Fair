from pydantic import BaseModel
from typing import Optional, Dict, Any

# Chat
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: str = "default"
    workflow_stage: str = "Started"

# Auth
class AuthRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

# User data
class Transaction(BaseModel):
    description: str
    amount: float
    date: str
    category: str

class Goal(BaseModel):
    name: str
    target: float
    current: float = 0
    deadline: Optional[str] = None

class Budget(BaseModel):
    category: str
    budgeted: float
    month: str  # YYYY-MM

class RecurringTransaction(BaseModel):
    description: str
    amount: float
    category: str
    start_date: str  # YYYY-MM-DD
    frequency: str = "monthly"  # daily, weekly, monthly, yearly
    interval: int = 1  # every N frequency units
    end_date: Optional[str] = None  # YYYY-MM-DD
    next_date: Optional[str] = None  # YYYY-MM-DD
