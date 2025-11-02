from datetime import datetime
from typing import Dict, List, Any, Optional
from agents.nodes import FinanceAgentState
from tools.data_loader import DataLoader

class BudgetManagerTool:
    """Manages budget analysis and tracking"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Main entry point for budget analysis"""
        budget_data = state.get("context", {}).get("budget")
        transactions = state.get("context", {}).get("transactions")
        
        if not budget_data:
            state["analysis_results"]["budget_manager"] = {
                "error": "No budget data available"
            }
            return state
        
        query = state.get("user_query", "").lower()
        
        if any(word in query for word in ["over", "overspending", "exceeded"]):
            analysis = self._analyze_overspending(budget_data)
        elif any(word in query for word in ["remaining", "left", "budget left"]):
            analysis = self._analyze_remaining_budget(budget_data)
        elif any(word in query for word in ["performance", "how am i doing", "budget performance"]):
            analysis = self._analyze_budget_performance(budget_data)
        else:
            analysis = self._analyze_current_budget_status(budget_data)
        
        state["analysis_results"]["budget_manager"] = analysis
        state["tools_used"].append("budget_manager")
        return state
    
    def _analyze_overspending(self, budget_data: Dict) -> Dict[str, Any]:
        """Analyze categories where spending exceeded budget"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget = budget_data.get("monthly_budgets", {}).get(current_month, {})
        
        if not monthly_budget:
            return {"error": "No budget data for current month"}
        
        categories = monthly_budget.get("categories", {})
        overspent_categories = []
        
        for category, data in categories.items():
            remaining = data.get("remaining", 0)
            if remaining < 0:
                overspent_categories.append({
                    "category": category,
                    "budgeted": data.get("budgeted", 0),
                    "spent": data.get("spent", 0),
                    "overspent_amount": abs(remaining),
                    "percentage_over": data.get("percentage_used", 0) - 100
                })
        
        # Sort by overspent amount
        overspent_categories.sort(key=lambda x: x["overspent_amount"], reverse=True)
        
        total_overspent = sum([cat["overspent_amount"] for cat in overspent_categories])
        
        return {
            "period": current_month,
            "overspent_categories": overspent_categories,
            "total_overspent": round(total_overspent, 2),
            "categories_over_budget": len(overspent_categories),
            "worst_category": overspent_categories[0] if overspent_categories else None,
            "recommendations": self._generate_overspending_recommendations(overspent_categories)
        }
    
    def _analyze_remaining_budget(self, budget_data: Dict) -> Dict[str, Any]:
        """Analyze remaining budget across categories"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget = budget_data.get("monthly_budgets", {}).get(current_month, {})
        
        if not monthly_budget:
            return {"error": "No budget data for current month"}
        
        categories = monthly_budget.get("categories", {})
        remaining_analysis = []
        
        for category, data in categories.items():
            remaining = data.get("remaining", 0)
            budgeted = data.get("budgeted", 0)
            
            if remaining > 0:
                remaining_analysis.append({
                    "category": category,
                    "budgeted": budgeted,
                    "spent": data.get("spent", 0),
                    "remaining": remaining,
                    "percentage_used": data.get("percentage_used", 0),
                    "percentage_remaining": round((remaining / budgeted) * 100, 1) if budgeted > 0 else 0
                })
        
        # Sort by remaining amount
        remaining_analysis.sort(key=lambda x: x["remaining"], reverse=True)
        
        total_remaining = sum([cat["remaining"] for cat in remaining_analysis])
        
        return {
            "period": current_month,
            "categories_with_budget_left": remaining_analysis,
            "total_remaining": round(total_remaining, 2),
            "categories_count": len(remaining_analysis),
            "highest_remaining": remaining_analysis[0] if remaining_analysis else None,
            "days_left_in_month": self._days_left_in_month(),
            "daily_spending_allowance": round(total_remaining / max(self._days_left_in_month(), 1), 2)
        }
    
    def _analyze_budget_performance(self, budget_data: Dict) -> Dict[str, Any]:
        """Comprehensive budget performance analysis"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget = budget_data.get("monthly_budgets", {}).get(current_month, {})
        
        if not monthly_budget:
            return {"error": "No budget data for current month"}
        
        categories = monthly_budget.get("categories", {})
        performance_summary = {
            "on_track": [],
            "warning": [],  # 80-100% used
            "over_budget": []
        }
        
        for category, data in categories.items():
            percentage_used = data.get("percentage_used", 0)
            category_info = {
                "category": category,
                "budgeted": data.get("budgeted", 0),
                "spent": data.get("spent", 0),
                "percentage_used": percentage_used,
                "remaining": data.get("remaining", 0)
            }
            
            if percentage_used > 100:
                performance_summary["over_budget"].append(category_info)
            elif percentage_used >= 80:
                performance_summary["warning"].append(category_info)
            else:
                performance_summary["on_track"].append(category_info)
        
        total_budgeted = monthly_budget.get("total_budgeted", 0)
        total_spent = monthly_budget.get("total_spent", 0)
        overall_percentage = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
        
        return {
            "period": current_month,
            "overall_performance": {
                "total_budgeted": total_budgeted,
                "total_spent": total_spent,
                "percentage_used": round(overall_percentage, 1),
                "remaining": round(total_budgeted - total_spent, 2)
            },
            "performance_summary": performance_summary,
            "categories_on_track": len(performance_summary["on_track"]),
            "categories_warning": len(performance_summary["warning"]),
            "categories_over": len(performance_summary["over_budget"]),
            "score": self._calculate_budget_score(performance_summary),
            "recommendations": self._generate_performance_recommendations(performance_summary)
        }
    
    def _analyze_current_budget_status(self, budget_data: Dict) -> Dict[str, Any]:
        """General current budget status"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget = budget_data.get("monthly_budgets", {}).get(current_month, {})
        
        if not monthly_budget:
            return {"error": "No budget data for current month"}
        
        categories = monthly_budget.get("categories", {})
        
        # Quick summary stats
        total_categories = len(categories)
        over_budget_count = sum(1 for data in categories.values() if data.get("remaining", 0) < 0)
        warning_count = sum(1 for data in categories.values() 
                          if 80 <= data.get("percentage_used", 0) <= 100)
        
        # Top spending categories
        top_spending = sorted(
            [(cat, data.get("spent", 0)) for cat, data in categories.items()],
            key=lambda x: x[1], reverse=True
        )[:3]
        
        return {
            "period": current_month,
            "summary": {
                "total_budgeted": monthly_budget.get("total_budgeted", 0),
                "total_spent": monthly_budget.get("total_spent", 0),
                "total_remaining": monthly_budget.get("total_remaining", 0),
                "overall_percentage": round(
                    (monthly_budget.get("total_spent", 0) / monthly_budget.get("total_budgeted", 1)) * 100, 1
                )
            },
            "category_status": {
                "total_categories": total_categories,
                "over_budget": over_budget_count,
                "warning_zone": warning_count,
                "on_track": total_categories - over_budget_count - warning_count
            },
            "top_spending_categories": [
                {"category": cat, "amount": round(amount, 2)} for cat, amount in top_spending
            ],
            "days_left_in_month": self._days_left_in_month(),
            "savings_rate": monthly_budget.get("savings_rate", 0)
        }
    
    def _days_left_in_month(self) -> int:
        """Calculate days remaining in current month"""
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return (next_month - now).days
    
    def _calculate_budget_score(self, performance_summary: Dict) -> str:
        """Calculate a simple budget performance score"""
        total_categories = (
            len(performance_summary["on_track"]) +
            len(performance_summary["warning"]) +
            len(performance_summary["over_budget"])
        )
        
        if total_categories == 0:
            return "No Data"
        
        on_track_ratio = len(performance_summary["on_track"]) / total_categories
        over_budget_ratio = len(performance_summary["over_budget"]) / total_categories
        
        if over_budget_ratio > 0.3:
            return "Needs Improvement"
        elif over_budget_ratio > 0.1:
            return "Fair"
        elif on_track_ratio > 0.7:
            return "Excellent"
        else:
            return "Good"
    
    def _generate_overspending_recommendations(self, overspent_categories: List[Dict]) -> List[str]:
        """Generate recommendations for overspending"""
        if not overspent_categories:
            return ["Great job staying within budget!"]
        
        recommendations = []
        worst_category = overspent_categories[0]
        
        recommendations.append(
            f"Consider reducing {worst_category['category']} spending by "
            f"${worst_category['overspent_amount']:.2f} next month"
        )
        
        if len(overspent_categories) > 1:
            recommendations.append(
                f"You're over budget in {len(overspent_categories)} categories. "
                "Focus on the top 2 overspenders first."
            )
        
        return recommendations
    
    def _generate_performance_recommendations(self, performance_summary: Dict) -> List[str]:
        """Generate performance-based recommendations"""
        recommendations = []
        
        if len(performance_summary["over_budget"]) > 0:
            recommendations.append(
                f"You have {len(performance_summary['over_budget'])} categories over budget. "
                "Consider adjusting spending or reallocating budget."
            )
        
        if len(performance_summary["warning"]) > 0:
            recommendations.append(
                f"{len(performance_summary['warning'])} categories are in the warning zone. "
                "Monitor these closely for the rest of the month."
            )
        
        if len(performance_summary["on_track"]) == len(performance_summary["on_track"]) + len(performance_summary["warning"]) + len(performance_summary["over_budget"]):
            recommendations.append("Excellent budget management! Keep up the great work.")
        
        return recommendations if recommendations else ["Keep monitoring your spending patterns."]