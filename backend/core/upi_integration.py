"""
UPI Integration Service for automatic expense tracking.

Provides multiple methods for UPI transaction integration:
1. SMS parsing (for devices that forward SMS)
2. Email parsing (for bank notification emails)
3. Webhook integration (for partnered payment apps)
4. Manual message paste endpoint

Supports major Indian banks and UPI apps like:
- Google Pay, PhonePe, Paytm
- SBI, HDFC, ICICI, Axis, Kotak, etc.
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class TransactionType(str, Enum):
    """Type of UPI transaction"""

    DEBIT = "debit"
    CREDIT = "credit"
    UNKNOWN = "unknown"


class BankType(str, Enum):
    """Supported bank types"""

    SBI = "sbi"
    HDFC = "hdfc"
    ICICI = "icici"
    AXIS = "axis"
    KOTAK = "kotak"
    PNB = "pnb"
    BOB = "bob"
    GENERIC = "generic"


# Comprehensive regex patterns for different banks and UPI apps
UPI_PATTERNS = {
    "sbi": {
        "amount": [
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:debited|credited)",
            r"(?:debited|credited).*?Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "merchant": [
            r"to\s+VPA\s+([^\s]+@[^\s]+)",
            r"to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+on",
        ],
        "ref_no": [
            r"UPI\s*Ref\s*No\s*[:\.]?\s*(\d+)",
            r"Ref\s*No\s*[:\.]?\s*([A-Z0-9]+)",
        ],
        "date": [
            r"on\s+(\d{1,2}-[A-Za-z]{3}-\d{2,4})",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
        ],
    },
    "hdfc": {
        "amount": [
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:debited|credited|spent|received)",
            r"INR\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "merchant": [
            r"at\s+([A-Z][^\s]+(?:\s+[A-Z][^\s]+)*)",
            r"to\s+([^\s]+@[^\s]+)",
        ],
        "ref_no": [
            r"Ref\s*no\s*[:\.]?\s*([A-Z0-9]+)",
            r"UPI/([A-Z0-9]+)",
        ],
        "date": [
            r"(\d{2}-\d{2}-\d{4})",
            r"(\d{2}/\d{2}/\d{4})",
        ],
    },
    "icici": {
        "amount": [
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"₹\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "merchant": [
            r"to\s+([^\s]+)",
            r"VPA:\s*([^\s]+@[^\s]+)",
        ],
        "ref_no": [
            r"Ref\s*no\s*[:\.]?\s*([A-Z0-9]+)",
        ],
        "date": [
            r"on\s+(\d{2}/\d{2}/\d{4})",
        ],
    },
    "phonepe": {
        "amount": [
            r"₹(\d+(?:,\d+)*(?:\.\d+)?)",
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "merchant": [
            r"to\s+([^\n]+)",
            r"@\s*([^\s]+)",
        ],
        "ref_no": [
            r"ID:\s*([A-Z0-9]+)",
            r"Transaction\s*ID:\s*([A-Z0-9]+)",
        ],
    },
    "gpay": {
        "amount": [
            r"₹(\d+(?:,\d+)*(?:\.\d+)?)",
            r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        ],
        "merchant": [
            r"to\s+([^\n]+)",
            r"Paid\s+([^\s]+)",
        ],
        "ref_no": [
            r"UPI\s*transaction\s*ID:\s*([A-Z0-9]+)",
        ],
    },
}

# Generic patterns that work across multiple banks
GENERIC_PATTERNS = {
    "amount": [
        r"Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        r"INR\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        r"₹\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:debited|credited|paid|received)",
    ],
    "merchant": [
        r"(?:to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"(?:to|from)\s+([^\s]+@[^\s]+)",
        r"VPA[:\s]+([^\s]+@[^\s]+)",
        r"at\s+([A-Z][^\s]+(?:\s+[A-Z][^\s]+)*)",
    ],
    "ref_no": [
        r"(?:Ref|Reference|UPI|Transaction|Txn)\s*(?:No|Number|ID)?[:\s]*([A-Z0-9]{10,})",
        r"([A-Z]{2,}\d{10,})",
    ],
    "date": [
        r"(\d{1,2}-\d{1,2}-\d{2,4})",
        r"(\d{1,2}/\d{1,2}/\d{2,4})",
        r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})",
    ],
}


def detect_bank_from_message(message: str) -> BankType:
    """
    Detect which bank or UPI app sent the message based on content.
    """
    message_lower = message.lower()

    if any(word in message_lower for word in ["sbi", "state bank", "onlinesbi"]):
        return BankType.SBI
    elif any(word in message_lower for word in ["hdfc", "hdfcbank"]):
        return BankType.HDFC
    elif any(word in message_lower for word in ["icici", "icicibank"]):
        return BankType.ICICI
    elif any(word in message_lower for word in ["axis", "axisbank"]):
        return BankType.AXIS
    elif any(word in message_lower for word in ["kotak", "kotakbank"]):
        return BankType.KOTAK
    elif "phonepe" in message_lower:
        return "phonepe"
    elif any(word in message_lower for word in ["google pay", "gpay", "tez"]):
        return "gpay"

    return BankType.GENERIC


def detect_transaction_type(message: str) -> TransactionType:
    """
    Detect if transaction is debit (expense) or credit (income).
    """
    message_lower = message.lower()

    # Credit indicators
    credit_keywords = [
        "credited",
        "received",
        "credit",
        "deposited",
        "payment received",
        "refund",
        "cashback",
    ]

    # Debit indicators
    debit_keywords = [
        "debited",
        "paid",
        "debit",
        "withdrawn",
        "sent",
        "payment made",
        "transferred",
        "spent",
    ]

    credit_score = sum(1 for keyword in credit_keywords if keyword in message_lower)
    debit_score = sum(1 for keyword in debit_keywords if keyword in message_lower)

    if credit_score > debit_score:
        return TransactionType.CREDIT
    elif debit_score > credit_score:
        return TransactionType.DEBIT

    return TransactionType.UNKNOWN


def extract_field(message: str, patterns: List[str]) -> Optional[str]:
    """
    Extract a field from message using a list of regex patterns.
    Returns first successful match.
    """
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_amount(amount_str: str) -> float:
    """Parse amount string to float, handling Indian number format."""
    if not amount_str:
        return 0.0
    # Remove currency symbols and commas
    cleaned = amount_str.replace(",", "").replace("₹", "").replace("Rs", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object, trying multiple formats."""
    if not date_str:
        return None

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%d %b %Y",
        "%d %b %y",
        "%Y-%m-%d",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


class UPITransactionParser:
    """
    Main class for parsing UPI transaction messages.
    Supports multiple banks and UPI apps.
    """

    def __init__(self):
        self.patterns = UPI_PATTERNS
        self.generic_patterns = GENERIC_PATTERNS

    def parse(self, message: str) -> Dict[str, Any]:
        """
        Parse UPI transaction message and extract all relevant information.

        Args:
            message: Raw SMS/notification message text

        Returns:
            Dictionary with transaction details:
            - success: bool - whether parsing was successful
            - transaction_type: TransactionType
            - amount: float
            - merchant: str (optional)
            - ref_no: str (optional)
            - date: datetime (optional)
            - description: str
            - raw_message: str
            - bank: BankType
        """
        result = {
            "success": False,
            "transaction_type": TransactionType.UNKNOWN,
            "amount": 0.0,
            "merchant": None,
            "ref_no": None,
            "date": None,
            "description": "",
            "raw_message": message,
            "bank": BankType.GENERIC,
        }

        # Detect bank/app
        bank = detect_bank_from_message(message)
        result["bank"] = bank

        # Detect transaction type
        result["transaction_type"] = detect_transaction_type(message)

        # Get appropriate patterns
        if bank in self.patterns:
            patterns = self.patterns[bank]
        else:
            patterns = self.generic_patterns

        # Extract amount
        amount_str = extract_field(message, patterns.get("amount", []))
        if amount_str:
            result["amount"] = parse_amount(amount_str)
            result["success"] = True
        else:
            # Fallback to generic patterns
            amount_str = extract_field(message, self.generic_patterns["amount"])
            if amount_str:
                result["amount"] = parse_amount(amount_str)
                result["success"] = True

        # Extract merchant/payee
        merchant = extract_field(message, patterns.get("merchant", []))
        if not merchant:
            merchant = extract_field(message, self.generic_patterns["merchant"])
        result["merchant"] = merchant

        # Extract reference number
        ref_no = extract_field(message, patterns.get("ref_no", []))
        if not ref_no:
            ref_no = extract_field(message, self.generic_patterns["ref_no"])
        result["ref_no"] = ref_no

        # Extract date
        date_str = extract_field(message, patterns.get("date", []))
        if not date_str:
            date_str = extract_field(message, self.generic_patterns["date"])
        if date_str:
            parsed_date = parse_date(date_str)
            if parsed_date:
                result["date"] = parsed_date
            else:
                result["date"] = datetime.now()
        else:
            result["date"] = datetime.now()

        # Generate description
        result["description"] = self._generate_description(result)

        return result

    def _generate_description(self, data: Dict[str, Any]) -> str:
        """Generate a user-friendly description from parsed data."""
        tx_type = data["transaction_type"]
        merchant = data.get("merchant")
        amount = data.get("amount", 0.0)

        if tx_type == TransactionType.DEBIT:
            action = "Payment to"
        elif tx_type == TransactionType.CREDIT:
            action = "Payment from"
        else:
            action = "Transaction with"

        if merchant:
            # Clean up merchant name
            merchant = merchant.replace("@", " ").strip()
            return f"{action} {merchant}"

        return "UPI Transaction"

    def batch_parse(self, messages: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple UPI messages in batch.

        Args:
            messages: List of raw message strings

        Returns:
            List of parsed transaction dictionaries
        """
        return [self.parse(msg) for msg in messages]


# Export singleton parser instance
upi_parser = UPITransactionParser()


def parse_upi_message(message: str) -> Dict[str, Any]:
    """
    Convenience function to parse a single UPI message.

    Args:
        message: Raw UPI SMS/notification text

    Returns:
        Parsed transaction dictionary
    """
    return upi_parser.parse(message)


def validate_parsed_transaction(parsed: Dict[str, Any]) -> bool:
    """
    Validate that a parsed transaction has minimum required fields.

    Args:
        parsed: Parsed transaction dictionary

    Returns:
        True if valid, False otherwise
    """
    return (
        parsed.get("success") is True
        and parsed.get("amount", 0.0) > 0
        and parsed.get("transaction_type") != TransactionType.UNKNOWN
    )


# Example usage and test messages
EXAMPLE_MESSAGES = [
    # SBI
    "Rs 500.00 debited from A/c **1234 on 15-Jan-24 to VPA merchant@paytm (UPI Ref No 123456789). Avl Bal: Rs 10000.00",
    # HDFC
    "Rs. 1,250.50 debited from your HDFC Bank A/c XX1234 on 16-Jan-24. Info: UPI/123456789/Payment to merchant@phonepe. Avl bal Rs 25000.00",
    # ICICI
    "Rs 750.00 debited from A/c XX5678 on 17-Jan-24 for VPA: merchant@paytm. UPI Ref no 987654321. Avl bal: Rs 15000",
    # PhonePe
    "You paid ₹300 to Merchant Name via PhonePe. Transaction ID: PP123456789. Download app: bit.ly/phonepe",
    # Google Pay
    "You sent ₹500 to Merchant Name using Google Pay. UPI transaction ID: 123456789",
    # Generic credit
    "Rs 2000.00 credited to A/c **1234 on 18-Jan-24 from sender@upi. Ref No: ABC123456789",
]


if __name__ == "__main__":
    # Test the parser
    print("Testing UPI Message Parser\n")
    print("=" * 80)

    for i, msg in enumerate(EXAMPLE_MESSAGES, 1):
        print(f"\nTest {i}:")
        print(f"Message: {msg[:70]}...")

        parsed = parse_upi_message(msg)

        print(f"Success: {parsed['success']}")
        print(f"Bank: {parsed['bank']}")
        print(f"Type: {parsed['transaction_type']}")
        print(f"Amount: ₹{parsed['amount']:.2f}")
        print(f"Merchant: {parsed['merchant']}")
        print(f"Ref No: {parsed['ref_no']}")
        print(f"Description: {parsed['description']}")
        print(f"Valid: {validate_parsed_transaction(parsed)}")
        print("-" * 80)
