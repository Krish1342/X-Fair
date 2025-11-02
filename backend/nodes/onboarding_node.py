"""
Onboarding Node - Handles user registration, consent, and profile creation
Stage 1: Started -> Onboarding
"""
import logging
from typing import Dict, Any
from core.state import FinanceAgentState, UserProfile, UserState, FinancialIntent

logger = logging.getLogger(__name__)


class OnboardingNode:
    """Handles user onboarding process"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Process onboarding flow"""
        try:
            user_query = state.get("user_query", "").lower()
            user_profile = state.get("user_profile")
            
            # Check if this is an onboarding-related query
            if any(keyword in user_query for keyword in ["start", "begin", "help", "new", "register"]):
                state["intent"] = FinancialIntent.ONBOARDING
                state["confidence_score"] = 0.9
                
                # Create basic user profile if none exists
                if not user_profile:
                    user_profile = UserProfile(
                        user_id="user_" + str(hash(user_query))[:8],
                        stage=UserState.NEW
                    )
                
                # Store consent and basic profile
                user_profile.consent_given = True
                user_profile.stage = UserState.ONBOARDED
                
                state["user_profile"] = user_profile
                state["tools_used"] = ["onboarding"]
                
                # Generate onboarding response
                onboarding_response = """
                Welcome to your Personal Finance Agent! I'm here to help you manage your finances intelligently.
                
                I can help you with:
                • Budget analysis and expense tracking
                • Goal setting and progress monitoring  
                • Investment insights and portfolio analysis
                • Tax planning and optimization
                • Financial health assessments
                • Personalized recommendations
                
                To get started, you can:
                1. Upload your bank statements or transaction data
                2. Ask about your spending patterns
                3. Set financial goals
                4. Get investment advice
                
                What would you like to explore first?
                """
                
                state["response"] = onboarding_response
                state["suggestions"] = [
                    "Analyze my spending patterns",
                    "Help me create a budget",
                    "Set financial goals",
                    "Investment recommendations"
                ]
                
                logger.info("User onboarded successfully")
                
            else:
                # Handle general queries during onboarding
                state["intent"] = FinancialIntent.GENERAL_QUERY
                state["confidence_score"] = 0.7
                state["tools_used"] = ["onboarding"]
                
                general_response = """
                Hi! I'm your Personal Finance Agent. I can help you with all aspects of financial management.
                
                To provide the most helpful assistance, could you tell me what specific financial topic you'd like help with?
                
                For example:
                • "Help me analyze my spending"
                • "I want to create a budget"
                • "Show me investment options"
                • "How can I save for retirement?"
                """
                
                state["response"] = general_response
                state["suggestions"] = [
                    "Analyze spending patterns",
                    "Create a budget plan", 
                    "Investment guidance",
                    "Savings strategies"
                ]
            
            state["current_node"] = "onboarding"
            
        except Exception as e:
            logger.error(f"Onboarding error: {e}")
            state["error_message"] = str(e)
            state["response"] = "I'm here to help with your finances! What would you like to know?"
        
        return state