"""
Test script for IntentClassifierNode
Tests confidence threshold adjustment and logging
"""
import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nodes.intent_classifier_node import IntentClassifierNode
from core.state import FinanceAgentState, SystemStage, UserProfile, UserState

class MockLLM:
    """Mock LLM for testing"""
    def __call__(self, *args, **kwargs):
        return "Mock LLM Response"

def create_test_state(query: str, is_demo: bool = False) -> FinanceAgentState:
    """Create a test state with optional demo user"""
    email = "demo@example.com" if is_demo else "user@example.com"
    
    return {
        "user_profile": UserProfile(
            user_id="test_user",
            email=email,
            stage=UserState.ACTIVE
        ),
        "system_stage": SystemStage.ADVANCED,
        "messages": [],
        "user_query": query,
        "intent": "",
        "confidence_score": 0.0,
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

def test_intent_classifier():
    """Test intent classifier functionality"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    classifier = IntentClassifierNode(MockLLM())
    
    print("\nRunning IntentClassifierNode tests...\n")
    
    # Test cases
    test_cases = [
        # Clear intent cases
        ("Help me create a budget", True),
        ("I want to save for retirement", False),
        # Ambiguous cases
        ("Show me my money", True),
        ("What should I do?", False),
        # Edge cases
        ("", True),
        ("Hello", False)
    ]
    
    for query, is_demo in test_cases:
        print(f"\nTesting query: '{query}' (Demo user: {is_demo})")
        state = create_test_state(query, is_demo)
        result = classifier(state)
        
        # Verify results
        assert "intent" in result, "Missing intent in result"
        assert "confidence_score" in result, "Missing confidence score"
        
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence_score']:.2f}")
        
        # Verify demo user threshold
        if is_demo:
            assert result["confidence_score"] >= 0.5 or result["intent"] == "unknown", \
                "Demo user confidence threshold not applied"
    
    print("\nAll tests completed successfully! 🎉")

if __name__ == "__main__":
    test_intent_classifier()