"""
Simplified LangGraph workflow using direct Groq integration
Clean implementation without HuggingFace dependencies
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from core.groq_client import groq_client


class WorkflowStage(Enum):
    STARTED = "Started"
    MVP = "MVP"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


@dataclass
class FinanceState:
    """Simplified state management for finance workflow"""
    user_id: str
    current_stage: str = WorkflowStage.STARTED.value
    user_query: str = ""
    intent: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    response: str = ""
    tools_used: List[str] = field(default_factory=list)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    next_action: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)


class SimplifiedFinanceWorkflow:
    """Simplified finance workflow using direct Groq integration"""
    
    def __init__(self):
        self.stages = {
            WorkflowStage.STARTED.value: self._handle_started_stage,
            WorkflowStage.MVP.value: self._handle_mvp_stage,
            WorkflowStage.INTERMEDIATE.value: self._handle_intermediate_stage,
            WorkflowStage.ADVANCED.value: self._handle_advanced_stage,
        }
    
    async def run(self, state: FinanceState) -> FinanceState:
        """Run the workflow asynchronously"""
        return self.run_sync(state)
    
    def run_sync(self, state: FinanceState) -> FinanceState:
        """Run the workflow synchronously"""
        
        # Step 1: Classify intent using Groq
        intent_result = groq_client.analyze_financial_query(
            state.user_query, 
            state.context
        )
        
        state.intent = intent_result["intent"]
        state.analysis_results["groq_analysis"] = intent_result
        
        # Step 2: Route to appropriate stage handler
        stage_handler = self.stages.get(state.current_stage, self._handle_started_stage)
        state = stage_handler(state)
        
        # Step 3: Generate final response using Groq
        state = self._generate_response(state)
        
        return state
    
    def _handle_started_stage(self, state: FinanceState) -> FinanceState:
        """Handle Started stage - basic onboarding and simple queries"""
        state.tools_used.append("onboarding_analyzer")
        
        # Simple responses for started stage
        if state.intent == "budget_analysis":
            state.analysis_results["budget_status"] = "Getting started with budget tracking"
            state.next_action = "Consider setting up budget categories"
        elif state.intent == "goal_planning":
            state.analysis_results["goal_status"] = "Ready to set financial goals"
            state.next_action = "Define your primary financial goal"
        else:
            state.analysis_results["general_status"] = "Welcome to your finance journey"
            state.next_action = "Explore basic budgeting features"
        
        return state
    
    def _handle_mvp_stage(self, state: FinanceState) -> FinanceState:
        """Handle MVP stage - basic budgeting and goal planning"""
        state.tools_used.append("budget_analyzer")
        state.tools_used.append("goal_tracker")
        
        # Enhanced analysis for MVP stage
        if state.intent == "budget_analysis":
            state.analysis_results["budget_insights"] = {
                "spending_categories": ["Food", "Transportation", "Entertainment"],
                "recommendations": "Focus on tracking daily expenses",
                "alerts": "Set up spending notifications"
            }
        elif state.intent == "investment_advice":
            state.analysis_results["investment_readiness"] = "Consider basic index funds"
            state.next_action = "Learn about investment basics"
        
        return state
    
    def _handle_intermediate_stage(self, state: FinanceState) -> FinanceState:
        """Handle Intermediate stage - advanced budgeting with AI insights"""
        state.tools_used.append("advanced_budget_analyzer")
        state.tools_used.append("risk_assessor")
        state.tools_used.append("market_analyzer")
        
        # Sophisticated analysis for intermediate users
        if state.intent == "investment_advice":
            state.analysis_results["portfolio_analysis"] = {
                "diversification": "Well-balanced portfolio recommended",
                "risk_level": "Moderate risk tolerance detected",
                "optimization": "Consider rebalancing quarterly"
            }
        elif state.intent == "risk_assessment":
            state.analysis_results["risk_profile"] = {
                "emergency_fund": "3-6 months expenses recommended",
                "insurance_needs": "Evaluate health and life insurance",
                "investment_risk": "Moderate risk tolerance"
            }
        
        return state
    
    def _handle_advanced_stage(self, state: FinanceState) -> FinanceState:
        """Handle Advanced stage - sophisticated portfolio management"""
        state.tools_used.append("portfolio_optimizer")
        state.tools_used.append("tax_analyzer")
        state.tools_used.append("retirement_planner")
        state.tools_used.append("market_intelligence")
        
        # Advanced financial analysis
        if state.intent == "investment_advice":
            state.analysis_results["advanced_portfolio"] = {
                "asset_allocation": "Optimize across multiple asset classes",
                "tax_strategy": "Consider tax-loss harvesting",
                "retirement_planning": "On track for retirement goals",
                "alternative_investments": "Explore REITs and commodities"
            }
        
        return state
    
    def _generate_response(self, state: FinanceState) -> FinanceState:
        """Generate final response using Groq with context"""
        
        # Build context for response generation
        context = {
            "stage": state.current_stage,
            "intent": state.intent,
            "tools_used": state.tools_used,
            "analysis_results": state.analysis_results,
            "user_query": state.user_query
        }
        
        # Create response prompt
        response_prompt = f"""Based on the financial analysis, provide a helpful response to the user.
        
User Query: {state.user_query}
Intent: {state.intent}
Stage: {state.current_stage}
Analysis: {state.analysis_results}

Provide a clear, actionable response that helps the user with their financial query."""
        
        # Get response from Groq
        result = groq_client.analyze_financial_query(response_prompt, context)
        state.response = result["response"]
        
        # Add message to conversation history
        state.messages.extend([
            {"role": "user", "content": state.user_query},
            {"role": "assistant", "content": state.response}
        ])
        
        return state


# Create global workflow instance
finance_workflow = SimplifiedFinanceWorkflow()