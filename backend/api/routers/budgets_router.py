from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models as dbm
from api.schemas import Budget
from api.deps import safe_uid, get_user_or_404

router = APIRouter()

@router.get("/budgets/{user_id}")
async def get_budgets(user_id: str, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    rows = (
        db.query(dbm.Budget)
        .filter(dbm.Budget.user_id == uid)
        .order_by(dbm.Budget.month.desc(), dbm.Budget.category.asc())
        .all()
    )
    return [{"id": r.id, "category": r.category, "budgeted": r.budgeted, "month": r.month} for r in rows]

@router.post("/budgets/{user_id}")
async def add_budget(user_id: str, budget: Budget, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    row = dbm.Budget(user_id=uid, category=budget.category, budgeted=budget.budgeted, month=budget.month)
    db.add(row)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Budget for category/month already exists")
    count = db.query(dbm.Budget).filter(dbm.Budget.user_id == uid).count()
    return {"message": "Budget added", "count": count}

@router.get("/budgets/{user_id}/{item_id}")
async def get_budget(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Budget).filter(dbm.Budget.user_id == uid, dbm.Budget.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"id": r.id, "category": r.category, "budgeted": r.budgeted, "month": r.month}

@router.put("/budgets/{user_id}/{item_id}")
async def update_budget(user_id: str, item_id: int, budget: Budget, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Budget).filter(dbm.Budget.user_id == uid, dbm.Budget.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Budget not found")
    r.category = budget.category
    r.budgeted = budget.budgeted
    r.month = budget.month
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Budget conflict (duplicate category/month)")
    return {"message": "Budget updated", "item": {"id": r.id, "category": r.category, "budgeted": r.budgeted, "month": r.month}}

@router.delete("/budgets/{user_id}/{item_id}")
async def delete_budget(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Budget).filter(dbm.Budget.user_id == uid, dbm.Budget.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(r)
    db.commit()
    count = db.query(dbm.Budget).filter(dbm.Budget.user_id == uid).count()
    return {"message": "Budget deleted", "count": count}
