"""
LangGraph workflow implementation for the Dynamic Personal Finance Agent
Based on the provided workflow diagram with stages and intelligent routing
"""
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

from core.state import (
    FinanceAgentState, 
    SystemStage, 
    FinancialIntent, 
    UserProfile,
    UserState,
    ToolResult
)
from nodes.onboarding_node import OnboardingNode
from nodes.intent_classifier_node import IntentClassifierNode
from nodes.statement_parser_node import StatementParserNode
from nodes.budget_analyzer_node import BudgetAnalyzerNode
from nodes.goal_planner_node import GoalPlannerNode
from nodes.rag_knowledge_node import RAGKnowledgeNode
from nodes.reasoning_engine_node import ReasoningEngineNode
from nodes.task_decomposer_node import TaskDecomposerNode
from nodes.ml_models_node import MLModelsNode
from nodes.action_executor_node import ActionExecutorNode
from config.settings import settings

logger = logging.getLogger(__name__)


class FinanceWorkflow:
    """Main LangGraph workflow implementation"""
    
    def __init__(self):
        self.groq_llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name="mixtral-8x7b-32768",
            temperature=0.1
        )
        self.setup_nodes()
        self.setup_workflow()
    
    def setup_nodes(self):
        """Initialize all workflow nodes"""
        self.onboarding_node = OnboardingNode(self.groq_llm)
        self.intent_classifier_node = IntentClassifierNode(self.groq_llm)
        self.statement_parser_node = StatementParserNode(self.groq_llm)
        self.budget_analyzer_node = BudgetAnalyzerNode(self.groq_llm)
        self.goal_planner_node = GoalPlannerNode(self.groq_llm)
        self.rag_knowledge_node = RAGKnowledgeNode(self.groq_llm)
        self.reasoning_engine_node = ReasoningEngineNode(self.groq_llm)
        self.task_decomposer_node = TaskDecomposerNode(self.groq_llm)
        self.ml_models_node = MLModelsNode()
        self.action_executor_node = ActionExecutorNode()
    
    def setup_workflow(self):
        """Setup the LangGraph workflow based on the diagram"""
        workflow = StateGraph(FinanceAgentState)
        
        # Add all nodes
        workflow.add_node("determine_stage", self.determine_stage)
        workflow.add_node("onboarding", self.onboarding_node)
        workflow.add_node("intent_classifier", self.intent_classifier_node)
        workflow.add_node("statement_parser", self.statement_parser_node)
        workflow.add_node("budget_analyzer", self.budget_analyzer_node)
        workflow.add_node("goal_planner", self.goal_planner_node)
        workflow.add_node("rag_knowledge", self.rag_knowledge_node)
        workflow.add_node("reasoning_engine_intermediate", self.reasoning_engine_node)
        workflow.add_node("reasoning_engine_advanced", self.reasoning_engine_node)
        workflow.add_node("task_decomposer", self.task_decomposer_node)
        workflow.add_node("ml_models", self.ml_models_node)
        workflow.add_node("action_executor", self.action_executor_node)
        workflow.add_node("generate_response", self.generate_response)
        
        # Set entry point
        workflow.set_entry_point("determine_stage")
        
        # Stage determination routing
        workflow.add_conditional_edges(
            "determine_stage",
            self.route_by_stage,
            {
                "onboarding": "onboarding",
                "mvp": "intent_classifier",
                "intermediate": "intent_classifier", 
                "advanced": "intent_classifier"
            }
        )
        
        # Onboarding flow
        workflow.add_edge("onboarding", "generate_response")
        
        # MVP Stage routing (Stage 1)
        workflow.add_conditional_edges(
            "intent_classifier",
            self.route_by_intent_and_stage,
            {
                # MVP Stage
                "budget_analyzer": "budget_analyzer",
                "goal_planner": "goal_planner",
                "statement_parser": "statement_parser",
                
                # Intermediate Stage  
                "rag_knowledge": "rag_knowledge",
                "reasoning_engine_intermediate": "reasoning_engine_intermediate",
                
                # Advanced Stage
                "task_decomposer": "task_decomposer",
                "reasoning_engine_advanced": "reasoning_engine_advanced",
                
                # Response generation
                "generate_response": "generate_response"
            }
        )
        
        # MVP stage flows
        workflow.add_edge("statement_parser", "budget_analyzer")
        workflow.add_edge("budget_analyzer", "goal_planner")
        workflow.add_edge("goal_planner", "generate_response")
        
        # Intermediate stage flows
        workflow.add_edge("rag_knowledge", "reasoning_engine_intermediate")
        workflow.add_edge("reasoning_engine_intermediate", "generate_response")
        
        # Advanced stage flows
        workflow.add_edge("task_decomposer", "reasoning_engine_advanced")
        workflow.add_edge("reasoning_engine_advanced", "ml_models")
        
        # ML Models conditional routing
        workflow.add_conditional_edges(
            "ml_models",
            self.should_execute_actions,
            {
                "action_executor": "action_executor",
                "generate_response": "generate_response"
            }
        )
        
        workflow.add_edge("action_executor", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Compile the workflow
        self.graph = workflow.compile()
    
    def determine_stage(self, state: FinanceAgentState) -> FinanceAgentState:
        """Determine which stage the user/system is in"""
        user_profile = state.get("user_profile")
        
        if not user_profile or not user_profile.consent_given:
            state["system_stage"] = SystemStage.STARTED
            state["current_node"] = "onboarding"
        elif user_profile.stage == UserState.NEW:
            state["system_stage"] = SystemStage.MVP
            state["current_node"] = "intent_classifier"
        elif len(state.get("financial_data", {})) > 0:
            state["system_stage"] = SystemStage.INTERMEDIATE
            state["current_node"] = "intent_classifier"
        else:
            state["system_stage"] = SystemStage.ADVANCED
            state["current_node"] = "intent_classifier"
        
        logger.info(f"Determined stage: {state['system_stage']}")
        return state
    
    def route_by_stage(self, state: FinanceAgentState) -> str:
        """Route based on system stage"""
        stage = state.get("system_stage", SystemStage.STARTED)
        
        if stage == SystemStage.STARTED:
            return "onboarding"
        else:
            return "mvp" if stage == SystemStage.MVP else stage.value
    
    def route_by_intent_and_stage(self, state: FinanceAgentState) -> str:
        """Route based on intent and current stage"""
        intent = state.get("intent", FinancialIntent.UNKNOWN)
        stage = state.get("system_stage", SystemStage.MVP)
        confidence = state.get("confidence_score", 0.0)
        
        # Low confidence - use general response
        if confidence < 0.6:
            return "generate_response"
        
        # Route based on stage and intent
        if stage == SystemStage.MVP:
            if intent in [FinancialIntent.BUDGETING, FinancialIntent.BASIC_INSIGHTS]:
                return "statement_parser"
            elif intent == FinancialIntent.GOAL_PLANNING:
                return "goal_planner"
            else:
                return "budget_analyzer"
                
        elif stage == SystemStage.INTERMEDIATE:
            if intent in [FinancialIntent.TAX_ANALYSIS, FinancialIntent.MARKET_DATA]:
                return "rag_knowledge"
            else:
                return "reasoning_engine_intermediate"
                
        elif stage == SystemStage.ADVANCED:
            if intent == FinancialIntent.TASK_DECOMPOSITION:
                return "task_decomposer"
            else:
                return "reasoning_engine_advanced"
        
        return "generate_response"
    
    def should_execute_actions(self, state: FinanceAgentState) -> str:
        """Determine if actions should be executed or just suggestions provided"""
        user_profile = state.get("user_profile")
        
        # Only execute if user has given explicit consent and we're in advanced stage
        if (user_profile and 
            user_profile.consent_given and 
            state.get("system_stage") == SystemStage.ADVANCED):
            return "action_executor"
        else:
            return "generate_response"
    
    def generate_response(self, state: FinanceAgentState) -> FinanceAgentState:
        """Generate final response using Groq LLM"""
        try:
            # Collect all analysis results
            analysis_results = state.get("analysis_results", {})
            tools_used = state.get("tools_used", [])
            user_query = state.get("user_query", "")
            
            # Create context for response generation
            context = f"""
            User Query: {user_query}
            Tools Used: {', '.join(tools_used)}
            Analysis Results: {analysis_results}
            System Stage: {state.get('system_stage', 'Unknown')}
            """
            
            # Generate response using Groq
            response_prompt = f"""
            You are an expert personal finance advisor. Based on the analysis below, provide a helpful, 
            clear, and actionable response to the user's financial query.
            
            {context}
            
            Provide a response that:
            1. Directly addresses the user's question
            2. Includes specific insights from the analysis
            3. Offers actionable recommendations
            4. Is conversational and encouraging
            5. Mentions any limitations or assumptions
            """
            
            response = self.groq_llm.invoke([HumanMessage(content=response_prompt)])
            
            state["response"] = response.content
            state["current_node"] = "generate_response"
            
            logger.info("Generated final response")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["response"] = "I apologize, but I encountered an error processing your request. Please try again."
            state["error_message"] = str(e)
        
        return state
    
    async def process_query(self, user_query: str, user_profile: UserProfile = None) -> Dict[str, Any]:
        """Process a user query through the workflow"""
        try:
            # Initialize state
            initial_state = {
                "user_profile": user_profile or UserProfile(user_id="anonymous"),
                "system_stage": SystemStage.STARTED,
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "intent": FinancialIntent.UNKNOWN,
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
            
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "response": final_state.get("response", "I couldn't process your request."),
                "intent": final_state.get("intent", FinancialIntent.UNKNOWN),
                "stage": final_state.get("system_stage", SystemStage.STARTED),
                "tools_used": final_state.get("tools_used", []),
                "analysis_results": final_state.get("analysis_results", {}),
                "suggestions": final_state.get("suggestions", []),
                "visualizations": final_state.get("visualizations", []),
                "error": final_state.get("error_message")
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "intent": FinancialIntent.UNKNOWN,
                "stage": SystemStage.STARTED,
                "tools_used": [],
                "analysis_results": {},
                "suggestions": [],
                "visualizations": [],
                "error": str(e)
            }


# Factory function
def create_finance_workflow() -> FinanceWorkflow:
    """Create and return a configured finance workflow"""
    return FinanceWorkflow()