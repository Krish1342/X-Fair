from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from db import models as dbm
from api.schemas import RecurringTransaction as RecSchema
from api.deps import safe_uid, get_user_or_404, parse_date, format_date, advance
from datetime import datetime

router = APIRouter()

@router.get("/recurring/{user_id}")
async def list_recurring(user_id: str, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    rows = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid).order_by(dbm.RecurringTransaction.next_date.asc()).all()
    return [
        {
            "id": r.id,
            "description": r.description,
            "amount": r.amount,
            "category": r.category,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat() if r.end_date else None,
            "frequency": r.frequency,
            "interval": r.interval,
            "next_date": r.next_date.isoformat(),
        }
        for r in rows
    ]

@router.post("/recurring/{user_id}")
async def create_recurring(user_id: str, item: RecSchema, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    start = parse_date(item.start_date)
    next_d = parse_date(item.next_date) if item.next_date else start
    r = dbm.RecurringTransaction(
        user_id=uid,
        description=item.description,
        amount=item.amount,
        category=item.category,
        start_date=start,
        end_date=parse_date(item.end_date) if item.end_date else None,
        frequency=item.frequency,
        interval=item.interval,
        next_date=next_d,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"message": "Recurring transaction created", "item": {
        "id": r.id,
        "description": r.description,
        "amount": r.amount,
        "category": r.category,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat() if r.end_date else None,
        "frequency": r.frequency,
        "interval": r.interval,
        "next_date": r.next_date.isoformat(),
    }}

@router.get("/recurring/{user_id}/{rec_id}")
async def get_recurring(user_id: str, rec_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid, dbm.RecurringTransaction.id == rec_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    return {
        "id": r.id,
        "description": r.description,
        "amount": r.amount,
        "category": r.category,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat() if r.end_date else None,
        "frequency": r.frequency,
        "interval": r.interval,
        "next_date": r.next_date.isoformat(),
    }

@router.put("/recurring/{user_id}/{rec_id}")
async def update_recurring(user_id: str, rec_id: int, item: RecSchema, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid, dbm.RecurringTransaction.id == rec_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    start = parse_date(item.start_date)
    next_d = parse_date(item.next_date) if item.next_date else start
    r.description = item.description
    r.amount = item.amount
    r.category = item.category
    r.start_date = start
    r.end_date = parse_date(item.end_date) if item.end_date else None
    r.frequency = item.frequency
    r.interval = item.interval
    r.next_date = next_d
    db.commit()
    return {"message": "Recurring transaction updated", "item": {
        "id": r.id,
        "description": r.description,
        "amount": r.amount,
        "category": r.category,
        "start_date": r.start_date.isoformat(),
        "end_date": r.end_date.isoformat() if r.end_date else None,
        "frequency": r.frequency,
        "interval": r.interval,
        "next_date": r.next_date.isoformat(),
    }}

@router.delete("/recurring/{user_id}/{rec_id}")
async def delete_recurring(user_id: str, rec_id: int, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    r = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid, dbm.RecurringTransaction.id == rec_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    db.delete(r)
    db.commit()
    count = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid).count()
    return {"message": "Recurring transaction deleted", "count": count}

@router.post("/recurring/{user_id}/generate")
async def generate_due_transactions(user_id: str, up_to: Optional[str] = None, db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    limit_date = parse_date(up_to) if up_to else today
    uid = safe_uid(user_id)
    rec_list = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid).all()
    generated = []
    for rec in rec_list:
        if rec.end_date and rec.end_date < (rec.next_date or rec.start_date):
            continue
        next_d = rec.next_date or rec.start_date
        while next_d <= limit_date:
            tx_row = dbm.Transaction(
                user_id=uid,
                description=rec.description,
                amount=rec.amount,
                date=next_d,
                category=rec.category,
                recurring_id=rec.id,
            )
            db.add(tx_row)
            db.flush()
            generated.append({
                "id": tx_row.id,
                "description": tx_row.description,
                "amount": tx_row.amount,
                "date": format_date(next_d),
                "category": tx_row.category,
                "recurring_id": rec.id,
            })
            next_d = advance(next_d, rec.frequency or "monthly", int(rec.interval or 1))
            if rec.end_date and next_d > rec.end_date:
                break
        rec.next_date = next_d
    db.commit()
    return {"message": "Generated transactions", "count": len(generated), "items": generated}

@router.get("/recurring/{user_id}/preview")
async def preview_recurring(user_id: str, periods: int = 3, db: Session = Depends(get_db)):
    uid = safe_uid(user_id)
    rec_list = db.query(dbm.RecurringTransaction).filter(dbm.RecurringTransaction.user_id == uid).all()
    previews = []
    for rec in rec_list:
        d = rec.next_date or rec.start_date
        dates = []
        cur = d
        for _ in range(max(1, int(periods))):
            dates.append(format_date(cur))
            cur = advance(cur, rec.frequency or "monthly", int(rec.interval or 1))
            if rec.end_date and cur > rec.end_date:
                break
        previews.append({"id": rec.id, "description": rec.description, "next_dates": dates})
    return {"items": previews}
