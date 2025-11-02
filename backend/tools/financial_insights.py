from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from agents.nodes import FinanceAgentState
from tools.data_loader import DataLoader

class FinancialInsightsTool:
    """Generates comprehensive financial insights and reports"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Main entry point for financial insights analysis"""
        context = state.get("context", {})
        
        # Combine all available data for comprehensive analysis
        analysis = self._generate_comprehensive_insights(context)
        
        state["analysis_results"]["financial_insights"] = analysis
        state["tools_used"].append("financial_insights")
        return state
    
    def _generate_comprehensive_insights(self, context: Dict) -> Dict[str, Any]:
        """Generate comprehensive financial insights from all available data"""
        insights = {
            "analysis_type": "Comprehensive Financial Insights",
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "spending_insights": {},
            "investment_insights": {},
            "goal_insights": {},
            "recommendations": [],
            "alerts": []
        }
        
        # Analyze each component if available
        if "transactions" in context and not context["transactions"].empty:
            insights["spending_insights"] = self._analyze_spending_patterns(context["transactions"])
        
        if "investments" in context and context["investments"]:
            insights["investment_insights"] = self._analyze_investment_trends(context["investments"])
        
        if "goals" in context and context["goals"]:
            insights["goal_insights"] = self._analyze_goal_performance(context["goals"])
        
        if "budget" in context and context["budget"]:
            insights["budget_insights"] = self._analyze_budget_trends(context["budget"])
        
        # Generate overall financial health score
        insights["financial_health_score"] = self._calculate_financial_health_score(context)
        
        # Generate summary and recommendations
        insights["summary"] = self._generate_executive_summary(insights)
        insights["recommendations"] = self._generate_comprehensive_recommendations(insights)
        insights["alerts"] = self._generate_financial_alerts(context)
        
        return insights
    
    def _analyze_spending_patterns(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze spending patterns and trends"""
        current_date = datetime.now()
        
        # Monthly spending trend
        transactions['month'] = transactions['date'].dt.to_period('M')
        monthly_spending = transactions[transactions['amount'] < 0].groupby('month')['amount'].sum().abs()
        
        # Category trends
        current_month = current_date.strftime("%Y-%m")
        last_month = (current_date - timedelta(days=30)).strftime("%Y-%m")
        
        current_month_data = transactions[
            (transactions['date'].dt.strftime("%Y-%m") == current_month) & 
            (transactions['amount'] < 0)
        ]
        last_month_data = transactions[
            (transactions['date'].dt.strftime("%Y-%m") == last_month) & 
            (transactions['amount'] < 0)
        ]
        
        category_trends = {}
        for category in current_month_data['category'].unique():
            current_spend = abs(current_month_data[current_month_data['category'] == category]['amount'].sum())
            last_spend = abs(last_month_data[last_month_data['category'] == category]['amount'].sum())
            
            change = current_spend - last_spend
            change_percent = (change / last_spend * 100) if last_spend > 0 else 0
            
            category_trends[category] = {
                "current_month": round(current_spend, 2),
                "last_month": round(last_spend, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 1)
            }
        
        # Merchant analysis
        merchant_spending = current_month_data.groupby('merchant')['amount'].sum().abs().sort_values(ascending=False)
        
        # Unusual spending detection
        daily_spending = transactions[transactions['amount'] < 0].groupby(
            transactions['date'].dt.date
        )['amount'].sum().abs()
        
        avg_daily_spending = daily_spending.mean()
        std_daily_spending = daily_spending.std()
        threshold = avg_daily_spending + (2 * std_daily_spending)
        
        unusual_days = daily_spending[daily_spending > threshold]
        
        return {
            "monthly_trend": monthly_spending.tail(6).to_dict(),
            "category_trends": category_trends,
            "top_merchants": merchant_spending.head(5).to_dict(),
            "unusual_spending_days": [
                {"date": str(date), "amount": round(amount, 2)} 
                for date, amount in unusual_days.items()
            ],
            "average_daily_spending": round(avg_daily_spending, 2),
            "spending_volatility": round(std_daily_spending, 2)
        }
    
    def _analyze_investment_trends(self, investments: List[Dict]) -> Dict[str, Any]:
        """Analyze investment performance trends"""
        total_market_value = sum(inv.get("market_value", 0) for inv in investments)
        total_cost = sum(inv.get("total_cost", 0) for inv in investments)
        total_gain_loss = sum(inv.get("unrealized_gain_loss", 0) for inv in investments)
        
        # Performance distribution
        performance_buckets = {"strong_gains": 0, "moderate_gains": 0, "small_gains": 0, "losses": 0}
        
        for inv in investments:
            return_pct = inv.get("percentage_change", 0)
            if return_pct > 10:
                performance_buckets["strong_gains"] += 1
            elif return_pct > 5:
                performance_buckets["moderate_gains"] += 1
            elif return_pct > 0:
                performance_buckets["small_gains"] += 1
            else:
                performance_buckets["losses"] += 1
        
        # Risk analysis
        volatility_score = self._calculate_portfolio_volatility(investments)
        diversification_score = self._calculate_diversification_score(investments)
        
        return {
            "portfolio_value": round(total_market_value, 2),
            "total_return": round(total_gain_loss, 2),
            "return_percentage": round((total_gain_loss / total_cost * 100), 2) if total_cost > 0 else 0,
            "performance_distribution": performance_buckets,
            "risk_metrics": {
                "volatility_score": volatility_score,
                "diversification_score": diversification_score,
                "largest_position_pct": max(
                    (inv.get("market_value", 0) / total_market_value * 100) 
                    for inv in investments
                ) if total_market_value > 0 else 0
            }
        }
    
    def _analyze_goal_performance(self, goals: List[Dict]) -> Dict[str, Any]:
        """Analyze goal achievement trends"""
        active_goals = [g for g in goals if g.get("status") == "active"]
        
        # Progress analysis
        total_target = sum(g.get("target_amount", 0) for g in active_goals)
        total_saved = sum(g.get("current_amount", 0) for g in active_goals)
        overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0
        
        # Timeline analysis
        goals_with_deadlines = [g for g in active_goals if g.get("deadline")]
        on_track_count = 0
        
        for goal in goals_with_deadlines:
            deadline = datetime.strptime(goal.get("deadline"), "%Y-%m-%d")
            days_remaining = (deadline - datetime.now()).days
            months_remaining = days_remaining / 30
            
            target = goal.get("target_amount", 0)
            current = goal.get("current_amount", 0)
            monthly_contribution = goal.get("monthly_contribution", 0)
            
            if months_remaining > 0:
                required_monthly = (target - current) / months_remaining
                if monthly_contribution >= required_monthly:
                    on_track_count += 1
        
        # Priority analysis
        high_priority_goals = [g for g in active_goals if g.get("priority") == "high"]
        high_priority_progress = sum(g.get("current_amount", 0) for g in high_priority_goals)
        high_priority_target = sum(g.get("target_amount", 0) for g in high_priority_goals)
        
        return {
            "total_goals": len(active_goals),
            "overall_progress_pct": round(overall_progress, 1),
            "amount_saved": round(total_saved, 2),
            "amount_remaining": round(total_target - total_saved, 2),
            "goals_on_track": on_track_count,
            "goals_with_deadlines": len(goals_with_deadlines),
            "high_priority_progress": round(
                (high_priority_progress / high_priority_target * 100), 1
            ) if high_priority_target > 0 else 0,
            "monthly_savings_rate": sum(g.get("monthly_contribution", 0) for g in active_goals)
        }
    
    def _analyze_budget_trends(self, budget_data: Dict) -> Dict[str, Any]:
        """Analyze budget performance trends"""
        monthly_budgets = budget_data.get("monthly_budgets", {})
        
        if not monthly_budgets:
            return {"error": "No budget data available"}
        
        # Get recent months data
        sorted_months = sorted(monthly_budgets.keys(), reverse=True)
        recent_months = sorted_months[:3]  # Last 3 months
        
        trends = {}
        for month in recent_months:
            month_data = monthly_budgets[month]
            trends[month] = {
                "total_spent": month_data.get("total_spent", 0),
                "total_budgeted": month_data.get("total_budgeted", 0),
                "savings_rate": month_data.get("savings_rate", 0),
                "categories_over_budget": sum(
                    1 for cat_data in month_data.get("categories", {}).values()
                    if cat_data.get("remaining", 0) < 0
                )
            }
        
        # Calculate trend direction
        if len(recent_months) >= 2:
            current_month = trends[recent_months[0]]
            previous_month = trends[recent_months[1]]
            
            spending_trend = current_month["total_spent"] - previous_month["total_spent"]
            savings_trend = current_month["savings_rate"] - previous_month["savings_rate"]
        else:
            spending_trend = 0
            savings_trend = 0
        
        return {
            "monthly_trends": trends,
            "spending_trend": round(spending_trend, 2),
            "savings_trend": round(savings_trend, 2),
            "trend_direction": "improving" if savings_trend > 0 else "declining" if savings_trend < 0 else "stable"
        }
    
    def _calculate_financial_health_score(self, context: Dict) -> Dict[str, Any]:
        """Calculate overall financial health score (0-100)"""
        score_components = {}
        total_score = 0
        max_possible = 0
        
        # Budget performance (25 points)
        if "budget" in context:
            budget_score = self._score_budget_performance(context["budget"])
            score_components["budget"] = budget_score
            total_score += budget_score
            max_possible += 25
        
        # Investment performance (25 points)
        if "investments" in context:
            investment_score = self._score_investment_performance(context["investments"])
            score_components["investments"] = investment_score
            total_score += investment_score
            max_possible += 25
        
        # Goal progress (25 points)
        if "goals" in context:
            goal_score = self._score_goal_progress(context["goals"])
            score_components["goals"] = goal_score
            total_score += goal_score
            max_possible += 25
        
        # Spending habits (25 points)
        if "transactions" in context:
            spending_score = self._score_spending_habits(context["transactions"])
            score_components["spending"] = spending_score
            total_score += spending_score
            max_possible += 25
        
        overall_score = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        return {
            "overall_score": round(overall_score, 1),
            "score_components": score_components,
            "rating": self._get_health_rating(overall_score),
            "max_possible_score": max_possible
        }
    
    def _score_budget_performance(self, budget_data: Dict) -> int:
        """Score budget performance (0-25 points)"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget = budget_data.get("monthly_budgets", {}).get(current_month, {})
        
        if not monthly_budget:
            return 0
        
        categories = monthly_budget.get("categories", {})
        if not categories:
            return 0
        
        over_budget_count = sum(1 for data in categories.values() if data.get("remaining", 0) < 0)
        total_categories = len(categories)
        
        # Score based on percentage of categories on budget
        on_budget_ratio = (total_categories - over_budget_count) / total_categories
        
        # Additional points for savings rate
        savings_rate = monthly_budget.get("savings_rate", 0)
        savings_bonus = min(5, savings_rate / 4)  # Up to 5 bonus points for 20%+ savings rate
        
        return min(25, int(on_budget_ratio * 20 + savings_bonus))
    
    def _score_investment_performance(self, investments: List[Dict]) -> int:
        """Score investment performance (0-25 points)"""
        if not investments:
            return 0
        
        total_return = sum(inv.get("unrealized_gain_loss", 0) for inv in investments)
        total_cost = sum(inv.get("total_cost", 0) for inv in investments)
        
        if total_cost <= 0:
            return 0
        
        return_percentage = (total_return / total_cost) * 100
        
        # Score based on returns (simplified)
        if return_percentage >= 10:
            return 25
        elif return_percentage >= 5:
            return 20
        elif return_percentage >= 0:
            return 15
        elif return_percentage >= -5:
            return 10
        else:
            return 5
    
    def _score_goal_progress(self, goals: List[Dict]) -> int:
        """Score goal progress (0-25 points)"""
        active_goals = [g for g in goals if g.get("status") == "active"]
        
        if not active_goals:
            return 0
        
        total_target = sum(g.get("target_amount", 0) for g in active_goals)
        total_saved = sum(g.get("current_amount", 0) for g in active_goals)
        
        if total_target <= 0:
            return 0
        
        progress_ratio = total_saved / total_target
        return min(25, int(progress_ratio * 25))
    
    def _score_spending_habits(self, transactions: pd.DataFrame) -> int:
        """Score spending habits (0-25 points)"""
        if transactions.empty:
            return 0
        
        # Analyze spending consistency
        daily_spending = transactions[transactions['amount'] < 0].groupby(
            transactions['date'].dt.date
        )['amount'].sum().abs()
        
        # Lower volatility = better score
        spending_volatility = daily_spending.std() / daily_spending.mean() if daily_spending.mean() > 0 else 0
        
        # Score based on spending consistency (lower volatility = higher score)
        if spending_volatility < 0.5:
            return 25
        elif spending_volatility < 1.0:
            return 20
        elif spending_volatility < 1.5:
            return 15
        elif spending_volatility < 2.0:
            return 10
        else:
            return 5
    
    def _get_health_rating(self, score: float) -> str:
        """Convert numerical score to rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Poor"
        else:
            return "Critical"
    
    def _calculate_portfolio_volatility(self, investments: List[Dict]) -> str:
        """Calculate portfolio volatility score"""
        returns = [inv.get("percentage_change", 0) for inv in investments]
        if not returns:
            return "Unknown"
        
        # Simple volatility measure based on return spread
        return_range = max(returns) - min(returns)
        
        if return_range < 5:
            return "Low"
        elif return_range < 15:
            return "Medium"
        else:
            return "High"
    
    def _calculate_diversification_score(self, investments: List[Dict]) -> str:
        """Calculate portfolio diversification score"""
        if len(investments) < 3:
            return "Poor"
        elif len(investments) < 6:
            return "Fair"
        elif len(investments) < 10:
            return "Good"
        else:
            return "Excellent"
    
    def _generate_executive_summary(self, insights: Dict) -> Dict[str, Any]:
        """Generate executive summary of financial insights"""
        summary = {
            "financial_health_rating": insights.get("financial_health_score", {}).get("rating", "Unknown"),
            "key_metrics": {},
            "highlights": [],
            "concerns": []
        }
        
        # Extract key metrics
        if "spending_insights" in insights:
            summary["key_metrics"]["average_daily_spending"] = insights["spending_insights"].get("average_daily_spending", 0)
        
        if "investment_insights" in insights:
            summary["key_metrics"]["portfolio_return"] = insights["investment_insights"].get("return_percentage", 0)
        
        if "goal_insights" in insights:
            summary["key_metrics"]["goal_progress"] = insights["goal_insights"].get("overall_progress_pct", 0)
        
        # Generate highlights and concerns
        health_score = insights.get("financial_health_score", {}).get("overall_score", 0)
        
        if health_score >= 80:
            summary["highlights"].append("Strong overall financial health")
        
        if "investment_insights" in insights:
            portfolio_return = insights["investment_insights"].get("return_percentage", 0)
            if portfolio_return > 5:
                summary["highlights"].append(f"Portfolio performing well with {portfolio_return:.1f}% returns")
            elif portfolio_return < -5:
                summary["concerns"].append(f"Portfolio showing negative returns of {portfolio_return:.1f}%")
        
        return summary
    
    def _generate_comprehensive_recommendations(self, insights: Dict) -> List[str]:
        """Generate comprehensive financial recommendations"""
        recommendations = []
        
        # Budget recommendations
        if "budget_insights" in insights:
            trend = insights["budget_insights"].get("trend_direction", "")
            if trend == "declining":
                recommendations.append("Consider reviewing your budget - spending has been increasing recently")
        
        # Investment recommendations
        if "investment_insights" in insights:
            risk_metrics = insights["investment_insights"].get("risk_metrics", {})
            diversification = risk_metrics.get("diversification_score", "")
            
            if diversification in ["Poor", "Fair"]:
                recommendations.append("Consider diversifying your investment portfolio across more assets")
        
        # Goal recommendations
        if "goal_insights" in insights:
            progress = insights["goal_insights"].get("overall_progress_pct", 0)
            if progress < 50:
                recommendations.append("Focus on increasing contributions to your financial goals")
        
        # General recommendations
        health_score = insights.get("financial_health_score", {}).get("overall_score", 0)
        if health_score < 70:
            recommendations.append("Consider meeting with a financial advisor to improve your financial health")
        
        return recommendations if recommendations else ["Keep up the good work with your financial management!"]
    
    def _generate_financial_alerts(self, context: Dict) -> List[Dict[str, Any]]:
        """Generate financial alerts and warnings"""
        alerts = []
        
        # Budget alerts
        if "budget" in context:
            current_month = datetime.now().strftime("%Y-%m")
            monthly_budget = context["budget"].get("monthly_budgets", {}).get(current_month, {})
            categories = monthly_budget.get("categories", {})
            
            for category, data in categories.items():
                if data.get("remaining", 0) < 0:
                    alerts.append({
                        "type": "warning",
                        "category": "budget",
                        "message": f"Over budget in {category} by ${abs(data.get('remaining', 0)):.2f}",
                        "severity": "medium"
                    })
        
        # Goal deadline alerts
        if "goals" in context:
            for goal in context["goals"]:
                deadline = goal.get("deadline", "")
                if deadline:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                    days_remaining = (deadline_date - datetime.now()).days
                    
                    if days_remaining < 30 and days_remaining > 0:
                        alerts.append({
                            "type": "info",
                            "category": "goals",
                            "message": f"Goal '{goal.get('name', '')}' deadline approaching in {days_remaining} days",
                            "severity": "low"
                        })
        
        # Investment alerts
        if "investments" in context:
            for inv in context["investments"]:
                loss_pct = inv.get("percentage_change", 0)
                if loss_pct < -10:
                    alerts.append({
                        "type": "warning",
                        "category": "investments",
                        "message": f"{inv.get('symbol', '')} is down {abs(loss_pct):.1f}%",
                        "severity": "medium"
                    })
        
        return alerts