from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from db.database import get_db
from db import models as dbm
from api.schemas import Transaction as TxSchema
from api.deps import safe_uid, get_user_or_404

router = APIRouter()

@router.get("/transactions/{user_id}")
async def get_transactions(user_id: str, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    rows = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == uid)
        .order_by(dbm.Transaction.date.desc(), dbm.Transaction.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "description": r.description,
            "amount": r.amount,
            "date": r.date.isoformat(),
            "category": r.category,
            "merchant": r.merchant,
            "account_type": r.account_type,
            "recurring_id": r.recurring_id,
        }
        for r in rows
    ]

@router.post("/transactions/{user_id}")
async def add_transaction(user_id: str, tx: TxSchema, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    row = dbm.Transaction(
        user_id=uid,
        description=tx.description,
        amount=tx.amount,
        date=datetime.strptime(tx.date, "%Y-%m-%d").date(),
        category=tx.category,
    )
    db.add(row)
    db.commit()
    count = db.query(dbm.Transaction).filter(dbm.Transaction.user_id == uid).count()
    return {"message": "Transaction added", "count": count}

@router.get("/transactions/{user_id}/{item_id}")
async def get_transaction(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    row = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == uid, dbm.Transaction.id == item_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "id": row.id,
        "description": row.description,
        "amount": row.amount,
        "date": row.date.isoformat(),
        "category": row.category,
        "merchant": row.merchant,
        "account_type": row.account_type,
        "recurring_id": row.recurring_id,
    }

@router.put("/transactions/{user_id}/{item_id}")
async def update_transaction(user_id: str, item_id: int, tx: TxSchema, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    row = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == uid, dbm.Transaction.id == item_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    row.description = tx.description
    row.amount = tx.amount
    row.date = datetime.strptime(tx.date, "%Y-%m-%d").date()
    row.category = tx.category
    db.commit()
    db.refresh(row)
    return {"message": "Transaction updated", "item": {
        "id": row.id,
        "description": row.description,
        "amount": row.amount,
        "date": row.date.isoformat(),
        "category": row.category,
        "merchant": row.merchant,
        "account_type": row.account_type,
        "recurring_id": row.recurring_id,
    }}

@router.delete("/transactions/{user_id}/{item_id}")
async def delete_transaction(user_id: str, item_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    row = (
        db.query(dbm.Transaction)
        .filter(dbm.Transaction.user_id == uid, dbm.Transaction.id == item_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(row)
    db.commit()
    count = db.query(dbm.Transaction).filter(dbm.Transaction.user_id == uid).count()
    return {"message": "Transaction deleted", "count": count}
