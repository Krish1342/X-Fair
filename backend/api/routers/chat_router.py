import os
import json
from typing import Dict, List, TypedDict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc, func, and_
from groq import Groq

from api.deps import get_current_user
from db.models import User, Transaction, Budget, Goal, RecurringTransaction
from db.database import SessionLocal

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define state for LangGraph
class FinanceChatState(TypedDict):
    messages: List[Dict[str, str]]
    user_id: int
    user_data: Dict[str, Any]
    context: Dict[str, Any]
    response: str

# Simple chat memory storage
chat_memory: Dict[int, List[Dict]] = {}
MAX_CHAT_HISTORY = 10

class ChatRequest(BaseModel):
    # Keep emp_id for frontend compatibility; also accept user_id
    emp_id: str | None = None
    user_id: int | None = None
    message: str
# --- Utility: simple category normalization and NLP-assisted action extraction ---

CATEGORY_MAP = {
    # Food related
    "dining": "Food & Dining",
    "food": "Food & Dining",
    "groceries": "Food & Dining",
    "grocery": "Food & Dining",
    "coffee": "Food & Dining",
    # Transportation
    "gas": "Transportation",
    "fuel": "Transportation",
    "uber": "Transportation",
    "lyft": "Transportation",
    "car": "Transportation",
    # Housing/Utilities
    "rent": "Housing",
    "mortgage": "Housing",
    "electric": "Utilities",
    "electricity": "Utilities",
    "power": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",
    # Entertainment and others
    "netflix": "Entertainment",
    "entertainment": "Entertainment",
    "shopping": "Shopping",
    "utilities": "Utilities",
    "transportation": "Transportation",
    "housing": "Housing",
    "savings": "Savings",
    "health": "Health & Fitness",
    "fitness": "Health & Fitness",
    "health & fitness": "Health & Fitness",
}

def normalize_category(cat: Optional[str]) -> Optional[str]:
    if not cat:
        return cat
    key = str(cat).strip().lower()
    return CATEGORY_MAP.get(key, cat)


def extract_action_from_message(message: str) -> Optional[Dict[str, Any]]:
    """Use LLM to extract a structured action from a natural language command.
    Returns a dict like {"action": str, "params": {...}} or None.
    Supported actions: add_transaction (expense/income), add_budget, update_budget, add_goal, update_goal, add_recurring
    """
    try:
        system = (
            "You are a parser. Return ONLY strict JSON with keys action and params.\n"
            "- Supported actions: add_transaction, add_budget, update_budget, add_goal, update_goal, add_recurring\n"
            "- For expenses, set amount negative.\n"
            "- Dates must be in YYYY-MM-DD. If 'today' is implied, use today's date.\n"
            "- For add_budget, require category, budgeted (number), and month (YYYY-MM). If month missing, use current month.\n"
            "- For add_transaction, require description (short), amount (number), category, date. Infer category from text if possible.\n"
            "- For update_goal, include id or name (if id not given), and any fields to change: target, current, deadline (YYYY-MM-DD).\n"
            "- If no clear actionable intent, return {\"action\": \"none\", \"params\": {}}."
        )
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        user = (
            f"Today: {today}. Current month: {current_month}."
        )
        resp = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user + "\nCommand: " + message},
            ],
            model="openai/gpt-oss-20b",
            max_tokens=300,
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        # Attempt to find JSON in content
        text = content.strip()
        if text.startswith("`"):
            text = text.strip("`")
        try:
            data = json.loads(text)
        except Exception:
            # Try to extract JSON block
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                data = json.loads(text[start : end + 1])
            else:
                return None
        if not isinstance(data, dict):
            return None
        action = str(data.get("action") or "none").lower()
        params = data.get("params") or {}
        if action == "none":
            return None
        # Normalize category and dates
        if action == "add_transaction":
            params["category"] = normalize_category(params.get("category"))
            # If message implies expense, ensure negative amount
            amt = params.get("amount")
            if amt is not None:
                try:
                    a = float(amt)
                    # If text suggests expense keywords, force negative
                    if any(k in message.lower() for k in ["expense", "spend", "paid", "dining", "bought", "purchase", "spent"]):
                        a = -abs(a)
                    params["amount"] = a
                except Exception:
                    pass
            if not params.get("date"):
                params["date"] = today
            if not params.get("description"):
                params["description"] = "Transaction"
        if action == "add_budget":
            if not params.get("month"):
                params["month"] = current_month
            if params.get("category"):
                params["category"] = normalize_category(params.get("category"))
        if action == "update_budget":
            if params.get("category"):
                params["category"] = normalize_category(params.get("category"))
            # Default to current month if month not provided
            if not params.get("month"):
                params["month"] = datetime.now().strftime("%Y-%m")
        if action in ("add_goal", "update_goal"):
            # Normalize deadline
            if params.get("deadline") and len(params["deadline"]) == 7:
                # Convert YYYY-MM to last day of month if needed
                try:
                    params["deadline"] = params["deadline"] + "-28"
                except Exception:
                    pass
        return {"action": action, "params": params}
    except Exception as e:
        print("extract_action_from_message error:", e)
        return None


# --- Action execution utilities ---

def run_action(db: Session, uid: int, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a supported action. Returns a result dict with status and item.
    Shared by chat and /chat/execute endpoint.
    """
    action = (action or "").lower()
    result: Dict[str, Any] = {"action": action, "user_id": uid}

    if action == "add_budget":
        category = params.get("category")
        budgeted = float(params.get("budgeted", 0) or 0)
        month = params.get("month")
        if not category or not month:
            raise HTTPException(status_code=400, detail="Missing category or month")
        row = Budget(user_id=uid, category=category, budgeted=budgeted, month=month)
        db.add(row)
        try:
            db.commit(); db.refresh(row)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Budget already exists for this category and month")
        result.update({"status": "ok", "item": {"id": row.id, "category": row.category, "budgeted": row.budgeted, "month": row.month}})

    elif action == "update_budget":
        item_id = params.get("id")
        category = params.get("category")
        month = params.get("month")
        budgeted = params.get("budgeted")
        if item_id:
            q = db.query(Budget).filter(Budget.user_id == uid, Budget.id == int(item_id))
        elif category and month:
            # Case-insensitive match on category to be user-friendly
            q = db.query(Budget).filter(
                Budget.user_id == uid,
                func.lower(Budget.category) == (category or "").lower(),
                Budget.month == month,
            )
        else:
            raise HTTPException(status_code=400, detail="Provide id or (category, month)")
        row = q.first()
        if not row:
            raise HTTPException(status_code=404, detail="Budget not found")
        if category:
            row.category = category
        if month:
            row.month = month
        if budgeted is not None:
            try:
                row.budgeted = float(budgeted)
            except Exception:
                pass
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Budget conflict")
        result.update({"status": "ok", "item": {"id": row.id, "category": row.category, "budgeted": row.budgeted, "month": row.month}})

    elif action == "add_goal":
        name = params.get("name") or "New Goal"
        target = float(params.get("target", 0) or 0)
        current = float(params.get("current", 0) or 0)
        deadline = params.get("deadline")
        d = None
        if deadline:
            try:
                d = datetime.fromisoformat(deadline).date()
            except Exception:
                d = None
        row = Goal(user_id=uid, name=name, target=target, current=current, deadline=d)
        db.add(row); db.commit(); db.refresh(row)
        result.update({"status": "ok", "item": {"id": row.id, "name": row.name, "target": row.target, "current": row.current, "deadline": row.deadline.isoformat() if row.deadline else None}})

    elif action == "update_goal":
        item_id = params.get("id")
        name = params.get("name")
        q = None
        if item_id:
            q = db.query(Goal).filter(Goal.user_id == uid, Goal.id == int(item_id))
        elif name:
            q = db.query(Goal).filter(Goal.user_id == uid, Goal.name == name)
        else:
            raise HTTPException(status_code=400, detail="Provide goal id or name")
        row = q.first()
        if not row:
            raise HTTPException(status_code=404, detail="Goal not found")
        if params.get("name") is not None:
            row.name = params.get("name")
        if params.get("target") is not None:
            try:
                row.target = float(params.get("target"))
            except Exception:
                pass
        if params.get("current") is not None:
            try:
                row.current = float(params.get("current"))
            except Exception:
                pass
        if params.get("deadline"):
            try:
                row.deadline = datetime.fromisoformat(params.get("deadline")).date()
            except Exception:
                pass
        db.commit(); db.refresh(row)
        result.update({"status": "ok", "item": {"id": row.id, "name": row.name, "target": row.target, "current": row.current, "deadline": row.deadline.isoformat() if row.deadline else None}})

    elif action == "add_transaction":
        description = params.get("description", "AI Transaction")
        amount = float(params.get("amount", 0) or 0)
        category = params.get("category")
        date_str = params.get("date")
        d = datetime.now().date()
        if date_str:
            try:
                d = datetime.fromisoformat(date_str).date()
            except Exception:
                pass
        row = Transaction(user_id=uid, description=description, amount=amount, date=d, category=category)
        db.add(row); db.commit(); db.refresh(row)
        result.update({"status": "ok", "item": {"id": row.id}})

    elif action == "add_recurring":
        description = params.get("description", "Recurring")
        amount = float(params.get("amount", 0) or 0)
        category = params.get("category", "Subscriptions")
        start_date = params.get("start_date")
        frequency = params.get("frequency", "monthly")
        interval = int(params.get("interval", 1) or 1)
        sd = datetime.now().date()
        if start_date:
            try:
                sd = datetime.fromisoformat(start_date).date()
            except Exception:
                pass
        row = RecurringTransaction(user_id=uid, description=description, amount=amount, category=category, start_date=sd, frequency=frequency, interval=interval, next_date=sd)
        db.add(row); db.commit(); db.refresh(row)
        result.update({"status": "ok", "item": {"id": row.id}})

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    return result


def get_user_financial_data(user_id: int, db: Session) -> Dict[str, Any]:
    """Get comprehensive user financial data for context"""
    try:
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get recent transactions (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = db.query(Transaction).filter(
            and_(Transaction.user_id == user_id, Transaction.date >= thirty_days_ago)
        ).order_by(desc(Transaction.date)).limit(20).all()
        
        # Get spending by category (current month)
        current_month = datetime.now().strftime("%Y-%m")
        current_month_start = datetime.now().replace(day=1).date()
        
        category_spending = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= current_month_start,
                Transaction.amount < 0  # Only expenses
            )
        ).group_by(Transaction.category).all()
        
        # Get current month budgets
        current_budgets = db.query(Budget).filter(
            and_(Budget.user_id == user_id, Budget.month == current_month)
        ).all()
        
        # Get active goals
        active_goals = db.query(Goal).filter(Goal.user_id == user_id).order_by(desc(Goal.created_at)).limit(5).all()
        
        # Get upcoming recurring transactions
        upcoming_recurring = db.query(RecurringTransaction).filter(
            and_(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.next_date <= datetime.now().date() + timedelta(days=7)
            )
        ).order_by(RecurringTransaction.next_date).all()
        
        # Calculate financial summary
        total_income = sum(t.amount for t in recent_transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in recent_transactions if t.amount < 0)
        net_worth = total_income - total_expenses
        
        return {
            'user': {
                'name': user.name,
                'email': user.email
            },
            'summary': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_worth': net_worth,
                'transaction_count': len(recent_transactions)
            },
            'recent_transactions': [
                {
                    'description': t.description,
                    'amount': t.amount,
                    'date': t.date.strftime('%Y-%m-%d'),
                    'category': t.category,
                    'merchant': t.merchant
                } for t in recent_transactions
            ],
            'category_spending': [
                {
                    'category': cat.category,
                    'spent': abs(cat.total)
                } for cat in category_spending
            ],
            'budgets': [
                {
                    'category': b.category,
                    'budgeted': b.budgeted,
                    'month': b.month
                } for b in current_budgets
            ],
            'goals': [
                {
                    'name': g.name,
                    'target': g.target,
                    'current': g.current,
                    'progress': (g.current / g.target * 100) if g.target > 0 else 0,
                    'deadline': g.deadline.strftime('%Y-%m-%d') if g.deadline else None
                } for g in active_goals
            ],
            'upcoming_recurring': [
                {
                    'description': r.description,
                    'amount': r.amount,
                    'next_date': r.next_date.strftime('%Y-%m-%d'),
                    'frequency': r.frequency
                } for r in upcoming_recurring
            ]
        }
    except Exception as e:
        print(f"Error getting financial data: {e}")
        return {}


def load_user_context(state: FinanceChatState) -> FinanceChatState:
    """Load user financial data and context"""
    from db.database import SessionLocal
    db = SessionLocal()
    try:
        user_data = get_user_financial_data(state["user_id"], db)
        state["user_data"] = user_data
        
        # Build context summary for AI
        context = {}
        if user_data:
            context = {
                "has_data": True,
                "recent_activity": len(user_data.get('recent_transactions', [])),
                "active_budgets": len(user_data.get('budgets', [])),
                "active_goals": len(user_data.get('goals', [])),
                "net_worth": user_data.get('summary', {}).get('net_worth', 0)
            }
        else:
            context = {"has_data": False}
        
        state["context"] = context
        return state
    finally:
        db.close()


def build_system_prompt(state: FinanceChatState) -> str:
    """Build system prompt with user financial context"""
    user_data = state["user_data"]
    
    if not user_data:
        return """You are FinanceBot, a helpful personal finance assistant. 
The user needs to log in to access personalized financial insights.
CRITICAL: Always format your response in HTML with proper tags."""
    
    user_info = user_data.get('user', {})
    summary = user_data.get('summary', {})
    goals = user_data.get('goals', [])
    budgets = user_data.get('budgets', [])
    recent_transactions = user_data.get('recent_transactions', [])[:5]  # Last 5 transactions
    category_spending = user_data.get('category_spending', [])
    
    user_name = user_info.get('name', 'there')
    
    # Build financial summary
    financial_summary = f"""
Current Financial Snapshot:
- Total Income (30 days): ${summary.get('total_income', 0):,.2f}
- Total Expenses (30 days): ${summary.get('total_expenses', 0):,.2f}
- Net Position: ${summary.get('net_worth', 0):,.2f}
- Recent Transactions: {summary.get('transaction_count', 0)}
"""
    
    # Build goals summary
    goals_summary = ""
    if goals:
        goals_summary = "Active Financial Goals:\n"
        for goal in goals[:3]:  # Top 3 goals
            progress = goal.get('progress', 0)
            goals_summary += f"- {goal['name']}: ${goal['current']:,.2f} of ${goal['target']:,.2f} ({progress:.1f}%)\n"
    else:
        goals_summary = "No active financial goals set"
    
    # Build budget summary
    budget_summary = ""
    if budgets:
        budget_summary = "Current Month Budgets:\n"
        for budget in budgets[:5]:
            budget_summary += f"- {budget['category']}: ${budget['budgeted']:,.2f}\n"
    else:
        budget_summary = "No budgets set for current month"
    
    # Build spending summary
    spending_summary = ""
    if category_spending:
        spending_summary = "Current Month Spending by Category:\n"
        for spending in category_spending[:5]:
            spending_summary += f"- {spending['category']}: ${spending['spent']:,.2f}\n"
    else:
        spending_summary = "No spending data for current month"
    
    return f"""
You are FinanceBot, a knowledgeable and friendly personal finance assistant for {user_name}.

CRITICAL FORMATTING REQUIREMENT: Always format your response as clean, well-structured HTML. Use proper HTML tags for structure and styling.

Your responses should be:
- Conversational and helpful, like talking to a trusted financial advisor
- Well-formatted using HTML tags (h3, p, ul, li, strong, em, div, etc.)
- Use HTML lists for recommendations and bullet points
- Use HTML tables for financial data when appropriate
- Use HTML headings for section organization
- Include inline CSS styling for better visual appeal
- Actionable and specific to their financial situation

HTML FORMATTING GUIDELINES:
- Use <h3> for main section headings with colors like #2c3e50 or #27ae60
- Use <p> for paragraphs with proper spacing
- Use <ul> and <li> for bullet points and recommendations
- Use <strong> for emphasis on important numbers or concepts
- Use <em> for highlighting key insights
- Use <table> with inline styles for financial data
- Add inline styles for colors, spacing, and layout
- Use <div> with styles for better visual organization

USER FINANCIAL CONTEXT:
{financial_summary}

{goals_summary}

{budget_summary}

{spending_summary}

When providing advice or insights:
1. Reference specific data from their financial profile
2. Provide actionable recommendations based on their spending patterns
3. Help them understand their financial health
4. Suggest improvements to budgets, goals, or spending habits
5. Format everything in clean HTML with appropriate styling

Example HTML format for financial insights:
<h3 style="color: #27ae60; margin-bottom: 10px;">💰 Financial Insights</h3>
<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
  <p><strong>Key Finding:</strong> Your explanation here</p>
  <ul style="margin: 10px 0;">
    <li style="margin: 5px 0;">Specific recommendation</li>
  </ul>
</div>
"""


def finance_chat_node(state: FinanceChatState) -> FinanceChatState:
    """Main chat processing node using Groq"""
    try:
        # Get the last user message
        last_message = state["messages"][-1]["content"]
        
        # Build system prompt with financial context
        system_prompt = build_system_prompt(state)
        
        # Call Groq API
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": last_message}
            ],
            model="openai/gpt-oss-20b",
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Ensure HTML formatting
        if not ai_response.strip().startswith('<'):
            ai_response = f"<p>{ai_response}</p>"
        
        # Add AI response to conversation
        state["messages"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        state["response"] = ai_response
        return state
        
    except Exception as e:
        print(f"Chat error: {e}")
        error_response = f"<p style='color: #e74c3c;'><strong>I'm experiencing technical difficulties.</strong> Please try again later. Error: {str(e)}</p>"
        state["response"] = error_response
        return state


# Create the LangGraph workflow
def create_finance_chat_graph():
    """Create LangGraph workflow for finance chat"""
    workflow = StateGraph(FinanceChatState)
    
    # Add nodes
    workflow.add_node("load_context", load_user_context)
    workflow.add_node("chat", finance_chat_node)
    
    # Add edges
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "chat")
    workflow.add_edge("chat", END)
    
    return workflow.compile()

# Initialize the graph
finance_chat_graph = create_finance_chat_graph()


def process_finance_chat(user_id: int, message: str) -> str:
    """Main chat processing function with context and memory"""
    try:
        # Get chat history for context
        history = chat_memory.get(user_id, [])

        # Create message list with recent history
        messages = []
        for msg in history[-6:]:  # Last 6 messages for context
            messages.append(msg)

        # Add current message
        current_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        }
        messages.append(current_message)

        # Create initial state
        initial_state = FinanceChatState(
            messages=messages,
            user_id=user_id,
            user_data={},
            context={},
            response="",
        )

        # Process through LangGraph workflow
        result = finance_chat_graph.invoke(initial_state)
        response = result.get(
            "response",
            "I apologize, but I couldn't process your request right now.",
        )

        # Store in memory
        if user_id not in chat_memory:
            chat_memory[user_id] = []

        # Add both user message and AI response to memory
        timestamp = datetime.now().isoformat()
        chat_memory[user_id].extend(
            [
                {"role": "user", "content": message, "timestamp": timestamp},
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp,
                },
            ]
        )

        # Trim history to maximum allowed length
        if len(chat_memory[user_id]) > MAX_CHAT_HISTORY:
            chat_memory[user_id] = chat_memory[user_id][-MAX_CHAT_HISTORY:]

        return response

    except Exception as e:
        print(f"Finance chat error: {e}")
        import traceback
        traceback.print_exc()
        return (
            "<p style='color: #e74c3c;'><strong>Sorry, I'm having trouble processing your request.</strong> Please try again later.</p>"
        )


@router.post("/chat")
async def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Advanced finance chatbot with LangGraph workflow and context"""
    try:
        # Determine user id: prefer authenticated user; else fallback to payload
        uid = current_user.id if current_user else None
        if uid is None:
            # Fallback to request-provided ids
            if request.user_id is not None:
                uid = request.user_id
            elif request.emp_id is not None:
                try:
                    uid = int(request.emp_id)
                except Exception:
                    uid = 1  # final fallback to test user
            else:
                uid = 1

        # Generate chat response
        response_html = process_finance_chat(uid, request.message)

        # Try to extract and auto-execute action when clear
        action_info = extract_action_from_message(request.message)
        executed = False
        action_result = None
        if action_info and action_info.get("action"):
            try:
                db = SessionLocal()
                action_result = run_action(db, uid, action_info["action"], action_info.get("params", {}))
                executed = True
                # Append a brief confirmation to the HTML response
                summary = f"<div style='margin-top:10px;padding:8px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#1f2937;'>✅ Executed action: <strong>{action_info['action']}</strong></div>"
                response_html = response_html + summary
            except HTTPException as he:
                # If execution fails, include notice but keep chat reply
                notice = f"<div style='margin-top:10px;padding:8px;border:1px solid #fecaca;border-radius:8px;background:#fef2f2;color:#991b1b;'>⚠️ Action failed: {he.detail}</div>"
                response_html = response_html + notice
            except Exception as e:
                notice = f"<div style='margin-top:10px;padding:8px;border:1px solid #fecaca;border-radius:8px;background:#fef2f2;color:#991b1b;'>⚠️ Action failed: {str(e)}</div>"
                response_html = response_html + notice
            finally:
                try:
                    db.close()
                except Exception:
                    pass

        return {
            "response": response_html,
            "user_id": uid,
            "timestamp": datetime.now().isoformat(),
            "action": action_info or {"action": "none", "params": {}},
            "executed": executed,
            "result": action_result,
        }
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return {
            "response": "<p style='color: #e74c3c;'>I'm having trouble connecting right now. Please try again later.</p>",
            "error": str(e)
        }


class ExecuteRequest(BaseModel):
    user_id: int | None = None
    action: str
    params: Dict[str, Any] | None = None


@router.post("/chat/execute")
async def execute_suggestion(req: ExecuteRequest, current_user: User = Depends(get_current_user)):
    """Execute a suggested action using DB write operations."""
    db = SessionLocal()
    try:
        uid = current_user.id if current_user else (req.user_id or 1)
        action = (req.action or "").lower()
        params = req.params or {}

        result = run_action(db, uid, action, params)
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Execution failed: {e}")
    finally:
        db.close()


@router.post("/chat/clear")
async def clear_chat(current_user: User = Depends(get_current_user)) -> Dict[str, str]:
    """Clear chat history for current user"""
    try:
        if current_user.id in chat_memory:
            del chat_memory[current_user.id]
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        return {"error": f"Failed to clear chat history: {str(e)}"}