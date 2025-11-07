# UPI Transaction Integration Guide

## Overview

The X-Fair finance application now includes comprehensive UPI transaction integration for automatic expense tracking. This feature allows users to automatically import transactions from UPI payment messages, eliminating manual entry.

## Features

### 1. **Multi-Bank Support**

- State Bank of India (SBI)
- HDFC Bank
- ICICI Bank
- Axis Bank
- Kotak Mahindra Bank
- Punjab National Bank (PNB)
- Bank of Baroda (BOB)
- Generic format support for other banks

### 2. **UPI App Support**

- Google Pay (GPay)
- PhonePe
- Paytm
- Amazon Pay
- Other UPI apps

### 3. **Automatic Detection**

- Bank/app detection from message
- Transaction type (debit/credit)
- Amount extraction (supports ₹, Rs., INR formats)
- Merchant/payee identification
- Reference number extraction
- Date parsing (multiple formats)
- Category auto-detection

### 4. **Bulk Upload Support**

- CSV file upload
- Excel (.xlsx, .xls) file upload
- Automatic data validation
- Category auto-detection
- Error reporting with row numbers

## API Endpoints

### 1. Parse Single UPI Message

**Endpoint:** `POST /api/v1/upload/upi-message/{user_id}`

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/upload/upi-message/1" \
  -F "message=Rs 500.00 debited from A/c **1234 on 15-Jan-24 to VPA merchant@paytm (UPI Ref No 123456789)"
```

**Response:**

```json
{
  "success": true,
  "message": "Transaction added from UPI message",
  "transaction": {
    "id": 123,
    "description": "Payment to merchant@paytm",
    "amount": -500.0,
    "date": "2024-01-15",
    "category": "Shopping",
    "merchant": "merchant@paytm",
    "account_type": "UPI"
  },
  "parsed_data": {
    "bank": "sbi",
    "transaction_type": "debit",
    "ref_no": "123456789",
    "success": true
  }
}
```

### 2. Bulk Upload CSV/Excel

**Endpoint:** `POST /api/v1/upload/transactions/{user_id}`

**CSV Format:**

```csv
description,amount,date,category,merchant,transaction_type
Swiggy Order,450.50,2024-01-15,Food & Dining,Swiggy,expense
Salary Credit,50000,2024-01-01,Income,,income
Metro Recharge,500,2024-01-10,Transportation,Delhi Metro,expense
```

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/upload/transactions/1" \
  -F "file=@transactions.csv"
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully uploaded 3 transactions",
  "summary": {
    "total_rows": 3,
    "success_count": 3,
    "error_count": 0,
    "errors": []
  },
  "transactions": [
    {
      "id": 124,
      "description": "Swiggy Order",
      "amount": -450.5,
      "date": "2024-01-15",
      "category": "Food & Dining"
    }
    // ... more transactions
  ]
}
```

## Usage Examples

### Frontend Integration

#### React Example

```javascript
// Upload UPI Message
async function uploadUPIMessage(userId, message) {
  const formData = new FormData();
  formData.append("message", message);

  const response = await fetch(`/api/v1/upload/upi-message/${userId}`, {
    method: "POST",
    body: formData,
  });

  return await response.json();
}

// Upload CSV File
async function uploadTransactionsFile(userId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`/api/v1/upload/transactions/${userId}`, {
    method: "POST",
    body: formData,
  });

  return await response.json();
}

// Usage
const message = "Rs 500 debited from A/c **1234 on 15-Jan-24 to merchant@upi";
const result = await uploadUPIMessage(1, message);
console.log(result);
```

### Mobile App Integration

#### SMS Forwarding (Android)

You can create an Android app that automatically forwards UPI SMS to your backend:

```kotlin
class SMSReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            for (message in messages) {
                val sender = message.displayOriginatingAddress
                val body = message.messageBody

                // Check if it's a UPI message
                if (isUPIMessage(sender, body)) {
                    // Forward to backend
                    uploadUPIMessage(body)
                }
            }
        }
    }

    private fun isUPIMessage(sender: String, body: String): Boolean {
        val upiKeywords = listOf("UPI", "debited", "credited", "VPA", "Ref No")
        return upiKeywords.any { body.contains(it, ignoreCase = true) }
    }
}
```

## Supported Message Formats

### SBI Format

```
Rs 500.00 debited from A/c **1234 on 15-Jan-24 to VPA merchant@paytm (UPI Ref No 123456789). Avl Bal: Rs 10000.00
```

### HDFC Format

```
Rs. 1,250.50 debited from your HDFC Bank A/c XX1234 on 16-Jan-24. Info: UPI/123456789/Payment to merchant@phonepe. Avl bal Rs 25000.00
```

### ICICI Format

```
Rs 750.00 debited from A/c XX5678 on 17-Jan-24 for VPA: merchant@paytm. UPI Ref no 987654321. Avl bal: Rs 15000
```

### PhonePe Format

```
You paid ₹300 to Merchant Name via PhonePe. Transaction ID: PP123456789.
```

### Google Pay Format

```
You sent ₹500 to Merchant Name using Google Pay. UPI transaction ID: 123456789
```

## Category Auto-Detection

The system automatically detects categories based on keywords in the transaction description:

| Category         | Keywords                                       |
| ---------------- | ---------------------------------------------- |
| Food & Dining    | restaurant, cafe, coffee, food, swiggy, zomato |
| Transportation   | uber, ola, taxi, gas, fuel, metro, bus         |
| Shopping         | amazon, flipkart, mall, myntra, ajio           |
| Entertainment    | movie, netflix, spotify, prime, hotstar        |
| Utilities        | electricity, water, gas bill, internet, mobile |
| Housing          | rent, mortgage, maintenance                    |
| Health & Fitness | doctor, hospital, pharmacy, gym, yoga          |
| Travel           | hotel, flight, airbnb, oyo, booking            |
| Education        | school, college, course, udemy, tuition        |
| Savings          | savings, investment, mutual fund, sip          |

## Error Handling

The API provides detailed error messages for troubleshooting:

### Invalid Message Format

```json
{
  "detail": "Could not extract valid transaction details from message. Please check the message format."
}
```

### Empty File

```json
{
  "detail": "File is empty or has no data rows"
}
```

### Row Validation Errors

```json
{
  "summary": {
    "total_rows": 10,
    "success_count": 8,
    "error_count": 2,
    "errors": ["Row 3: Invalid amount format", "Row 7: Description is required"]
  }
}
```

## Security Considerations

1. **Authentication Required**: All upload endpoints require user authentication
2. **User Isolation**: Transactions are strictly associated with the authenticated user
3. **Input Validation**: All inputs are validated and sanitized
4. **Rate Limiting**: Consider implementing rate limits for upload endpoints
5. **File Size Limits**: CSV/Excel uploads are limited to prevent abuse

## Best Practices

### For Users

1. **Regular Imports**: Import UPI messages regularly to keep data up-to-date
2. **Review Categories**: Auto-detected categories may need adjustment
3. **Bulk Uploads**: Use CSV/Excel for historical data import
4. **Message Cleanup**: Remove sensitive information before uploading

### For Developers

1. **Error Handling**: Always handle upload errors gracefully
2. **Progress Indicators**: Show upload progress for bulk files
3. **Preview**: Allow users to preview transactions before finalizing
4. **Duplicate Detection**: Implement duplicate transaction detection
5. **Batch Processing**: Process large files in batches

## Future Enhancements

1. **Automatic SMS Forwarding**: Native mobile app integration
2. **Email Integration**: Parse bank notification emails
3. **Webhook Support**: Real-time integration with payment apps
4. **OCR Support**: Extract data from transaction screenshots
5. **Duplicate Detection**: Automatic duplicate transaction detection
6. **Smart Categorization**: ML-based category prediction
7. **Multi-currency Support**: Support for international transactions

## Troubleshooting

### Message Not Parsing

**Issue**: UPI message not being parsed correctly

**Solutions**:

- Verify message format matches supported banks
- Check for special characters or encoding issues
- Try using generic patterns
- Contact support with message format

### Wrong Category Assignment

**Issue**: Transactions assigned to wrong category

**Solutions**:

- Manually update category after import
- Add custom keywords to category detection
- Use specific descriptions in transactions

### File Upload Fails

**Issue**: CSV/Excel file upload returns errors

**Solutions**:

- Check file format (CSV or Excel only)
- Verify column headers match expected format
- Ensure date formats are consistent
- Check for empty required fields

## Support

For issues or feature requests:

- GitHub Issues: [repository-url]
- Email: support@xfair.com
- Documentation: [docs-url]

## Changelog

### Version 1.0.0 (Current)

- Initial UPI integration
- Multi-bank support
- CSV/Excel bulk upload
- Auto category detection
- Comprehensive error handling
