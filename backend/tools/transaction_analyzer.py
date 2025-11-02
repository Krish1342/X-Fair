import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from agents.nodes import FinanceAgentState
from tools.data_loader import DataLoader

class TransactionAnalyzerTool:
    """Analyzes transaction data to answer spending-related queries"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Main entry point for transaction analysis"""
        transactions = state.get("context", {}).get("transactions")
        if transactions is None or transactions.empty:
            state["analysis_results"]["transaction_analyzer"] = {
                "error": "No transaction data available"
            }
            return state
        
        query = state.get("user_query", "").lower()
        analysis = {}
        
        # Determine analysis type based on query keywords
        if any(word in query for word in ["food", "dining", "restaurant", "eat"]):
            analysis = self._analyze_food_spending(transactions, query)
        elif any(word in query for word in ["this month", "monthly", "current month"]):
            analysis = self._analyze_monthly_spending(transactions, query)
        elif any(word in query for word in ["category", "categories"]):
            analysis = self._analyze_spending_by_category(transactions)
        elif any(word in query for word in ["total", "spent", "spending"]):
            analysis = self._analyze_total_spending(transactions, query)
        else:
            # Default comprehensive analysis
            analysis = self._analyze_recent_spending(transactions)
        
        state["analysis_results"]["transaction_analyzer"] = analysis
        state["tools_used"].append("transaction_analyzer")
        return state
    
    def _analyze_food_spending(self, df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Analyze food and dining spending"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Filter for food categories
        food_categories = ["Food & Dining", "Groceries"]
        food_transactions = df[df['category'].isin(food_categories)]
        
        # Current month food spending
        current_month_food = food_transactions[
            (food_transactions['date'].dt.month == current_month) &
            (food_transactions['date'].dt.year == current_year)
        ]
        
        total_food_spent = abs(current_month_food['amount'].sum())
        transaction_count = len(current_month_food)
        avg_transaction = total_food_spent / transaction_count if transaction_count > 0 else 0
        
        # Compare to previous month
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        
        prev_month_food = food_transactions[
            (food_transactions['date'].dt.month == prev_month) &
            (food_transactions['date'].dt.year == prev_year)
        ]
        prev_total = abs(prev_month_food['amount'].sum())
        
        change_amount = total_food_spent - prev_total
        change_percent = ((change_amount / prev_total) * 100) if prev_total > 0 else 0
        
        # Top merchants
        top_merchants = current_month_food.groupby('merchant')['amount'].sum().abs().sort_values(ascending=False).head(3)
        
        return {
            "category": "Food & Dining Analysis",
            "current_month_total": round(total_food_spent, 2),
            "transaction_count": transaction_count,
            "average_transaction": round(avg_transaction, 2),
            "previous_month_total": round(prev_total, 2),
            "month_over_month_change": round(change_amount, 2),
            "change_percentage": round(change_percent, 1),
            "top_merchants": top_merchants.to_dict()
        }
    
    def _analyze_monthly_spending(self, df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Analyze current month spending"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_transactions = df[
            (df['date'].dt.month == current_month) &
            (df['date'].dt.year == current_year)
        ]
        
        # Separate income and expenses
        expenses = current_month_transactions[current_month_transactions['amount'] < 0]
        income = current_month_transactions[current_month_transactions['amount'] > 0]
        
        total_expenses = abs(expenses['amount'].sum())
        total_income = income['amount'].sum()
        net_cash_flow = total_income - total_expenses
        
        # Spending by category
        category_spending = expenses.groupby('category')['amount'].sum().abs().sort_values(ascending=False)
        
        return {
            "period": f"{datetime.now().strftime('%B %Y')}",
            "total_expenses": round(total_expenses, 2),
            "total_income": round(total_income, 2),
            "net_cash_flow": round(net_cash_flow, 2),
            "transaction_count": len(current_month_transactions),
            "expense_count": len(expenses),
            "category_breakdown": category_spending.to_dict(),
            "top_category": category_spending.index[0] if len(category_spending) > 0 else None,
            "top_category_amount": round(category_spending.iloc[0], 2) if len(category_spending) > 0 else 0
        }
    
    def _analyze_spending_by_category(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze spending patterns by category"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_expenses = df[
            (df['date'].dt.month == current_month) &
            (df['date'].dt.year == current_year) &
            (df['amount'] < 0)
        ]
        
        category_analysis = {}
        
        for category in current_month_expenses['category'].unique():
            category_data = current_month_expenses[current_month_expenses['category'] == category]
            total_spent = abs(category_data['amount'].sum())
            transaction_count = len(category_data)
            avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
            
            category_analysis[category] = {
                "total_spent": round(total_spent, 2),
                "transaction_count": transaction_count,
                "average_transaction": round(avg_transaction, 2),
                "percentage_of_total": 0  # Will calculate after getting total
            }
        
        total_expenses = sum([cat["total_spent"] for cat in category_analysis.values()])
        
        # Calculate percentages
        for category in category_analysis:
            if total_expenses > 0:
                category_analysis[category]["percentage_of_total"] = round(
                    (category_analysis[category]["total_spent"] / total_expenses) * 100, 1
                )
        
        return {
            "period": f"{datetime.now().strftime('%B %Y')}",
            "total_expenses": round(total_expenses, 2),
            "category_breakdown": category_analysis,
            "category_count": len(category_analysis)
        }
    
    def _analyze_total_spending(self, df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Analyze total spending over specified period"""
        # Default to current month if no specific period mentioned
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        if "week" in query.lower():
            # Last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            period_transactions = df[
                (df['date'] >= start_date) & (df['date'] <= end_date)
            ]
            period_name = "Last 7 days"
        else:
            # Current month
            period_transactions = df[
                (df['date'].dt.month == current_month) &
                (df['date'].dt.year == current_year)
            ]
            period_name = f"{datetime.now().strftime('%B %Y')}"
        
        expenses = period_transactions[period_transactions['amount'] < 0]
        income = period_transactions[period_transactions['amount'] > 0]
        
        return {
            "period": period_name,
            "total_expenses": round(abs(expenses['amount'].sum()), 2),
            "total_income": round(income['amount'].sum(), 2),
            "net_amount": round(income['amount'].sum() + expenses['amount'].sum(), 2),
            "expense_transactions": len(expenses),
            "income_transactions": len(income),
            "largest_expense": {
                "amount": round(abs(expenses['amount'].min()), 2) if len(expenses) > 0 else 0,
                "description": expenses.loc[expenses['amount'].idxmin(), 'description'] if len(expenses) > 0 else "",
                "merchant": expenses.loc[expenses['amount'].idxmin(), 'merchant'] if len(expenses) > 0 else ""
            }
        }
    
    def _analyze_recent_spending(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Provide a comprehensive recent spending analysis"""
        # Last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        recent_transactions = df[
            (df['date'] >= start_date) & (df['date'] <= end_date)
        ]
        
        expenses = recent_transactions[recent_transactions['amount'] < 0]
        daily_spending = expenses.groupby(expenses['date'].dt.date)['amount'].sum().abs()
        
        return {
            "period": "Last 30 days",
            "total_expenses": round(abs(expenses['amount'].sum()), 2),
            "daily_average": round(daily_spending.mean(), 2),
            "highest_spending_day": {
                "date": str(daily_spending.idxmax()) if len(daily_spending) > 0 else None,
                "amount": round(daily_spending.max(), 2) if len(daily_spending) > 0 else 0
            },
            "transaction_count": len(expenses),
            "top_categories": expenses.groupby('category')['amount'].sum().abs().sort_values(ascending=False).head(3).to_dict()
        }