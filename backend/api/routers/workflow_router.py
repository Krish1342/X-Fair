from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db import models as dbm
from typing import Dict, Any, AsyncGenerator
import json
from core.langgraph_workflow import finance_workflow

router = APIRouter()

@router.get("/workflow/status/{user_id}")
async def get_workflow_status(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.query(dbm.User).filter(dbm.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    has_goals = db.query(dbm.Goal).filter(dbm.Goal.user_id == user_id).count() > 0
    has_budgets = db.query(dbm.Budget).filter(dbm.Budget.user_id == user_id).count() > 0
    has_transactions = db.query(dbm.Transaction).filter(dbm.Transaction.user_id == user_id).count() > 0

    if not (has_goals or has_budgets or has_transactions):
        current_stage = "started"
        next_steps = ["Provide consent", "Set a budget", "Add your first goal"]
    elif not (has_goals and has_budgets):
        current_stage = "mvp"
        next_steps = ["Complete budgets and goals", "Review spending patterns"]
    else:
        current_stage = "intermediate"
        next_steps = ["Explore AI insights", "Plan next actions"]

    return {"user_id": user_id, "current_stage": current_stage, "next_steps": next_steps}

@router.get("/workflow/visualization")
async def get_workflow_visualization():
    """Return a detailed workflow graph definition: stages, nodes, and edges"""
    graph = {
        "stages": [
            {
                "id": "started",
                "label": "Started",
                "nodes": ["onboarding_node", "store_consent_profile"],
            },
            {
                "id": "mvp",
                "label": "MVP",
                "nodes": [
                    "intent_classifier",
                    "statement_parser",
                    "budget_analyzer",
                    "goal_planner",
                    "dashboard_generator",
                ],
            },
            {
                "id": "intermediate",
                "label": "Intermediate",
                "nodes": [
                    "rag_knowledge_retriever",
                    "reasoning_engine",
                    "finance_tools",
                    "notification_sender",
                ],
            },
            {
                "id": "advanced",
                "label": "Advanced",
                "nodes": [
                    "task_decomposer",
                    "reasoning_engine",
                    "ml_models",
                    "action_executor",
                    "continuous_learning",
                ],
            },
        ],
        "nodes": [
            {"id": "system_stage_router", "label": "System Stage Router"},
            {"id": "onboarding_node", "label": "Onboarding"},
            {"id": "store_consent_profile", "label": "Store Consent & Profile"},
            {"id": "intent_classifier", "label": "Intent Classifier"},
            {"id": "statement_parser", "label": "Statement Parser"},
            {"id": "budget_analyzer", "label": "Budget Analyzer"},
            {"id": "goal_planner", "label": "Goal Planner"},
            {"id": "rag_knowledge_retriever", "label": "RAG Knowledge"},
            {"id": "reasoning_engine", "label": "Reasoning Engine"},
            {"id": "finance_tools", "label": "Finance Tools"},
            {"id": "notification_sender", "label": "Notifications"},
            {"id": "task_decomposer", "label": "Task Decomposer"},
            {"id": "ml_models", "label": "ML Models"},
            {"id": "action_executor", "label": "Action Executor"},
            {"id": "dashboard_generator", "label": "Dashboard Generator"},
            {"id": "feedback_collector", "label": "Feedback Collector"},
            {"id": "continuous_learning", "label": "Continuous Learning"},
        ],
        "edges": [
            {"from": "system_stage_router", "to": "onboarding_node", "when": "started"},
            {"from": "system_stage_router", "to": "intent_classifier", "when": "mvp"},
            {"from": "system_stage_router", "to": "rag_knowledge_retriever", "when": "intermediate"},
            {"from": "system_stage_router", "to": "task_decomposer", "when": "advanced"},

            # Started path
            {"from": "onboarding_node", "to": "store_consent_profile"},
            {"from": "store_consent_profile", "to": "intent_classifier"},

            # MVP path
            {"from": "intent_classifier", "to": "statement_parser"},
            {"from": "statement_parser", "to": "budget_analyzer"},
            {"from": "budget_analyzer", "to": "goal_planner"},
            {"from": "goal_planner", "to": "dashboard_generator"},
            {"from": "dashboard_generator", "to": "feedback_collector"},

            # Intermediate path
            {"from": "rag_knowledge_retriever", "to": "reasoning_engine"},
            {"from": "reasoning_engine", "to": "finance_tools"},
            {"from": "finance_tools", "to": "notification_sender"},
            {"from": "notification_sender", "to": "feedback_collector"},

            # Advanced path
            {"from": "task_decomposer", "to": "reasoning_engine"},
            {"from": "reasoning_engine", "to": "ml_models"},
            {"from": "ml_models", "to": "action_executor"},
            {"from": "action_executor", "to": "continuous_learning", "when": "execute"},
            {"from": "action_executor", "to": "feedback_collector", "when": "suggestions_only"},

            # Terminal
            {"from": "continuous_learning", "to": "END"},
            {"from": "feedback_collector", "to": "END"},
        ],
    }
    return {"workflow_structure": graph}


@router.get("/workflow/run/stream")
async def stream_workflow_run(user_id: int, query: str) -> StreamingResponse:
    """Server-Sent Events stream of a workflow run, emitting per-node events"""

    async def event_gen() -> AsyncGenerator[bytes, None]:
        try:
            # Build initial state for the run
            initial_state = {
                "user_id": str(user_id),
                "user_query": query,
                "current_stage": "started",
                "system_stage": "started",
                "intent": "unknown",
                "context": {},
                "response": "",
                "analysis_results": {},
                "next_action": "",
                "tools_used": [],
                "messages": [],
                "consent_given": False,
                "profile_complete": False,
                "execute_action": False,
                "explanations": [],
            }

            async for evt in finance_workflow.stream_trace(initial_state):
                ev_name = (evt.get("event") or "").lower()
                data = evt.get("data") or {}
                # Try to standardize node name for UI highlighting
                node_name = None
                if isinstance(data, dict):
                    node_name = data.get("name") or data.get("node") or data.get("id")
                # LangGraph events often include 'on_node_start'/'on_node_end'
                if node_name and ("node_start" in ev_name or "node_end" in ev_name):
                    data["node"] = node_name

                payload = {"event": ev_name, "data": data}
                line = ("data: " + json.dumps(payload) + "\n\n").encode("utf-8")
                yield line

            # Final done event
            yield b"event: done\n" + b"data: {\"ok\": true}\n\n"
        except Exception as e:
            err = {"event": "error", "data": {"message": str(e)}}
            yield ("data: " + json.dumps(err) + "\n\n").encode("utf-8")

    return StreamingResponse(event_gen(), media_type="text/event-stream")

@router.get("/tools")
async def get_available_tools(db: Session = Depends(get_db)):
    # Derive available tools from DB presence rather than static list
    # If there is data, we expose relevant capabilities
    has_transactions = db.query(dbm.Transaction).count() > 0
    has_budgets = db.query(dbm.Budget).count() > 0
    has_goals = db.query(dbm.Goal).count() > 0
    tools = []
    if has_transactions:
        tools.append("statement_parser")
        tools.append("budget_analyzer")
    if has_budgets:
        tools.append("budget_alerts")
    if has_goals:
        tools.append("goal_planner")
    return {"tools": tools}

@router.get("/examples")
async def get_example_queries(db: Session = Depends(get_db)):
    # Return example prompts conditioned on presence of user data
    has_transactions = db.query(dbm.Transaction).count() > 0
    has_budgets = db.query(dbm.Budget).count() > 0
    has_goals = db.query(dbm.Goal).count() > 0
    examples = []
    if has_transactions:
        examples.append("Summarize my spending over the last month")
        examples.append("Which categories did I overspend in this month?")
    if has_budgets:
        examples.append("How am I tracking against my budgets this month?")
    if has_goals:
        examples.append("Am I on track for my Emergency Fund goal?")
    if not examples:
        examples.append("Help me get started with budgeting and goals")
    return {"examples": examples}
