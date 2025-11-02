from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import get_db
from db import models as dbm
from api.schemas import Goal
from api.deps import safe_uid, get_user_or_404

router = APIRouter()

@router.get("/goals/{user_id}")
async def get_goals(user_id: str, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    rows = (
        db.query(dbm.Goal)
        .filter(dbm.Goal.user_id == uid)
        .order_by(dbm.Goal.deadline.is_(None), dbm.Goal.deadline.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "target": r.target,
            "current": r.current,
            "deadline": r.deadline.isoformat() if r.deadline else None,
            "category": r.category,
            "monthly_contribution": r.monthly_contribution,
            "description": r.description,
        }
        for r in rows
    ]

@router.post("/goals/{user_id}")
async def add_goal(user_id: str, goal: Goal, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    row = dbm.Goal(
        user_id=uid,
        name=goal.name,
        target=goal.target,
        current=goal.current or 0,
        deadline=datetime.strptime(goal.deadline, "%Y-%m-%d").date() if goal.deadline else None,
    )
    db.add(row)
    db.commit()
    count = db.query(dbm.Goal).filter(dbm.Goal.user_id == uid).count()
    return {"message": "Goal added", "count": count}

@router.get("/goals/{user_id}/{item_id}")
async def get_goal(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Goal).filter(dbm.Goal.user_id == uid, dbm.Goal.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {
        "id": r.id,
        "name": r.name,
        "target": r.target,
        "current": r.current,
        "deadline": r.deadline.isoformat() if r.deadline else None,
        "category": r.category,
        "monthly_contribution": r.monthly_contribution,
        "description": r.description,
    }

@router.put("/goals/{user_id}/{item_id}")
async def update_goal(user_id: str, item_id: int, goal: Goal, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Goal).filter(dbm.Goal.user_id == uid, dbm.Goal.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Goal not found")
    r.name = goal.name
    r.target = goal.target
    r.current = goal.current or 0
    r.deadline = datetime.strptime(goal.deadline, "%Y-%m-%d").date() if goal.deadline else None
    db.commit()
    return {"message": "Goal updated", "item": {
        "id": r.id,
        "name": r.name,
        "target": r.target,
        "current": r.current,
        "deadline": r.deadline.isoformat() if r.deadline else None,
    }}

@router.delete("/goals/{user_id}/{item_id}")
async def delete_goal(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.Goal).filter(dbm.Goal.user_id == uid, dbm.Goal.id == item_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(r)
    db.commit()
    count = db.query(dbm.Goal).filter(dbm.Goal.user_id == uid).count()
    return {"message": "Goal deleted", "count": count}
