from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from agents.nodes import FinanceAgentState
from tools.data_loader import DataLoader

class GoalTrackerTool:
    """Tracks progress toward financial goals"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Main entry point for goal tracking analysis"""
        goals = state.get("context", {}).get("goals")
        
        if not goals:
            state["analysis_results"]["goal_tracker"] = {
                "error": "No financial goals data available"
            }
            return state
        
        query = state.get("user_query", "").lower()
        
        if any(word in query for word in ["emergency", "emergency fund"]):
            analysis = self._analyze_specific_goal(goals, "emergency_fund")
        elif any(word in query for word in ["vacation", "travel", "trip"]):
            analysis = self._analyze_specific_goal(goals, "vacation_fund")
        elif any(word in query for word in ["house", "home", "down payment"]):
            analysis = self._analyze_specific_goal(goals, "house_down_payment")
        elif any(word in query for word in ["retirement", "401k"]):
            analysis = self._analyze_specific_goal(goals, "retirement_401k")
        elif any(word in query for word in ["car", "vehicle"]):
            analysis = self._analyze_specific_goal(goals, "car_replacement")
        elif any(word in query for word in ["progress", "how close", "track"]):
            analysis = self._analyze_overall_progress(goals)
        elif any(word in query for word in ["behind", "on track", "ahead"]):
            analysis = self._analyze_goal_timeline(goals)
        else:
            analysis = self._analyze_goals_summary(goals)
        
        state["analysis_results"]["goal_tracker"] = analysis
        state["tools_used"].append("goal_tracker")
        return state
    
    def _analyze_specific_goal(self, goals: List[Dict], goal_id: str) -> Dict[str, Any]:
        """Analyze a specific financial goal"""
        goal = next((g for g in goals if g.get("goal_id") == goal_id), None)
        
        if not goal:
            return {"error": f"Goal with ID '{goal_id}' not found"}
        
        target_amount = goal.get("target_amount", 0)
        current_amount = goal.get("current_amount", 0)
        monthly_contribution = goal.get("monthly_contribution", 0)
        deadline = goal.get("deadline", "")
        
        # Calculate progress metrics
        progress_percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
        remaining_amount = target_amount - current_amount
        
        # Timeline analysis
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d") if deadline else None
        days_remaining = (deadline_date - datetime.now()).days if deadline_date else None
        months_remaining = days_remaining / 30 if days_remaining else None
        
        # Projection analysis
        if monthly_contribution > 0 and months_remaining:
            projected_amount = current_amount + (monthly_contribution * months_remaining)
            on_track = projected_amount >= target_amount
            shortfall = max(0, target_amount - projected_amount)
            additional_monthly_needed = shortfall / months_remaining if months_remaining > 0 else 0
        else:
            projected_amount = current_amount
            on_track = False
            shortfall = remaining_amount
            additional_monthly_needed = 0
        
        return {
            "goal_details": {
                "name": goal.get("name", ""),
                "description": goal.get("description", ""),
                "target_amount": target_amount,
                "current_amount": current_amount,
                "deadline": deadline,
                "priority": goal.get("priority", ""),
                "category": goal.get("category", "")
            },
            "progress_analysis": {
                "progress_percentage": round(progress_percentage, 1),
                "amount_remaining": round(remaining_amount, 2),
                "days_remaining": days_remaining,
                "months_remaining": round(months_remaining, 1) if months_remaining else None
            },
            "projection": {
                "monthly_contribution": monthly_contribution,
                "projected_final_amount": round(projected_amount, 2),
                "on_track": on_track,
                "shortfall": round(shortfall, 2),
                "additional_monthly_needed": round(additional_monthly_needed, 2)
            },
            "recommendations": self._generate_goal_recommendations(goal, on_track, additional_monthly_needed),
            "milestone_progress": self._calculate_milestones(current_amount, target_amount)
        }
    
    def _analyze_overall_progress(self, goals: List[Dict]) -> Dict[str, Any]:
        """Analyze progress across all goals"""
        total_target = sum(goal.get("target_amount", 0) for goal in goals)
        total_current = sum(goal.get("current_amount", 0) for goal in goals)
        total_monthly = sum(goal.get("monthly_contribution", 0) for goal in goals)
        
        overall_progress = (total_current / total_target * 100) if total_target > 0 else 0
        
        # Analyze individual goal progress
        goal_progress = []
        for goal in goals:
            target = goal.get("target_amount", 0)
            current = goal.get("current_amount", 0)
            progress = (current / target * 100) if target > 0 else 0
            
            goal_progress.append({
                "goal_id": goal.get("goal_id", ""),
                "name": goal.get("name", ""),
                "progress_percentage": round(progress, 1),
                "current_amount": current,
                "target_amount": target,
                "priority": goal.get("priority", ""),
                "status": self._determine_goal_status(goal)
            })
        
        # Sort by progress percentage
        goal_progress.sort(key=lambda x: x["progress_percentage"], reverse=True)
        
        # Category analysis
        category_summary = {}
        for goal in goals:
            category = goal.get("category", "other")
            if category not in category_summary:
                category_summary[category] = {
                    "count": 0,
                    "total_target": 0,
                    "total_current": 0
                }
            
            category_summary[category]["count"] += 1
            category_summary[category]["total_target"] += goal.get("target_amount", 0)
            category_summary[category]["total_current"] += goal.get("current_amount", 0)
        
        # Add progress percentages to categories
        for category in category_summary:
            target = category_summary[category]["total_target"]
            current = category_summary[category]["total_current"]
            category_summary[category]["progress_percentage"] = round(
                (current / target * 100), 1
            ) if target > 0 else 0
        
        return {
            "overall_summary": {
                "total_goals": len(goals),
                "total_target_amount": round(total_target, 2),
                "total_current_amount": round(total_current, 2),
                "overall_progress_percentage": round(overall_progress, 1),
                "total_monthly_contributions": round(total_monthly, 2),
                "amount_remaining": round(total_target - total_current, 2)
            },
            "individual_progress": goal_progress,
            "category_breakdown": category_summary,
            "leading_goal": goal_progress[0] if goal_progress else None,
            "lagging_goal": goal_progress[-1] if goal_progress else None,
            "high_priority_goals": [g for g in goal_progress if g["priority"] == "high"]
        }
    
    def _analyze_goal_timeline(self, goals: List[Dict]) -> Dict[str, Any]:
        """Analyze goal timelines and deadlines"""
        timeline_analysis = []
        
        for goal in goals:
            deadline = goal.get("deadline", "")
            if not deadline:
                continue
                
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            days_remaining = (deadline_date - datetime.now()).days
            
            target_amount = goal.get("target_amount", 0)
            current_amount = goal.get("current_amount", 0)
            monthly_contribution = goal.get("monthly_contribution", 0)
            
            remaining_amount = target_amount - current_amount
            months_remaining = max(1, days_remaining / 30)
            required_monthly = remaining_amount / months_remaining if months_remaining > 0 else 0
            
            # Determine if on track
            if monthly_contribution >= required_monthly:
                status = "On Track"
            elif monthly_contribution >= required_monthly * 0.8:
                status = "Slightly Behind"
            else:
                status = "Behind Schedule"
            
            timeline_analysis.append({
                "goal_name": goal.get("name", ""),
                "goal_id": goal.get("goal_id", ""),
                "deadline": deadline,
                "days_remaining": days_remaining,
                "months_remaining": round(months_remaining, 1),
                "current_monthly": monthly_contribution,
                "required_monthly": round(required_monthly, 2),
                "status": status,
                "priority": goal.get("priority", ""),
                "shortfall_risk": round(max(0, required_monthly - monthly_contribution), 2)
            })
        
        # Sort by urgency (days remaining)
        timeline_analysis.sort(key=lambda x: x["days_remaining"])
        
        # Summary statistics
        on_track_count = sum(1 for g in timeline_analysis if g["status"] == "On Track")
        behind_count = sum(1 for g in timeline_analysis if g["status"] == "Behind Schedule")
        
        return {
            "timeline_summary": {
                "total_goals_with_deadlines": len(timeline_analysis),
                "goals_on_track": on_track_count,
                "goals_behind_schedule": behind_count,
                "goals_slightly_behind": len(timeline_analysis) - on_track_count - behind_count
            },
            "goal_timelines": timeline_analysis,
            "most_urgent": timeline_analysis[0] if timeline_analysis else None,
            "highest_risk": max(timeline_analysis, key=lambda x: x["shortfall_risk"]) if timeline_analysis else None,
            "recommendations": self._generate_timeline_recommendations(timeline_analysis)
        }
    
    def _analyze_goals_summary(self, goals: List[Dict]) -> Dict[str, Any]:
        """General goals overview"""
        active_goals = [g for g in goals if g.get("status") == "active"]
        
        # Priority breakdown
        priority_breakdown = {"high": 0, "medium": 0, "low": 0}
        for goal in active_goals:
            priority = goal.get("priority", "medium")
            priority_breakdown[priority] += 1
        
        # Category breakdown
        category_breakdown = {}
        for goal in active_goals:
            category = goal.get("category", "other")
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Quick stats
        total_target = sum(g.get("target_amount", 0) for g in active_goals)
        total_saved = sum(g.get("current_amount", 0) for g in active_goals)
        
        return {
            "goals_overview": {
                "total_active_goals": len(active_goals),
                "total_target_amount": round(total_target, 2),
                "total_saved": round(total_saved, 2),
                "overall_progress": round((total_saved / total_target * 100), 1) if total_target > 0 else 0,
                "amount_remaining": round(total_target - total_saved, 2)
            },
            "priority_breakdown": priority_breakdown,
            "category_breakdown": category_breakdown,
            "goal_list": [
                {
                    "name": goal.get("name", ""),
                    "target": goal.get("target_amount", 0),
                    "current": goal.get("current_amount", 0),
                    "progress": round((goal.get("current_amount", 0) / goal.get("target_amount", 1) * 100), 1),
                    "priority": goal.get("priority", ""),
                    "deadline": goal.get("deadline", "")
                }
                for goal in active_goals
            ]
        }
    
    def _determine_goal_status(self, goal: Dict) -> str:
        """Determine the status of a goal based on progress and timeline"""
        target = goal.get("target_amount", 0)
        current = goal.get("current_amount", 0)
        progress = (current / target * 100) if target > 0 else 0
        
        deadline = goal.get("deadline", "")
        if deadline:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            days_remaining = (deadline_date - datetime.now()).days
            
            if progress >= 100:
                return "Completed"
            elif days_remaining < 0:
                return "Overdue"
            elif progress >= 75:
                return "On Track"
            elif progress >= 50:
                return "Progressing"
            else:
                return "Behind"
        else:
            if progress >= 100:
                return "Completed"
            elif progress >= 75:
                return "Good Progress"
            elif progress >= 25:
                return "Some Progress"
            else:
                return "Just Started"
    
    def _calculate_milestones(self, current: float, target: float) -> Dict[str, Any]:
        """Calculate milestone progress"""
        milestones = [25, 50, 75, 90, 100]
        progress_percentage = (current / target * 100) if target > 0 else 0
        
        completed_milestones = [m for m in milestones if progress_percentage >= m]
        next_milestone = None
        
        for milestone in milestones:
            if progress_percentage < milestone:
                next_milestone = milestone
                break
        
        return {
            "completed_milestones": completed_milestones,
            "next_milestone": next_milestone,
            "amount_to_next_milestone": round(
                (target * (next_milestone / 100) - current), 2
            ) if next_milestone else 0
        }
    
    def _generate_goal_recommendations(self, goal: Dict, on_track: bool, additional_needed: float) -> List[str]:
        """Generate recommendations for a specific goal"""
        recommendations = []
        
        if on_track:
            recommendations.append("Great job! You're on track to reach your goal.")
        else:
            if additional_needed > 0:
                recommendations.append(
                    f"To stay on track, consider increasing your monthly contribution by ${additional_needed:.2f}"
                )
        
        # Priority-based recommendations
        priority = goal.get("priority", "")
        if priority == "high":
            recommendations.append("This is a high-priority goal. Consider reallocating funds from lower-priority goals if needed.")
        
        # Goal-specific recommendations
        goal_id = goal.get("goal_id", "")
        if goal_id == "emergency_fund":
            recommendations.append("Emergency funds should be easily accessible. Consider a high-yield savings account.")
        elif goal_id == "retirement_401k":
            recommendations.append("Don't forget to take advantage of any employer matching contributions.")
        
        return recommendations
    
    def _generate_timeline_recommendations(self, timeline_analysis: List[Dict]) -> List[str]:
        """Generate recommendations based on timeline analysis"""
        recommendations = []
        
        behind_goals = [g for g in timeline_analysis if g["status"] == "Behind Schedule"]
        urgent_goals = [g for g in timeline_analysis if g["days_remaining"] < 90]
        
        if behind_goals:
            recommendations.append(
                f"You have {len(behind_goals)} goals behind schedule. "
                "Consider increasing contributions or adjusting deadlines."
            )
        
        if urgent_goals:
            recommendations.append(
                f"{len(urgent_goals)} goals have deadlines within 90 days. "
                "Focus on these high-priority items."
            )
        
        if not behind_goals and not urgent_goals:
            recommendations.append("Your goal timelines look manageable. Keep up the consistent contributions!")
        
        return recommendations