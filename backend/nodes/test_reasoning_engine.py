"""
Test script for ReasoningEngineNode
Tests context extraction, fallback responses, and health score recommendations
"""
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nodes.reasoning_engine_node import ReasoningEngineNode
from core.state import FinanceAgentState, SystemStage, UserProfile
from langchain_core.messages import HumanMessage

class MockLLM:
    """Mock LLM for testing"""
    def __call__(self, *args, **kwargs):
        return "Mock LLM Response"

def create_test_state(query: str, include_data: bool = True) -> FinanceAgentState:
    """Create a test state with optional data"""
    state: FinanceAgentState = {
        "user_profile": UserProfile(user_id="test_user"),
        "system_stage": SystemStage.ADVANCED,
        "messages": [HumanMessage(content=query)],
        "user_query": query,
        "intent": "financial_planning",
        "confidence_score": 0.9,
        "context": {},
        "financial_data": {},
        "current_node": "",
        "tools_used": [],
        "analysis_results": {},
        "response": "",
        "suggestions": [],
        "visualizations": [],
        "should_continue": True,
        "error_message": None,
        "retry_count": 0
    }
    
    if include_data:
        # Add sample financial data
        state["analysis_results"] = {
            "budget_analysis": {
                "total_income": 5000,
                "total_expenses": 3500,
                "category_totals": {
                    "Housing": 1500,
                    "Food": 500,
                    "Transportation": 300,
                    "Investment": 800
                },
                "category_percentages": {
                    "Housing": 30,
                    "Food": 10,
                    "Transportation": 6,
                    "Investment": 16
                },
                "discretionary_spending": 700,
                "fixed_expenses": 2800
            },
            "goals_analysis": {
                "goals": [
                    {"name": "Emergency Fund", "target": 15000},
                    {"name": "House Down Payment", "target": 50000}
                ],
                "total_monthly_required": 1000
            }
        }
    
    return state

def test_reasoning_engine():
    """Test reasoning engine functionality"""
    engine = ReasoningEngineNode(MockLLM())
    
    print("\nRunning ReasoningEngineNode tests...\n")
    
    # Test 1: Normal operation with data
    print("Test 1: Testing with complete financial data")
    state = create_test_state("Help me plan my investments")
    result = engine(state)
    reasoning = result["analysis_results"]["reasoning_analysis"]
    
    assert "context_analysis" in reasoning, "Missing context analysis"
    assert "health_based_recommendations" in reasoning, "Missing health-based recommendations"
    print("✅ Context extraction and recommendations working")
    
    # Test 2: Fallback response
    print("\nTest 2: Testing fallback response (no data)")
    empty_state = create_test_state("What should I do with my money?", include_data=False)
    empty_result = engine(empty_state)
    fallback = empty_result["analysis_results"]["reasoning_analysis"]
    
    assert fallback["status"] == "fallback", "Fallback response not triggered"
    assert "basic_recommendations" in fallback, "Missing basic recommendations"
    print("✅ Fallback response working")
    
    # Test 3: Health score recommendations
    print("\nTest 3: Testing health score-based recommendations")
    health_scores = [25, 45, 75, 90]
    
    for score in health_scores:
        state = create_test_state(f"Analyze my finances with health score {score}")
        state["analysis_results"]["budget_analysis"]["health_score"] = score
        result = engine(state)
        recommendations = result["analysis_results"]["reasoning_analysis"]["health_based_recommendations"]
        
        assert len(recommendations) > 0, f"No recommendations for health score {score}"
        print(f"✅ Generated recommendations for health score {score}")
    
    print("\nAll tests completed successfully! 🎉")

if __name__ == "__main__":
    test_reasoning_engine()