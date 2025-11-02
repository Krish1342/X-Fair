"""
Finance Router - Main API endpoints for the Dynamic Personal Finance Agent
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from core.langgraph_workflow import finance_workflow
from core.state import UserProfile, UserState, SystemStage, FinancialIntent

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    stage: str
    tools_used: List[str]
    analysis_results: Dict[str, Any]
    suggestions: List[str]
    visualizations: List[Dict[str, Any]]
    error: Optional[str] = None

class OnboardingRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    income: Optional[float] = None
    risk_tolerance: Optional[str] = None
    financial_goals: Optional[List[str]] = None

class WorkflowStatusResponse(BaseModel):
    user_id: str
    current_stage: str
    available_features: List[str]
    next_steps: List[str]

# Using LangGraph-based workflow instance from core.langgraph_workflow

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Main chat endpoint for interacting with the finance agent
    """
    try:
        # Build initial LangGraph state and run
        user_id = request.user_id or "anonymous"
        # If you want onboarding path on first runs, set consent/profile accordingly
        state = {
            "user_id": user_id,
            "user_query": request.query,
            "current_stage": "started",
            "system_stage": "started",
            "intent": "unknown",
            "context": {},
            "response": "",
            "analysis_results": {},
            "next_action": "",
            "tools_used": [],
            "messages": [],
            "consent_given": True,
            "profile_complete": True,
            "execute_action": False,
            "explanations": [],
        }

        final_state = await finance_workflow.run_async(state)

        return ChatResponse(
            response=str(final_state.get("response", "")),
            intent=str(final_state.get("intent", "unknown")),
            stage=str(final_state.get("current_stage", final_state.get("system_stage", "started"))),
            tools_used=list(final_state.get("tools_used", []) or []),
            analysis_results=dict(final_state.get("analysis_results", {}) or {}),
            suggestions=[],
            visualizations=[],
            error=None,
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/onboarding")
async def complete_onboarding(request: OnboardingRequest):
    """
    Complete user onboarding process
    """
    try:
        # Create user profile
        user_profile = UserProfile(
            user_id=request.user_id,
            name=request.name,
            email=request.email,
            age=request.age,
            income=request.income,
            risk_tolerance=request.risk_tolerance,
            financial_goals=request.financial_goals or [],
            consent_given=True,
            stage=UserState.ONBOARDED
        )
        
        # In real implementation, save to database
        # database.save_user_profile(user_profile)
        
        return {
            "message": "Onboarding completed successfully",
            "user_id": user_profile.user_id,
            "stage": user_profile.stage.value,
            "next_steps": [
                "Start by asking about your spending patterns",
                "Upload transaction data for analysis",
                "Set specific financial goals",
                "Explore investment recommendations"
            ]
        }
        
    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/status/{user_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(user_id: str):
    """
    Get current workflow status for a user
    """
    try:
        # In real implementation, load from database
        user_profile = UserProfile(
            user_id=user_id,
            stage=UserState.ONBOARDED,
            consent_given=True
        )
        
        # Determine current stage and available features
        if user_profile.stage == UserState.NEW:
            current_stage = "started"
            available_features = ["onboarding", "basic_chat"]
            next_steps = ["Complete profile setup", "Provide consent"]
        elif user_profile.stage == UserState.ONBOARDED:
            current_stage = "mvp"
            available_features = [
                "budget_analysis", "goal_planning", "basic_insights",
                "statement_parsing", "expense_tracking"
            ]
            next_steps = [
                "Upload financial data",
                "Set financial goals", 
                "Review spending patterns"
            ]
        else:  # ACTIVE
            current_stage = "advanced"
            available_features = [
                "budget_analysis", "goal_planning", "basic_insights",
                "tax_analysis", "market_data", "portfolio_tracking",
                "task_decomposition", "ml_forecasting", "portfolio_optimization",
                "automated_execution"
            ]
            next_steps = [
                "Review ML insights",
                "Execute recommended actions",
                "Monitor progress"
            ]
        
        return WorkflowStatusResponse(
            user_id=user_id,
            current_stage=current_stage,
            available_features=available_features,
            next_steps=next_steps
        )
        
    except Exception as e:
        logger.error(f"Workflow status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/visualization")
async def get_workflow_visualization():
    """
    Get workflow diagram and structure
    """
    return {
        "workflow_structure": {
            "stages": {
                "started": {
                    "description": "User Input/Upload → Onboarding",
                    "components": ["User Input", "Onboarding", "Consent & Profile Storage"]
                },
                "mvp": {
                    "description": "Intent Classification → Statement Parser → Budget Analyzer → Goal Planner",
                    "components": ["Intent Classifier", "Statement Parser", "Budget Analyzer", "Goal Planner"]
                },
                "intermediate": {
                    "description": "RAG Knowledge Retriever → Reasoning Engine",
                    "components": ["RAG Knowledge Retriever", "Reasoning Engine", "Structured Plans"]
                },
                "advanced": {
                    "description": "Task Decomposer → Reasoning Engine → ML Models → Action Executor",
                    "components": ["Task Decomposer", "Reasoning Engine", "ML Models", "Action Executor"]
                }
            },
            "routing_logic": {
                "stage_determination": "Based on user profile and data availability",
                "intent_classification": "Rule-based + LLM classification using Groq",
                "tool_routing": "Intent and stage-based smart routing"
            }
        },
        "supported_intents": [intent.value for intent in FinancialIntent],
        "system_stages": [stage.value for stage in SystemStage]
    }

@router.get("/tools")
async def get_available_tools():
    """
    Get list of available financial tools and their capabilities
    """
    return {
        "stage_1_mvp": {
            "statement_parser": {
                "description": "Parse CSV/PDF financial statements",
                "input": "Transaction data, bank statements",
                "output": "Categorized transactions, summary statistics"
            },
            "budget_analyzer": {
                "description": "Categorize and compute budget analysis", 
                "input": "Transaction data",
                "output": "Spending patterns, budget alerts, recommendations"
            },
            "goal_planner": {
                "description": "Simple interest calculation and goal tracking",
                "input": "Financial goals, timelines",
                "output": "Savings targets, progress tracking, recommendations"
            }
        },
        "stage_2_intermediate": {
            "rag_knowledge": {
                "description": "Tax docs and FAQs retrieval",
                "input": "Financial questions, tax queries",
                "output": "Relevant knowledge, regulatory information"
            },
            "reasoning_engine": {
                "description": "Planner with structured plans",
                "input": "Financial context, analysis results",
                "output": "Strategic plans, recommendations, insights"
            }
        },
        "stage_3_advanced": {
            "task_decomposer": {
                "description": "Multi-step financial plans",
                "input": "Complex financial objectives",
                "output": "Detailed task breakdowns, execution plans"
            },
            "ml_models": {
                "description": "Expense forecasting, portfolio optimization, risk analysis",
                "input": "Historical data, user preferences",
                "output": "Predictions, optimizations, risk assessments"
            },
            "action_executor": {
                "description": "Automated financial actions (with consent)",
                "input": "Analysis results, user consent",
                "output": "Executed actions, notifications, reports"
            }
        }
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        return {
            "status": "healthy",
            "version": "2.0.0",
            "workflow": "operational",
            "groq_api": "configured",  # Using groq_client inside core.langgraph_workflow
            "timestamp": "2024-01-01T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/examples")
async def get_example_queries():
    """
    Get example queries for different stages
    """
    return {
        "onboarding_examples": [
            "Hello, I'm new to personal finance and need help getting started",
            "Can you help me understand my spending?",
            "I want to start investing but don't know where to begin"
        ],
        "mvp_examples": [
            "Analyze my spending patterns from my bank statement",
            "Help me create a budget for this month",
            "I want to save $10,000 for a vacation in 2 years",
            "Show me where I'm overspending"
        ],
        "intermediate_examples": [
            "What tax deductions am I eligible for?",
            "Explain the current market conditions",
            "How should I diversify my investment portfolio?",
            "Create a comprehensive financial plan"
        ],
        "advanced_examples": [
            "Create a step-by-step plan for early retirement",
            "Predict my expenses for the next year",
            "Optimize my portfolio allocation",
            "Automatically rebalance my investments"
        ]
    }