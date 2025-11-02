"""
Simplified FastAPI server for testing the basic structure
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dynamic Personal Finance Agent API",
    description="LangGraph-based Personal Finance Agent (Test Server)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Dynamic Personal Finance Agent API (Test Server)",
        "version": "2.0.0", 
        "description": "Multi-stage LangGraph workflow with simplified implementation",
        "status": "Running",
        "endpoints": {
            "health": "/health",
            "test_chat": "/api/v1/test-chat",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance-agent-api"}


@app.post("/api/v1/test-chat")
async def test_chat(request: dict):
    """Test chat endpoint that simulates AI responses"""
    user_message = request.get("message", "")
    
    # Simple keyword-based responses for testing
    if "budget" in user_message.lower():
        response = "I can help you analyze your budget. Your spending patterns show you're within your limits for most categories."
    elif "invest" in user_message.lower():
        response = "Investment analysis shows your portfolio is well-diversified. Consider increasing your tech stock allocation."
    elif "goal" in user_message.lower():
        response = "You're making great progress on your savings goal. You're 65% of the way there!"
    else:
        response = f"I received your message: '{user_message}'. The full LangGraph workflow will be available once dependencies are resolved."
    
    return {
        "response": response,
        "intent": "general_inquiry",
        "workflow_stage": "Started",
        "tools_used": ["test_analyzer"],
        "next_action": "Continue exploring financial features"
    }


@app.post("/api/v1/auth/login")
async def test_login(request: dict):
    """Test login endpoint"""
    return {
        "message": "Login successful",
        "user": {
            "id": "demo_user",
            "name": "Demo User",
            "email": request.get("email", "demo@example.com")
        },
        "token": "demo_token_123",
        "workflow_stage": "Started"
    }


@app.post("/api/v1/auth/register")
async def test_register(request: dict):
    """Test registration endpoint"""
    return {
        "message": "Registration successful",
        "user": {
            "id": "new_user",
            "name": request.get("name", "New User"),
            "email": request.get("email", "user@example.com")
        },
        "token": "new_token_123",
        "workflow_stage": "Started"
    }


@app.get("/api/v1/auth/verify")
async def test_verify():
    """Test token verification"""
    return {
        "user": {
            "id": "demo_user",
            "name": "Demo User",
            "email": "demo@example.com"
        },
        "workflow_stage": "Started"
    }


@app.get("/api/v1/dashboard")
async def test_dashboard():
    """Test dashboard data"""
    return {
        "accountBalance": 12450.50,
        "monthlyIncome": 5000,
        "monthlyExpenses": 3200,
        "savingsRate": 36,
        "budgetCategories": [
            {"name": "Food & Dining", "budgeted": 600, "spent": 485, "percentage": 81},
            {"name": "Transportation", "budgeted": 400, "spent": 320, "percentage": 80},
            {"name": "Entertainment", "budgeted": 200, "spent": 150, "percentage": 75},
            {"name": "Shopping", "budgeted": 300, "spent": 380, "percentage": 127}
        ],
        "recentTransactions": [
            {"description": "Coffee Shop", "amount": -4.50, "date": "2025-10-11", "category": "Food & Dining"},
            {"description": "Salary Deposit", "amount": 2500, "date": "2025-10-10", "category": "Income"},
            {"description": "Gas Station", "amount": -45.00, "date": "2025-10-09", "category": "Transportation"},
            {"description": "Online Purchase", "amount": -89.99, "date": "2025-10-08", "category": "Shopping"},
            {"description": "Restaurant", "amount": -67.50, "date": "2025-10-07", "category": "Food & Dining"}
        ],
        "goals": [
            {"name": "Emergency Fund", "target": 10000, "current": 6500, "deadline": "2025-12-31"},
            {"name": "Vacation Fund", "target": 3000, "current": 1200, "deadline": "2025-07-01"},
            {"name": "New Car", "target": 25000, "current": 8500, "deadline": "2026-06-01"}
        ],
        "insights": [
            {"title": "Great Job!", "description": "You stayed under budget in 3 out of 4 categories this month.", "type": "success"},
            {"title": "Shopping Alert", "description": "You've exceeded your shopping budget by 27%. Consider reducing discretionary purchases.", "type": "warning"},
            {"title": "Savings Tip", "description": "Your emergency fund is 65% complete. You're on track to reach your goal by December.", "type": "tip"}
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "simple_test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )