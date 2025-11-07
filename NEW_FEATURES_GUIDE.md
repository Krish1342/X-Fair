# X-Fair - New Features Guide

## 🚀 New Features Added

### 1. Bulk Transaction Upload 📊

Upload multiple transactions at once using CSV or Excel files.

#### How to Use:

1. **From Dashboard or Transactions Page**: Click the "Bulk Upload" button
2. **Prepare Your File**: Create a CSV or Excel file with these columns:
   - `description` (Required): Transaction description
   - `amount` (Required): Transaction amount (negative for expenses, positive for income)
   - `date` (Required): Date in YYYY-MM-DD format (e.g., 2024-03-15)
   - `category` (Optional): Category name (will auto-detect if not provided)

#### Example CSV Format:

```csv
description,amount,date,category
Grocery Shopping,-150.50,2024-03-15,Food
Salary,5000.00,2024-03-01,Income
Netflix Subscription,-15.99,2024-03-10,Entertainment
```

#### Features:

- ✅ Supports CSV, XLS, and XLSX files
- ✅ Auto-detects categories using 60+ keywords
- ✅ Validates all data before import
- ✅ Shows detailed error messages for invalid rows
- ✅ Upload summary with success/error counts

---

### 2. UPI Transaction Integration 💳

Automatically extract transaction details from UPI SMS messages.

#### How to Use:

1. **From Dashboard or Transactions Page**: Click the "Add UPI" button
2. **Copy UPI SMS**: Copy the entire transaction SMS from your bank app
3. **Paste**: Paste it into the text area
4. **Process**: Click "Process UPI Message" to extract and save the transaction

#### Supported Banks & Apps:

- State Bank of India (SBI)
- HDFC Bank
- ICICI Bank
- Axis Bank
- Kotak Mahindra Bank
- Punjab National Bank (PNB)
- Bank of Baroda (BOB)
- Google Pay
- PhonePe
- Paytm

#### Example UPI Message:

```
Rs 500.00 debited from A/c XX1234 on 15-03-2024.
UPI Ref 410123456789. Paid to AMAZON
```

#### Auto-Extracted Information:

- ✅ Transaction amount
- ✅ Merchant/Payee name
- ✅ Reference number
- ✅ Transaction date
- ✅ Auto-assigned category (based on merchant)
- ✅ Bank/App identification

---

## 🎯 Category Auto-Detection

The system automatically detects categories based on keywords in transaction descriptions:

| Category          | Keywords                                                     |
| ----------------- | ------------------------------------------------------------ |
| 🍕 Food           | restaurant, cafe, food, grocery, swiggy, zomato, pizza, etc. |
| 🏠 Housing        | rent, mortgage, housing, property, maintenance, etc.         |
| 🚗 Transportation | uber, ola, fuel, petrol, metro, bus, cab, etc.               |
| 🎬 Entertainment  | netflix, spotify, movie, theatre, gaming, etc.               |
| 🏥 Healthcare     | hospital, doctor, pharmacy, medicine, clinic, etc.           |
| 🛍️ Shopping       | amazon, flipkart, shopping, mall, store, etc.                |
| 📚 Education      | tuition, books, course, school, college, etc.                |
| 💼 Bills          | electricity, water, gas, internet, mobile, etc.              |
| ✈️ Travel         | flight, hotel, airbnb, booking, vacation, etc.               |
| 💰 Savings        | savings, investment, mutual fund, stocks, etc.               |
| 👔 Subscriptions  | subscription, membership, premium, etc.                      |

---

## 🔧 Technical Details

### Backend APIs

#### Bulk Upload Endpoint

```
POST /upload/transactions/{user_id}
Content-Type: multipart/form-data

Response:
{
  "total_rows": 10,
  "success_count": 8,
  "error_count": 2,
  "errors": [
    {"row": 3, "error": "Invalid date format"},
    {"row": 7, "error": "Amount must be a number"}
  ]
}
```

#### UPI Upload Endpoint

```
POST /upload/upi/{user_id}
Content-Type: application/json

Body:
{
  "message": "Rs 500.00 debited from A/c XX1234..."
}

Response:
{
  "transaction_id": 123,
  "amount": 500.00,
  "merchant": "AMAZON",
  "category": "Shopping",
  "date": "2024-03-15",
  "reference_number": "410123456789",
  "bank_detected": "SBI"
}
```

---

## 📝 Best Practices

### For Bulk Upload:

1. **Validate your data** before uploading
2. **Use consistent date format** (YYYY-MM-DD)
3. **Check amount signs** (negative for expenses, positive for income)
4. **Review error messages** and fix invalid rows
5. **Start with a small file** to test format

### For UPI Integration:

1. **Copy complete SMS** - don't edit or truncate
2. **Check bank support** - ensure your bank is supported
3. **Verify extracted data** before saving
4. **Set up SMS forwarding** for automatic processing (future feature)

---

## 🐛 Troubleshooting

### Bulk Upload Issues:

**Problem**: "Invalid date format" error

- **Solution**: Use YYYY-MM-DD format (e.g., 2024-03-15)

**Problem**: "Amount must be a number" error

- **Solution**: Remove currency symbols, use only numbers and decimal point

**Problem**: File not accepted

- **Solution**: Ensure file is .csv, .xls, or .xlsx format

### UPI Upload Issues:

**Problem**: "Failed to parse UPI message"

- **Solution**: Ensure you copied the complete SMS without editing

**Problem**: Bank not detected

- **Solution**: Check if your bank is in the supported list, or manually add transaction

**Problem**: Wrong amount or date

- **Solution**: Verify SMS format matches bank's standard format

---

## 🔜 Coming Soon

- 📧 Email integration for automatic expense tracking
- 🤖 AI-powered duplicate detection
- 📊 Advanced transaction categorization rules
- 🔄 Scheduled imports from bank statements
- 📱 Mobile app with SMS auto-capture

---

## 💡 Tips

1. **Monthly Routine**: Upload bank statements at month-end for complete tracking
2. **UPI Habits**: Process UPI SMS daily to stay updated
3. **Category Review**: Check auto-assigned categories and adjust if needed
4. **Backup Data**: Export transactions regularly as CSV for backup

---

## 📞 Support

For issues or questions:

- Check the troubleshooting section above
- Review error messages carefully
- Contact support with error details and sample data (remove sensitive info)

---

**Last Updated**: 2024-03-15
**Version**: 1.0.0
