"""
Goal Planner Node - Simple interest calculation and goal tracking
Stage 1: MVP - Goal Planner
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class GoalPlannerNode:
    """Plans and tracks financial goals"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Plan and analyze financial goals"""
        try:
            user_query = state.get("user_query", "").lower()
            
            # Check if user is asking about goals
            if any(keyword in user_query for keyword in [
                "goal", "save", "target", "plan", "retirement", "emergency", "vacation"
            ]):
                goals_analysis = self._analyze_goals(user_query)
                state["analysis_results"]["goals_analysis"] = goals_analysis
                state["tools_used"] = state.get("tools_used", []) + ["goal_planner"]
                
                # Add goal recommendations
                recommendations = self._generate_goal_recommendations(goals_analysis)
                state["analysis_results"]["goal_recommendations"] = recommendations
                
                logger.info("Goal planning analysis completed")
            else:
                # Create general goal framework
                general_goals = self._create_general_goal_framework()
                state["analysis_results"]["goals_analysis"] = general_goals
                state["tools_used"] = state.get("tools_used", []) + ["goal_planner"]
            
            state["current_node"] = "goal_planner"
            
        except Exception as e:
            logger.error(f"Goal planning error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _analyze_goals(self, user_query: str) -> Dict[str, Any]:
        """Analyze specific financial goals from user query"""
        goals = []
        
        # Extract goal information (simplified NLP)
        if "retirement" in user_query:
            goals.append(self._create_retirement_goal())
        
        if "emergency" in user_query:
            goals.append(self._create_emergency_fund_goal())
        
        if "house" in user_query or "home" in user_query:
            goals.append(self._create_house_goal())
        
        if "vacation" in user_query:
            goals.append(self._create_vacation_goal())
        
        # If no specific goals mentioned, create sample goals
        if not goals:
            goals = [
                self._create_emergency_fund_goal(),
                self._create_retirement_goal()
            ]
        
        return {
            "goals": goals,
            "total_monthly_required": sum(goal["monthly_required"] for goal in goals),
            "priority_ranking": self._rank_goals(goals)
        }
    
    def _create_retirement_goal(self) -> Dict[str, Any]:
        """Create retirement savings goal"""
        target_amount = 1000000  # $1M retirement goal
        years_to_retirement = 30
        annual_return = 0.07  # 7% average return
        
        # Calculate required monthly savings with compound interest
        monthly_rate = annual_return / 12
        months = years_to_retirement * 12
        
        # Future value of annuity formula
        monthly_required = target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
        
        return {
            "name": "Retirement Savings",
            "target_amount": target_amount,
            "timeline_years": years_to_retirement,
            "monthly_required": round(monthly_required, 2),
            "priority": "High",
            "category": "Long-term",
            "progress": 0.0,
            "notes": "Assumes 7% annual return with compound interest"
        }
    
    def _create_emergency_fund_goal(self) -> Dict[str, Any]:
        """Create emergency fund goal"""
        monthly_expenses = 4000  # Estimated monthly expenses
        target_months = 6  # 6 months of expenses
        target_amount = monthly_expenses * target_months
        timeline_months = 12  # Build emergency fund in 1 year
        
        monthly_required = target_amount / timeline_months
        
        return {
            "name": "Emergency Fund",
            "target_amount": target_amount,
            "timeline_years": 1,
            "monthly_required": round(monthly_required, 2),
            "priority": "Critical",
            "category": "Safety",
            "progress": 0.0,
            "notes": "6 months of living expenses for financial security"
        }
    
    def _create_house_goal(self) -> Dict[str, Any]:
        """Create house down payment goal"""
        house_price = 400000
        down_payment_percent = 0.20
        target_amount = house_price * down_payment_percent
        timeline_years = 5
        
        monthly_required = target_amount / (timeline_years * 12)
        
        return {
            "name": "House Down Payment",
            "target_amount": target_amount,
            "timeline_years": timeline_years,
            "monthly_required": round(monthly_required, 2),
            "priority": "Medium",
            "category": "Major Purchase",
            "progress": 0.0,
            "notes": f"20% down payment for ${house_price:,} home"
        }
    
    def _create_vacation_goal(self) -> Dict[str, Any]:
        """Create vacation savings goal"""
        target_amount = 5000
        timeline_months = 8
        
        monthly_required = target_amount / timeline_months
        
        return {
            "name": "Dream Vacation",
            "target_amount": target_amount,
            "timeline_years": timeline_months / 12,
            "monthly_required": round(monthly_required, 2),
            "priority": "Low",
            "category": "Lifestyle",
            "progress": 0.0,
            "notes": "Family vacation fund"
        }
    
    def _rank_goals(self, goals: List[Dict]) -> List[str]:
        """Rank goals by priority"""
        priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        sorted_goals = sorted(goals, key=lambda x: priority_order.get(x["priority"], 5))
        return [goal["name"] for goal in sorted_goals]
    
    def _generate_goal_recommendations(self, goals_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for achieving goals"""
        recommendations = []
        goals = goals_analysis["goals"]
        total_monthly = goals_analysis["total_monthly_required"]
        
        recommendations.append(f"Total monthly savings needed: ${total_monthly:.2f}")
        
        # Priority-based recommendations
        for goal in goals:
            if goal["priority"] == "Critical":
                recommendations.append(f"🚨 Priority: {goal['name']} - ${goal['monthly_required']:.2f}/month")
            elif goal["priority"] == "High":
                recommendations.append(f"⭐ Important: {goal['name']} - ${goal['monthly_required']:.2f}/month")
        
        # Strategy recommendations
        recommendations.append("Consider automating savings transfers to stay on track")
        recommendations.append("Review and adjust goals quarterly based on income changes")
        
        if total_monthly > 2000:  # High savings requirement
            recommendations.append("Consider increasing income or extending timelines for more manageable monthly amounts")
        
        return recommendations
    
    def _create_general_goal_framework(self) -> Dict[str, Any]:
        """Create a general goal planning framework"""
        return {
            "framework": "50/30/20 Rule + Goals",
            "recommended_goals": [
                "Emergency Fund (3-6 months expenses)",
                "Retirement Savings (10-15% of income)",
                "Debt Payoff (if applicable)",
                "Major Purchase Savings"
            ],
            "goal_setting_tips": [
                "Make goals SMART (Specific, Measurable, Achievable, Relevant, Time-bound)",
                "Start with emergency fund as foundation",
                "Automate savings for consistency",
                "Review progress monthly"
            ],
            "next_steps": [
                "Define specific financial goals",
                "Calculate required monthly savings",
                "Set up automatic transfers",
                "Track progress regularly"
            ]
        }