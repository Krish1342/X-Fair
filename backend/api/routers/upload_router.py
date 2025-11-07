"""
Upload router for bulk transaction imports.
Supports CSV and Excel file formats with automatic category detection.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any
import csv
import io
import pandas as pd

from db.database import get_db
from db import models as dbm
from api.deps import safe_uid, get_user_or_404
from core.upi_integration import (
    parse_upi_message,
    validate_parsed_transaction,
    TransactionType,
)

router = APIRouter()

# Category keywords for auto-detection
CATEGORY_KEYWORDS = {
    "Food & Dining": [
        "restaurant",
        "cafe",
        "coffee",
        "food",
        "dining",
        "pizza",
        "burger",
        "grocery",
        "groceries",
        "swiggy",
        "zomato",
        "uber eats",
    ],
    "Transportation": [
        "uber",
        "lyft",
        "taxi",
        "gas",
        "fuel",
        "petrol",
        "parking",
        "toll",
        "metro",
        "bus",
        "train",
        "ola",
    ],
    "Shopping": [
        "amazon",
        "flipkart",
        "mall",
        "store",
        "shop",
        "clothing",
        "fashion",
        "myntra",
        "ajio",
    ],
    "Entertainment": [
        "movie",
        "cinema",
        "netflix",
        "spotify",
        "prime",
        "hotstar",
        "concert",
        "game",
        "gaming",
    ],
    "Utilities": [
        "electricity",
        "power",
        "water",
        "gas bill",
        "internet",
        "broadband",
        "mobile",
        "phone bill",
    ],
    "Housing": ["rent", "mortgage", "maintenance", "housing"],
    "Health & Fitness": [
        "doctor",
        "hospital",
        "pharmacy",
        "medicine",
        "gym",
        "fitness",
        "yoga",
        "medical",
    ],
    "Travel": ["hotel", "flight", "airbnb", "oyo", "booking", "travel", "vacation"],
    "Education": [
        "school",
        "college",
        "course",
        "udemy",
        "coursera",
        "tuition",
        "books",
    ],
    "Savings": ["savings", "investment", "mutual fund", "sip", "fixed deposit"],
    "Subscriptions": ["subscription", "membership", "premium"],
}


def detect_category(description: str) -> str:
    """
    Automatically detect category based on transaction description keywords.
    Returns the most likely category or "Uncategorized" if no match found.
    """
    description_lower = description.lower()

    # Count matches for each category
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in description_lower)
        if score > 0:
            category_scores[category] = score

    # Return category with highest score
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]

    return "Uncategorized"


def validate_transaction_row(row: Dict[str, Any], row_num: int) -> Dict[str, Any]:
    """
    Validate and normalize a transaction row from CSV/Excel.
    Returns validated data or raises ValueError with details.
    """
    errors = []

    # Required fields
    if not row.get("description") or str(row.get("description")).strip() == "":
        errors.append(f"Row {row_num}: Description is required")

    if not row.get("amount"):
        errors.append(f"Row {row_num}: Amount is required")

    # Validate amount
    try:
        amount = float(
            str(row["amount"])
            .replace(",", "")
            .replace("₹", "")
            .replace("Rs", "")
            .strip()
        )
        # If transaction_type is specified, respect it; otherwise use amount sign
        if row.get("transaction_type"):
            tx_type = str(row["transaction_type"]).lower().strip()
            if tx_type in ["expense", "debit", "payment"]:
                amount = -abs(amount)
            elif tx_type in ["income", "credit", "received"]:
                amount = abs(amount)
    except (ValueError, TypeError):
        errors.append(f"Row {row_num}: Invalid amount format")
        amount = 0.0

    # Validate date
    date_obj = datetime.now().date()
    if row.get("date"):
        date_str = str(row["date"]).strip()
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        else:
            errors.append(
                f"Row {row_num}: Invalid date format (use YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY)"
            )

    # Auto-detect category if not provided
    category = row.get("category", "").strip() or detect_category(
        row.get("description", "")
    )

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "description": str(row["description"]).strip(),
        "amount": amount,
        "date": date_obj,
        "category": category,
        "merchant": row.get("merchant", "").strip() or None,
        "account_type": row.get("account_type", "").strip() or None,
    }


@router.post("/upload/transactions/{user_id}")
async def upload_transactions(
    user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Bulk upload transactions from CSV or Excel file.

    Expected columns:
    - description (required): Transaction description
    - amount (required): Transaction amount (positive for income, negative for expenses)
    - date (optional): Transaction date in YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY format
    - category (optional): Will be auto-detected if not provided
    - merchant (optional): Merchant/payee name
    - account_type (optional): Account type
    - transaction_type (optional): "expense", "income", "debit", or "credit"

    Returns:
    - Summary of uploaded transactions with success/failure counts
    """
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)

    # Validate file type
    filename = file.filename.lower()
    if not (
        filename.endswith(".csv")
        or filename.endswith(".xlsx")
        or filename.endswith(".xls")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a CSV or Excel (.xlsx, .xls) file",
        )

    try:
        # Read file content
        content = await file.read()

        # Parse based on file type
        if filename.endswith(".csv"):
            # Parse CSV
            text_content = content.decode("utf-8-sig")  # Handle BOM
            csv_reader = csv.DictReader(io.StringIO(text_content))
            rows = list(csv_reader)
        else:
            # Parse Excel
            df = pd.read_excel(io.BytesIO(content))
            rows = df.to_dict("records")

        if not rows:
            raise HTTPException(
                status_code=400, detail="File is empty or has no data rows"
            )

        # Validate and process transactions
        success_count = 0
        error_count = 0
        errors = []
        added_transactions = []

        for idx, row in enumerate(
            rows, start=2
        ):  # Start from 2 (assuming row 1 is header)
            try:
                # Validate and normalize row
                validated_data = validate_transaction_row(row, idx)

                # Create transaction
                transaction = dbm.Transaction(
                    user_id=uid,
                    description=validated_data["description"],
                    amount=validated_data["amount"],
                    date=validated_data["date"],
                    category=validated_data["category"],
                    merchant=validated_data["merchant"],
                    account_type=validated_data["account_type"],
                )

                db.add(transaction)
                db.flush()  # Get ID without committing

                added_transactions.append(
                    {
                        "id": transaction.id,
                        "description": transaction.description,
                        "amount": transaction.amount,
                        "date": transaction.date.isoformat(),
                        "category": transaction.category,
                    }
                )

                success_count += 1

            except ValueError as e:
                error_count += 1
                errors.append(str(e))
            except Exception as e:
                error_count += 1
                errors.append(f"Row {idx}: {str(e)}")

        # Commit all successful transactions
        if success_count > 0:
            db.commit()
        else:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"No valid transactions found. Errors: {'; '.join(errors[:5])}",
            )

        return {
            "success": True,
            "message": f"Successfully uploaded {success_count} transactions",
            "summary": {
                "total_rows": len(rows),
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors[:10],  # Return first 10 errors
            },
            "transactions": added_transactions[:20],  # Return first 20 transactions
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/upload/upi-message/{user_id}")
async def upload_upi_message(
    user_id: str, message: str = Form(...), db: Session = Depends(get_db)
):
    """
    Parse and add a transaction from a UPI SMS/notification message.

    Supports common UPI message formats from Indian banks like:
    - SBI, HDFC, ICICI, Axis, Kotak, PNB, BOB, etc.
    - Google Pay, PhonePe, Paytm

    Example message:
    "Rs 500.00 debited from A/c **1234 on 01-Jan-24 to VPA merchant@upi (UPI Ref No 123456789). Avl Bal: Rs 10000.00"
    """
    uid = safe_uid(user_id)
    get_user_or_404(db, uid)

    if not message or message.strip() == "":
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Parse UPI message using the advanced parser
        parsed = parse_upi_message(message)

        # Validate parsed data
        if not validate_parsed_transaction(parsed):
            raise HTTPException(
                status_code=400,
                detail="Could not extract valid transaction details from message. Please check the message format.",
            )

        # Determine amount sign based on transaction type
        amount = parsed["amount"]
        if parsed["transaction_type"] == TransactionType.DEBIT:
            amount = -abs(amount)
        elif parsed["transaction_type"] == TransactionType.CREDIT:
            amount = abs(amount)

        # Auto-detect category
        category = detect_category(parsed["description"])

        # Create transaction
        transaction = dbm.Transaction(
            user_id=uid,
            description=parsed["description"],
            amount=amount,
            date=parsed.get("date", datetime.now()).date(),
            category=category,
            merchant=parsed.get("merchant"),
            account_type="UPI",
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return {
            "success": True,
            "message": "Transaction added from UPI message",
            "transaction": {
                "id": transaction.id,
                "description": transaction.description,
                "amount": transaction.amount,
                "date": transaction.date.isoformat(),
                "category": transaction.category,
                "merchant": transaction.merchant,
                "account_type": transaction.account_type,
            },
            "parsed_data": {
                "bank": parsed.get("bank"),
                "transaction_type": parsed.get("transaction_type"),
                "ref_no": parsed.get("ref_no"),
                "success": parsed.get("success"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to process UPI message: {str(e)}"
        )
