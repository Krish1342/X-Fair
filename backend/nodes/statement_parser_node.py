"""
Statement Parser Node - Parses CSV/PDF financial statements
Stage 1: MVP - Statement Parser
"""
import logging
import pandas as pd
import io
from typing import Dict, Any, List
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class StatementParserNode:
    """Parses and processes financial statements"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Parse financial statements from user input"""
        try:
            user_query = state.get("user_query", "")
            
            # Check if user is trying to upload or parse data
            if any(keyword in user_query.lower() for keyword in [
                "statement", "csv", "data", "upload", "file", "transaction", "bank"
            ]):
                # Simulate parsing financial data (in real implementation, handle file uploads)
                parsed_data = self._simulate_statement_parsing()
                
                state["financial_data"]["transactions"] = parsed_data["transactions"]
                state["financial_data"]["summary"] = parsed_data["summary"]
                state["tools_used"] = state.get("tools_used", []) + ["statement_parser"]
                
                # Add analysis results
                state["analysis_results"]["statement_analysis"] = {
                    "total_transactions": len(parsed_data["transactions"]),
                    "total_income": parsed_data["summary"]["total_income"],
                    "total_expenses": parsed_data["summary"]["total_expenses"],
                    "net_flow": parsed_data["summary"]["net_flow"],
                    "top_categories": parsed_data["summary"]["top_categories"]
                }
                
                logger.info("Financial statement parsed successfully")
                
            else:
                # Handle general financial data queries
                state["analysis_results"]["statement_note"] = "No financial data provided for parsing"
            
            state["current_node"] = "statement_parser"
            
        except Exception as e:
            logger.error(f"Statement parsing error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _simulate_statement_parsing(self) -> Dict[str, Any]:
        """Simulate parsing of financial statement data"""
        # In a real implementation, this would parse actual CSV/PDF files
        sample_transactions = [
            {"date": "2024-01-01", "description": "Salary Deposit", "amount": 5000.00, "category": "Income"},
            {"date": "2024-01-02", "description": "Grocery Store", "amount": -150.00, "category": "Food"},
            {"date": "2024-01-03", "description": "Gas Station", "amount": -60.00, "category": "Transportation"},
            {"date": "2024-01-04", "description": "Utility Bill", "amount": -120.00, "category": "Utilities"},
            {"date": "2024-01-05", "description": "Restaurant", "amount": -85.00, "category": "Food"},
            {"date": "2024-01-06", "description": "Online Shopping", "amount": -200.00, "category": "Shopping"},
            {"date": "2024-01-07", "description": "Investment Contribution", "amount": -500.00, "category": "Investment"},
        ]
        
        # Calculate summary statistics
        total_income = sum(t["amount"] for t in sample_transactions if t["amount"] > 0)
        total_expenses = sum(abs(t["amount"]) for t in sample_transactions if t["amount"] < 0)
        net_flow = total_income - total_expenses
        
        # Category breakdown
        categories = {}
        for transaction in sample_transactions:
            category = transaction["category"]
            amount = abs(transaction["amount"]) if transaction["amount"] < 0 else 0
            categories[category] = categories.get(category, 0) + amount
        
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "transactions": sample_transactions,
            "summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_flow": net_flow,
                "top_categories": top_categories
            }
        }