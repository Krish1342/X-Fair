"""
Budget Analyzer Node - Categorizes and computes budget analysis
Stage 1: MVP - Budget Analyzer
"""
import logging
from typing import Dict, Any, List
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class BudgetAnalyzerNode:
    """Analyzes budget and spending patterns"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Analyze budget and spending patterns"""
        try:
            financial_data = state.get("financial_data", {})
            transactions = financial_data.get("transactions", [])
            
            if transactions:
                budget_analysis = self._analyze_budget(transactions)
                state["analysis_results"]["budget_analysis"] = budget_analysis
                state["tools_used"] = state.get("tools_used", []) + ["budget_analyzer"]
                
                # Generate budget insights
                insights = self._generate_budget_insights(budget_analysis)
                state["analysis_results"]["budget_insights"] = insights
                
                logger.info("Budget analysis completed")
            else:
                # Create sample budget analysis for demonstration
                sample_analysis = self._create_sample_budget_analysis()
                state["analysis_results"]["budget_analysis"] = sample_analysis
                state["tools_used"] = state.get("tools_used", []) + ["budget_analyzer"]
            
            state["current_node"] = "budget_analyzer"
            
        except Exception as e:
            logger.error(f"Budget analysis error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _analyze_budget(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Perform budget analysis on transactions"""
        # Categorize expenses
        category_totals = {}
        monthly_trends = {}
        
        for transaction in transactions:
            if transaction["amount"] < 0:  # Expense
                category = transaction["category"]
                amount = abs(transaction["amount"])
                category_totals[category] = category_totals.get(category, 0) + amount
                
                # Monthly tracking (simplified)
                month = transaction["date"][:7]  # YYYY-MM
                if month not in monthly_trends:
                    monthly_trends[month] = {}
                monthly_trends[month][category] = monthly_trends[month].get(category, 0) + amount
        
        # Calculate percentages
        total_expenses = sum(category_totals.values())
        category_percentages = {
            category: (amount / total_expenses) * 100 
            for category, amount in category_totals.items()
        }
        
        # Identify budget alerts
        alerts = []
        for category, percentage in category_percentages.items():
            if percentage > 30:  # Over 30% in one category
                alerts.append(f"High spending in {category}: {percentage:.1f}% of budget")
        
        return {
            "category_totals": category_totals,
            "category_percentages": category_percentages,
            "monthly_trends": monthly_trends,
            "total_expenses": total_expenses,
            "alerts": alerts,
            "recommendations": self._generate_recommendations(category_percentages)
        }
    
    def _generate_budget_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable budget insights"""
        insights = []
        
        category_percentages = analysis["category_percentages"]
        
        # Top spending categories
        top_category = max(category_percentages, key=category_percentages.get)
        insights.append(f"Your highest spending category is {top_category} at {category_percentages[top_category]:.1f}%")
        
        # Budget balance
        if category_percentages.get("Food", 0) > 15:
            insights.append("Consider meal planning to reduce food expenses")
        
        if category_percentages.get("Shopping", 0) > 10:
            insights.append("Review discretionary spending for potential savings")
        
        # Positive insights
        if category_percentages.get("Investment", 0) > 10:
            insights.append("Great job prioritizing investments!")
        
        return insights
    
    def _generate_recommendations(self, category_percentages: Dict[str, float]) -> List[str]:
        """Generate budget recommendations"""
        recommendations = []
        
        # 50/30/20 rule guidance
        essentials = ["Food", "Utilities", "Transportation"]
        essential_spending = sum(category_percentages.get(cat, 0) for cat in essentials)
        
        if essential_spending > 50:
            recommendations.append("Consider reducing essential expenses - aim for 50% of income")
        
        if category_percentages.get("Investment", 0) < 20:
            recommendations.append("Try to save/invest at least 20% of your income")
        
        # Specific category recommendations
        if category_percentages.get("Food", 0) > 15:
            recommendations.append("Food spending is high - try meal planning and cooking at home")
        
        return recommendations
    
    def _create_sample_budget_analysis(self) -> Dict[str, Any]:
        """Create sample budget analysis for demonstration"""
        return {
            "category_totals": {
                "Food": 235.00,
                "Transportation": 60.00,
                "Utilities": 120.00,
                "Shopping": 200.00,
                "Investment": 500.00
            },
            "category_percentages": {
                "Food": 21.1,
                "Transportation": 5.4,
                "Utilities": 10.8,
                "Shopping": 17.9,
                "Investment": 44.8
            },
            "total_expenses": 1115.00,
            "alerts": ["High spending in Investment: 44.8% of budget"],
            "recommendations": [
                "Great job prioritizing investments!",
                "Consider reducing food expenses through meal planning"
            ]
        }