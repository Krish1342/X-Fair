"""
Portfolio router for managing stocks and mutual funds.
Includes live price updates using yfinance API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import yfinance as yf

from db.database import get_db
from db import models as dbm
from api.deps import safe_uid, get_user_or_404

router = APIRouter()


# Request/Response Models
class StockCreate(BaseModel):
    symbol: str
    name: str
    quantity: float
    avg_buy_price: float
    exchange: Optional[str] = None
    currency: str = "USD"
    notes: Optional[str] = None


class StockUpdate(BaseModel):
    quantity: Optional[float] = None
    avg_buy_price: Optional[float] = None
    notes: Optional[str] = None


class MutualFundCreate(BaseModel):
    scheme_code: str
    scheme_name: str
    fund_house: Optional[str] = None
    units: float
    avg_nav: float
    scheme_type: Optional[str] = None
    sip_amount: Optional[float] = None
    sip_date: Optional[int] = None
    currency: str = "INR"
    notes: Optional[str] = None


class MutualFundUpdate(BaseModel):
    units: Optional[float] = None
    avg_nav: Optional[float] = None
    sip_amount: Optional[float] = None
    sip_date: Optional[int] = None
    notes: Optional[str] = None


def get_live_stock_price(symbol: str) -> Dict[str, Any]:
    """
    Fetch live stock price using yfinance.
    Returns current price, change, and additional data.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if hist.empty:
            # Try 5-day history
            hist = ticker.history(period="5d")
        
        current_price = None
        prev_close = None
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
            else:
                prev_close = info.get('previousClose', current_price)
        else:
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
        
        if current_price is None:
            raise ValueError("Could not fetch price data")
        
        change = current_price - prev_close if prev_close else 0
        change_percent = (change / prev_close * 100) if prev_close else 0
        
        return {
            "success": True,
            "symbol": symbol,
            "current_price": current_price,
            "previous_close": prev_close,
            "change": change,
            "change_percent": change_percent,
            "currency": info.get('currency', 'USD'),
            "market_cap": info.get('marketCap'),
            "volume": info.get('volume'),
            "day_high": info.get('dayHigh'),
            "day_low": info.get('dayLow'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
        }
    except Exception as e:
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e),
            "current_price": None,
        }


def get_mutual_fund_nav(scheme_code: str) -> Dict[str, Any]:
    """
    Fetch mutual fund NAV. 
    For Indian mutual funds, you would typically use MFAPI or similar.
    This is a placeholder that can be extended.
    """
    # Placeholder - in production, integrate with Indian MF APIs
    # like https://api.mfapi.in/mf/{scheme_code}
    try:
        # For now, return a mock response
        # You can integrate with actual MF API here
        return {
            "success": True,
            "scheme_code": scheme_code,
            "current_nav": None,  # Would come from API
            "nav_date": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "scheme_code": scheme_code,
            "error": str(e),
        }


# Stock Endpoints
@router.post("/portfolio/stocks/{user_id}")
def create_stock(user_id: str, stock: StockCreate, db: Session = Depends(get_db)):
    """Create a new stock holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    # Get live price
    price_data = get_live_stock_price(stock.symbol)
    
    new_stock = dbm.Stock(
        user_id=uid,
        symbol=stock.symbol.upper(),
        name=stock.name,
        quantity=stock.quantity,
        avg_buy_price=stock.avg_buy_price,
        current_price=price_data.get("current_price"),
        last_updated=datetime.now() if price_data.get("success") else None,
        exchange=stock.exchange,
        currency=stock.currency,
        notes=stock.notes,
    )
    
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    
    return {
        "success": True,
        "stock": {
            "id": new_stock.id,
            "symbol": new_stock.symbol,
            "name": new_stock.name,
            "quantity": new_stock.quantity,
            "avg_buy_price": new_stock.avg_buy_price,
            "current_price": new_stock.current_price,
            "total_investment": new_stock.quantity * new_stock.avg_buy_price,
            "current_value": new_stock.quantity * new_stock.current_price if new_stock.current_price else 0,
        }
    }


@router.get("/portfolio/stocks/{user_id}")
def get_stocks(user_id: str, refresh: bool = False, db: Session = Depends(get_db)):
    """Get all stock holdings with optional live price refresh"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    stocks = db.query(dbm.Stock).filter(dbm.Stock.user_id == uid).all()
    
    stock_list = []
    for stock in stocks:
        # Refresh price if requested or if data is stale (>1 hour)
        should_refresh = refresh or (
            stock.last_updated is None or 
            datetime.now() - stock.last_updated > timedelta(hours=1)
        )
        
        if should_refresh:
            price_data = get_live_stock_price(stock.symbol)
            if price_data.get("success"):
                stock.current_price = price_data["current_price"]
                stock.last_updated = datetime.now()
                db.commit()
        
        total_investment = stock.quantity * stock.avg_buy_price
        current_value = stock.quantity * stock.current_price if stock.current_price else 0
        profit_loss = current_value - total_investment
        profit_loss_percent = (profit_loss / total_investment * 100) if total_investment > 0 else 0
        
        stock_list.append({
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "quantity": stock.quantity,
            "avg_buy_price": stock.avg_buy_price,
            "current_price": stock.current_price,
            "total_investment": total_investment,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent,
            "exchange": stock.exchange,
            "currency": stock.currency,
            "last_updated": stock.last_updated.isoformat() if stock.last_updated else None,
            "notes": stock.notes,
        })
    
    return {"success": True, "stocks": stock_list}


@router.get("/portfolio/stocks/{user_id}/{stock_id}")
def get_stock(user_id: str, stock_id: int, db: Session = Depends(get_db)):
    """Get a specific stock with live price"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    stock = db.query(dbm.Stock).filter(
        dbm.Stock.id == stock_id, 
        dbm.Stock.user_id == uid
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Get live price
    price_data = get_live_stock_price(stock.symbol)
    if price_data.get("success"):
        stock.current_price = price_data["current_price"]
        stock.last_updated = datetime.now()
        db.commit()
    
    total_investment = stock.quantity * stock.avg_buy_price
    current_value = stock.quantity * stock.current_price if stock.current_price else 0
    
    return {
        "success": True,
        "stock": {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "quantity": stock.quantity,
            "avg_buy_price": stock.avg_buy_price,
            "current_price": stock.current_price,
            "total_investment": total_investment,
            "current_value": current_value,
            "profit_loss": current_value - total_investment,
            "profit_loss_percent": ((current_value - total_investment) / total_investment * 100) if total_investment > 0 else 0,
            "price_data": price_data if price_data.get("success") else None,
        }
    }


@router.put("/portfolio/stocks/{user_id}/{stock_id}")
def update_stock(user_id: str, stock_id: int, stock_update: StockUpdate, db: Session = Depends(get_db)):
    """Update a stock holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    stock = db.query(dbm.Stock).filter(
        dbm.Stock.id == stock_id,
        dbm.Stock.user_id == uid
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    if stock_update.quantity is not None:
        stock.quantity = stock_update.quantity
    if stock_update.avg_buy_price is not None:
        stock.avg_buy_price = stock_update.avg_buy_price
    if stock_update.notes is not None:
        stock.notes = stock_update.notes
    
    db.commit()
    db.refresh(stock)
    
    return {"success": True, "message": "Stock updated successfully"}


@router.delete("/portfolio/stocks/{user_id}/{stock_id}")
def delete_stock(user_id: str, stock_id: int, db: Session = Depends(get_db)):
    """Delete a stock holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    stock = db.query(dbm.Stock).filter(
        dbm.Stock.id == stock_id,
        dbm.Stock.user_id == uid
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    db.delete(stock)
    db.commit()
    
    return {"success": True, "message": "Stock deleted successfully"}


# Mutual Fund Endpoints
@router.post("/portfolio/mutual-funds/{user_id}")
def create_mutual_fund(user_id: str, mf: MutualFundCreate, db: Session = Depends(get_db)):
    """Create a new mutual fund holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    new_mf = dbm.MutualFund(
        user_id=uid,
        scheme_code=mf.scheme_code,
        scheme_name=mf.scheme_name,
        fund_house=mf.fund_house,
        units=mf.units,
        avg_nav=mf.avg_nav,
        current_nav=mf.avg_nav,  # Initially same as avg_nav
        scheme_type=mf.scheme_type,
        sip_amount=mf.sip_amount,
        sip_date=mf.sip_date,
        currency=mf.currency,
        notes=mf.notes,
    )
    
    db.add(new_mf)
    db.commit()
    db.refresh(new_mf)
    
    return {
        "success": True,
        "mutual_fund": {
            "id": new_mf.id,
            "scheme_code": new_mf.scheme_code,
            "scheme_name": new_mf.scheme_name,
            "units": new_mf.units,
            "avg_nav": new_mf.avg_nav,
            "current_nav": new_mf.current_nav,
            "total_investment": new_mf.units * new_mf.avg_nav,
        }
    }


@router.get("/portfolio/mutual-funds/{user_id}")
def get_mutual_funds(user_id: str, db: Session = Depends(get_db)):
    """Get all mutual fund holdings"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    mfs = db.query(dbm.MutualFund).filter(dbm.MutualFund.user_id == uid).all()
    
    mf_list = []
    for mf in mfs:
        total_investment = mf.units * mf.avg_nav
        current_value = mf.units * mf.current_nav if mf.current_nav else 0
        profit_loss = current_value - total_investment
        profit_loss_percent = (profit_loss / total_investment * 100) if total_investment > 0 else 0
        
        mf_list.append({
            "id": mf.id,
            "scheme_code": mf.scheme_code,
            "scheme_name": mf.scheme_name,
            "fund_house": mf.fund_house,
            "units": mf.units,
            "avg_nav": mf.avg_nav,
            "current_nav": mf.current_nav,
            "total_investment": total_investment,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent,
            "scheme_type": mf.scheme_type,
            "sip_amount": mf.sip_amount,
            "sip_date": mf.sip_date,
            "currency": mf.currency,
            "notes": mf.notes,
        })
    
    return {"success": True, "mutual_funds": mf_list}


@router.put("/portfolio/mutual-funds/{user_id}/{mf_id}")
def update_mutual_fund(user_id: str, mf_id: int, mf_update: MutualFundUpdate, db: Session = Depends(get_db)):
    """Update a mutual fund holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    mf = db.query(dbm.MutualFund).filter(
        dbm.MutualFund.id == mf_id,
        dbm.MutualFund.user_id == uid
    ).first()
    
    if not mf:
        raise HTTPException(status_code=404, detail="Mutual fund not found")
    
    if mf_update.units is not None:
        mf.units = mf_update.units
    if mf_update.avg_nav is not None:
        mf.avg_nav = mf_update.avg_nav
    if mf_update.sip_amount is not None:
        mf.sip_amount = mf_update.sip_amount
    if mf_update.sip_date is not None:
        mf.sip_date = mf_update.sip_date
    if mf_update.notes is not None:
        mf.notes = mf_update.notes
    
    db.commit()
    db.refresh(mf)
    
    return {"success": True, "message": "Mutual fund updated successfully"}


@router.delete("/portfolio/mutual-funds/{user_id}/{mf_id}")
def delete_mutual_fund(user_id: str, mf_id: int, db: Session = Depends(get_db)):
    """Delete a mutual fund holding"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    mf = db.query(dbm.MutualFund).filter(
        dbm.MutualFund.id == mf_id,
        dbm.MutualFund.user_id == uid
    ).first()
    
    if not mf:
        raise HTTPException(status_code=404, detail="Mutual fund not found")
    
    db.delete(mf)
    db.commit()
    
    return {"success": True, "message": "Mutual fund deleted successfully"}


@router.get("/portfolio/summary/{user_id}")
def get_portfolio_summary(user_id: str, db: Session = Depends(get_db)):
    """Get overall portfolio summary with total investment, current value, and P&L"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    # Get stocks
    stocks = db.query(dbm.Stock).filter(dbm.Stock.user_id == uid).all()
    stocks_investment = sum(s.quantity * s.avg_buy_price for s in stocks)
    stocks_current = sum(s.quantity * (s.current_price or s.avg_buy_price) for s in stocks)
    
    # Get mutual funds
    mfs = db.query(dbm.MutualFund).filter(dbm.MutualFund.user_id == uid).all()
    mf_investment = sum(m.units * m.avg_nav for m in mfs)
    mf_current = sum(m.units * (m.current_nav or m.avg_nav) for m in mfs)
    
    total_investment = stocks_investment + mf_investment
    total_current = stocks_current + mf_current
    total_pl = total_current - total_investment
    total_pl_percent = (total_pl / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "success": True,
        "summary": {
            "total_investment": total_investment,
            "current_value": total_current,
            "profit_loss": total_pl,
            "profit_loss_percent": total_pl_percent,
            "stocks": {
                "count": len(stocks),
                "investment": stocks_investment,
                "current_value": stocks_current,
                "profit_loss": stocks_current - stocks_investment,
            },
            "mutual_funds": {
                "count": len(mfs),
                "investment": mf_investment,
                "current_value": mf_current,
                "profit_loss": mf_current - mf_investment,
            },
        }
    }


@router.post("/portfolio/refresh-prices/{user_id}")
def refresh_all_prices(user_id: str, db: Session = Depends(get_db)):
    """Refresh all stock prices"""
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)
    
    stocks = db.query(dbm.Stock).filter(dbm.Stock.user_id == uid).all()
    
    updated = 0
    failed = 0
    
    for stock in stocks:
        try:
            price_data = get_live_stock_price(stock.symbol)
            if price_data.get("success") and price_data.get("current_price"):
                stock.current_price = price_data["current_price"]
                stock.last_updated = datetime.now()
                updated += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Updated {updated} stocks, {failed} failed",
        "updated": updated,
        "failed": failed,
    }
