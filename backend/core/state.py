"""
Core state management for the Dynamic Personal Finance Agent
"""
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from langchain_core.messages import BaseMessage


class SystemStage(Enum):
    """System stages as defined in the workflow diagram"""
    STARTED = "started"
    INTERMEDIATE = "intermediate" 
    MVP = "mvp"
    ADVANCED = "advanced"


class UserState(Enum):
    """User onboarding states"""
    NEW = "new"
    ONBOARDED = "onboarded"
    ACTIVE = "active"


@dataclass
class UserProfile:
    """User profile information"""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    income: Optional[float] = None
    risk_tolerance: Optional[str] = None
    financial_goals: List[str] = None
    consent_given: bool = False
    stage: UserState = UserState.NEW


class FinanceAgentState(TypedDict):
    """Main state for the finance agent workflow"""
    # User information
    user_profile: UserProfile
    system_stage: SystemStage
    
    # Conversation state
    messages: List[BaseMessage]
    user_query: str
    intent: str
    confidence_score: float
    
    # Context and data
    context: Dict[str, Any]
    financial_data: Dict[str, Any]
    
    # Processing state
    current_node: str
    tools_used: List[str]
    analysis_results: Dict[str, Any]
    
    # Response generation
    response: str
    suggestions: List[str]
    visualizations: List[Dict[str, Any]]
    
    # Workflow control
    should_continue: bool
    error_message: Optional[str]
    retry_count: int


class FinancialIntent(Enum):
    """Financial intents for routing"""
    # Stage 1: MVP
    BUDGETING = "budgeting"
    GOAL_PLANNING = "goal_planning" 
    BASIC_INSIGHTS = "basic_insights"
    
    # Stage 2: Intermediate
    TAX_ANALYSIS = "tax_analysis"
    MARKET_DATA = "market_data"
    PORTFOLIO_TRACKING = "portfolio_tracking"
    
    # Stage 3: Advanced
    TASK_DECOMPOSITION = "task_decomposition"
    ML_FORECASTING = "ml_forecasting"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    AUTOMATED_EXECUTION = "automated_execution"
    
    # General
    ONBOARDING = "onboarding"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


@dataclass
class ToolResult:
    """Result from a financial tool execution"""
    tool_name: str
    success: bool
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]] = None
    suggestions: List[str] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowConfig:
    """Configuration for the workflow execution"""
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_visualizations: bool = True
    enable_suggestions: bool = True
    debug_mode: bool = False