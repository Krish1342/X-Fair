from typing import Optional, Dict, Any
from core.simple_workflow import finance_workflow, FinanceState


class FinanceAgent:
    """Main Finance Agent that uses the simplified Groq-based workflow"""

    def __init__(self):
        self.workflow = finance_workflow

    async def process_query(
        self, user_query: str, user_id: str = "default", context: Optional[Dict[Any, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user financial query through the LangGraph workflow"""
        
        # Initialize state
        initial_state = FinanceState(
            user_id=user_id,
            current_stage="Started",
            user_query=user_query,
            context=context or {},
            messages=[],
            intent="",
            tools_used=[],
            analysis_results={},
            response="",
            next_action=""
        )

        try:
            # Run the workflow
            final_state = await self.workflow.run(initial_state)

            return {
                "response": final_state.response,
                "intent": final_state.intent,
                "tools_used": final_state.tools_used,
                "analysis_results": final_state.analysis_results,
                "workflow_stage": final_state.current_stage,
                "next_action": final_state.next_action
            }

        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "intent": "ERROR",
                "tools_used": [],
                "analysis_results": {},
                "workflow_stage": "Started",
                "next_action": ""
            }

    def process_query_sync(
        self, user_query: str, user_id: str = "default", context: Optional[Dict[Any, Any]] = None
    ) -> Dict[str, Any]:
        """Synchronous version of process_query"""
        
        # Initialize state
        initial_state = FinanceState(
            user_id=user_id,
            current_stage="Started",
            user_query=user_query,
            context=context or {},
            messages=[],
            intent="",
            tools_used=[],
            analysis_results={},
            response="",
            next_action=""
        )

        try:
            # Run the workflow synchronously
            final_state = self.workflow.run_sync(initial_state)

            return {
                "response": final_state.response,
                "intent": final_state.intent,
                "tools_used": final_state.tools_used,
                "analysis_results": final_state.analysis_results,
                "workflow_stage": final_state.current_stage,
                "next_action": final_state.next_action
            }

        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "intent": "ERROR",
                "tools_used": [],
                "analysis_results": {},
                "workflow_stage": "Started",
                "next_action": ""
            }

    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow"""
        return """
        🤖 Advanced Personal Finance Agent Workflow (LangGraph):
        
        ┌─────────────────┐
        │    Started      │ ← Initial onboarding and setup
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │      MVP        │ ← Basic expense tracking
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │ Intermediate    │ ← Smart budgeting with AI
        └─────────┬───────┘
                  │
        ┌─────────▼───────┐
        │   Advanced      │ ← Investment planning & portfolio mgmt
        └─────────────────┘
        
        � Workflow Nodes:
        
        Core Processing:
        • Onboarding Node: User profile setup and initial configuration
        • Intent Classifier: AI-powered intent detection and routing
        • Statement Parser: Financial document processing and extraction
        • Budget Analyzer: Spending analysis and budget optimization
        • Goal Planner: Financial goal setting and tracking
        • RAG Knowledge: Knowledge base integration and retrieval
        • Reasoning Engine: AI-powered financial reasoning and advice
        • Task Decomposer: Complex task breakdown and planning
        • ML Models: Predictive analytics and pattern recognition
        • Action Executor: Automated action execution and follow-up
        
        🎯 Progressive Workflow:
        The system adapts to user's financial sophistication level and 
        provides increasingly sophisticated features as they progress
        through the workflow stages.
        
        🔄 State Management:
        LangGraph maintains comprehensive state including user context,
        conversation history, and cross-node information sharing.
        """


# Factory function to create the agent
def create_finance_agent() -> FinanceAgent:
    """Create and return a configured finance agent"""
    return FinanceAgent()
