"""
Test script for TaskDecomposerNode
Tests JSON formatting and human-readable summaries
"""
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nodes.task_decomposer_node import TaskDecomposerNode
from core.state import FinanceAgentState, UserProfile, SystemStage, UserState
from langchain_core.messages import HumanMessage

class MockLLM:
    """Mock LLM for testing"""
    def __call__(self, *args, **kwargs):
        return "Mock LLM Response"

def test_task_decomposer():
    """Test task decomposer with various queries"""
    
    # Initialize components
    decomposer = TaskDecomposerNode(MockLLM())
    
    # Test queries from requirements
    test_queries = [
        "Plan my retirement",
        "Help me buy a house",
        # Additional test cases
        "Create a step-by-step plan for early retirement",
        "I want to save $10,000 for a vacation in 2 years",
        "Create a comprehensive financial plan",
        "Optimize my portfolio allocation"
    ]
    
    print("\nRunning TaskDecomposerNode tests...\n")
    
    for query in test_queries:
        print(f"\n--- Testing query: {query} ---")
        
        # Create test state
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
            # Additional required fields
            "response": "",
            "suggestions": [],
            "visualizations": [],  # List of visualization dictionaries
            "should_continue": True,
            "error_message": None,
            "retry_count": 0
        }
        
        # Process query
        try:
            result_state = decomposer(state)
            
            # Validate response structure
            decomposition = result_state["analysis_results"]["task_decomposition"]
            
            # Check required fields
            assert "version" in decomposition, "Missing version field"
            assert "timestamp" in decomposition, "Missing timestamp field"
            assert "plan" in decomposition, "Missing plan field"
            assert "tasks" in decomposition["plan"], "Missing tasks in plan"
            assert "summary" in decomposition["plan"], "Missing human-readable summary"
            
            # Print summary
            print("\nValidation successful!")
            print(f"Number of tasks: {len(decomposition['plan']['tasks'])}")
            print(f"Complexity level: {decomposition['task_analysis']['complexity_level']}")
            print("\nHuman-readable summary excerpt:")
            print("--------------------------------")
            summary_lines = decomposition["plan"]["summary"].split("\n")[:5]
            print("\n".join(summary_lines))
            print("...")
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            raise
            
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_task_decomposer()