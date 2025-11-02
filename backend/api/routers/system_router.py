from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from collections import defaultdict
from db.database import get_db
from db import models as dbm
from core.groq_client import groq_client

router = APIRouter()

@router.get("/health")
async def health_check():
    groq_status = "healthy" if groq_client.api_key else "missing_api_key"
    return {
        "status": "healthy",
        "service": "finance-agent-api",
        "groq_integration": groq_status,
    }

@router.get("/dashboard")
async def get_dashboard(user_id: int, timeframe: str = "30d", db: Session = Depends(get_db)):
    # Validate user
    user = db.query(dbm.User).filter(dbm.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine date window
    today = date.today()
    tf_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = tf_map.get(timeframe.lower(), 30)
    start_date = today - timedelta(days=days)

    # Transactions within window
    tx_q = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == user_id, dbm.Transaction.date >= start_date, dbm.Transaction.date <= today)
    )
    txs = tx_q.all()

    income = sum(t.amount for t in txs if t.amount > 0)
    expenses = sum(-t.amount for t in txs if t.amount < 0)
    savings_rate = round(((income - expenses) / income) * 100, 2) if income > 0 else 0.0

    # Account balance = net of all transactions to date
    all_net = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == user_id)
        .all()
    )
    account_balance = round(sum(t.amount for t in all_net), 2)

    # Budgets for current month and spend by category
    month_key = f"{today.year}-{today.month:02d}"
    budgets = db.query(dbm.Budget).filter(dbm.Budget.user_id == user_id, dbm.Budget.month == month_key).all()
    spent_by_cat = defaultdict(float)
    month_start = date(today.year, today.month, 1)
    month_txs = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == user_id, dbm.Transaction.date >= month_start, dbm.Transaction.date <= today)
        .all()
    )
    for t in month_txs:
        if t.amount < 0:
            spent_by_cat[t.category or "Uncategorized"] += -t.amount
    budget_categories = []
    for b in budgets:
        spent = round(spent_by_cat.get(b.category, 0.0), 2)
        pct = round((spent / b.budgeted) * 100, 2) if b.budgeted else 0.0
        budget_categories.append({"name": b.category, "budgeted": b.budgeted, "spent": spent, "percentage": pct})

    # Recent transactions (last 5)
    recent = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == user_id)
        .order_by(dbm.Transaction.date.desc(), dbm.Transaction.id.desc())
        .limit(5)
        .all()
    )
    recent_transactions = [
        {"id": t.id, "description": t.description, "amount": t.amount, "date": t.date.isoformat(), "category": t.category}
        for t in recent
    ]

    # Goals
    goals = (
        db.query(dbm.Goal)
        .filter(dbm.Goal.user_id == user_id)
        .order_by(dbm.Goal.deadline.is_(None), dbm.Goal.deadline.asc())
        .all()
    )
    goals_out = [
        {
            "id": g.id,
            "name": g.name,
            "target": g.target,
            "current": g.current or 0.0,
            "deadline": g.deadline.isoformat() if g.deadline else None,
        }
        for g in goals
    ]

    # User-tailored insights + actionable suggestions
    insights = []
    suggestions = []

    # Overspending alerts with concrete suggestion
    for b in budget_categories:
        if b["budgeted"] and b["spent"] > b["budgeted"]:
            over_pct = round(((b["spent"] - b["budgeted"]) / b["budgeted"]) * 100, 1)
            insights.append({
                "title": f"{b['name']} over budget",
                "description": f"You've spent ${b['spent']:.2f} against a ${b['budgeted']:.2f} budget ({over_pct}% over).",
                "type": "warning",
                "category": b["name"],
            })
            # Suggest: increase this month's budget slightly or set next month's budget proactively
            # Provide complete params so the execute API can succeed immediately
            increased_amount = round(b["budgeted"] * 1.1, 2)
            suggestions.append({
                "label": f"Increase {b['name']} budget by 10% for {month_key}",
                "action": "update_budget",
                "params": {
                    "category": b["name"],
                    "month": month_key,
                    "budgeted": increased_amount,
                },
                "explain": "You overspent in this category; temporarily increasing budget can avoid constant overages while you adjust habits.",
            })

    # If a category has zero budget but has spending, propose adding a budget
    spent_nonbudget = [
        cat for cat, amt in spent_by_cat.items()
        if amt > 0 and not any(b["name"] == cat for b in budget_categories)
    ]
    for cat in spent_nonbudget[:3]:
        amt = round(spent_by_cat[cat], 2)
        base_budget = max(50.0, round(amt * 1.1, 2))
        insights.append({
            "title": f"No budget set for {cat}",
            "description": f"You've spent ${amt:.2f} this month in {cat} without a budget.",
            "type": "tip",
            "category": cat,
        })
        suggestions.append({
            "label": f"Create {cat} budget ${base_budget} for {month_key}",
            "action": "add_budget",
            "params": {"category": cat, "budgeted": base_budget, "month": month_key},
            "explain": "Setting a small starter budget helps track and control this spend category.",
        })

    # Savings rate suggestion: if below 20% and income>0, propose a small recurring transfer
    if income > 0 and savings_rate < 20:
        suggested_amount = round(0.05 * income, 2)  # 5% of monthly income
        insights.append({
            "title": "Improve savings rate",
            "description": f"Your savings rate is {savings_rate}%. Automating a ${suggested_amount:.2f}/mo transfer can help.",
            "type": "tip",
        })
        suggestions.append({
            "label": f"Create recurring Savings transfer ${suggested_amount}/mo",
            "action": "add_recurring",
            "params": {
                "description": "Auto-transfer to savings",
                "amount": -suggested_amount,
                "category": "Savings",
                "start_date": today.isoformat(),
                "frequency": "monthly",
                "interval": 1,
            },
            "explain": "Automated savings make it easier to hit your goals without manual effort.",
        })

    return {
        "accountBalance": account_balance,
        "monthlyIncome": round(income, 2),
        "monthlyExpenses": round(expenses, 2),
        "savingsRate": savings_rate,
        "budgetCategories": budget_categories,
        "recentTransactions": recent_transactions,
        "goals": goals_out,
        "insights": insights,
        "suggestions": suggestions,
    }
