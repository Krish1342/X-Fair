"""
Action Executor Node - Executes automated financial actions
Stage 3: Advanced - Action Executor
"""
import logging
from typing import Dict, Any, List
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class ActionExecutorNode:
    """Executes automated financial actions based on analysis and user consent"""
    
    def __init__(self):
        self.enabled_actions = {
            "portfolio_rebalancing": False,  # Requires broker API
            "bill_payments": False,          # Requires banking API
            "savings_transfers": False,      # Requires banking API
            "investment_purchases": False,   # Requires broker API
            "notifications": True,           # Always available
            "report_generation": True        # Always available
        }
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Execute automated actions based on analysis results"""
        try:
            analysis_results = state.get("analysis_results", {})
            user_profile = state.get("user_profile")
            
            # Check user consent for automated actions
            if not user_profile or not user_profile.consent_given:
                state["analysis_results"]["action_execution"] = {
                    "status": "consent_required",
                    "message": "User consent required for automated actions"
                }
                return state
            
            # Determine available actions based on analysis
            available_actions = self._identify_available_actions(analysis_results)
            
            # Execute safe actions (notifications, reports)
            executed_actions = []
            suggested_actions = []
            
            for action in available_actions:
                if self.enabled_actions.get(action["type"], False):
                    # Execute the action
                    execution_result = self._execute_action(action, analysis_results)
                    executed_actions.append(execution_result)
                else:
                    # Add to suggestions for manual execution
                    suggested_actions.append(action)
            
            state["analysis_results"]["action_execution"] = {
                "executed_actions": executed_actions,
                "suggested_actions": suggested_actions,
                "execution_summary": self._create_execution_summary(executed_actions, suggested_actions)
            }
            
            state["tools_used"] = state.get("tools_used", []) + ["action_executor"]
            state["current_node"] = "action_executor"
            
            logger.info(f"Executed {len(executed_actions)} actions, suggested {len(suggested_actions)}")
            
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _identify_available_actions(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify actions that can be taken based on analysis results"""
        actions = []
        
        # Budget-based actions
        if "budget_analysis" in analysis_results:
            budget = analysis_results["budget_analysis"]
            
            # Alert for overspending
            for alert in budget.get("alerts", []):
                actions.append({
                    "type": "notifications",
                    "action": "send_budget_alert",
                    "description": f"Budget Alert: {alert}",
                    "priority": "high",
                    "data": {"alert_message": alert}
                })
            
            # Savings optimization suggestions
            if budget.get("total_expenses", 0) > 0:
                actions.append({
                    "type": "savings_transfers",
                    "action": "optimize_savings",
                    "description": "Automatically transfer surplus funds to savings",
                    "priority": "medium",
                    "data": {"transfer_amount": budget.get("total_expenses", 0) * 0.1}
                })
        
        # Goal-based actions
        if "goals_analysis" in analysis_results:
            goals = analysis_results["goals_analysis"]
            
            for goal in goals.get("goals", []):
                if goal.get("priority") == "Critical":
                    actions.append({
                        "type": "savings_transfers",
                        "action": "goal_contribution",
                        "description": f"Automated transfer for {goal['name']}",
                        "priority": "high",
                        "data": {
                            "goal_name": goal["name"],
                            "monthly_amount": goal.get("monthly_required", 0)
                        }
                    })
        
        # Investment-based actions
        if "ml_analysis" in analysis_results:
            ml_results = analysis_results["ml_analysis"]
            
            if "portfolio_optimization" in ml_results:
                portfolio = ml_results["portfolio_optimization"]
                actions.append({
                    "type": "portfolio_rebalancing",
                    "action": "rebalance_portfolio",
                    "description": "Rebalance portfolio to optimal allocation",
                    "priority": "medium",
                    "data": {
                        "target_allocation": portfolio.get("optimal_allocation", {}),
                        "rebalancing_threshold": 5.0
                    }
                })
        
        # Task-based actions
        if "task_decomposition" in analysis_results:
            tasks = analysis_results["task_decomposition"]
            
            # Generate automated reminders for critical tasks
            execution_plan = tasks.get("execution_plan", {})
            for phase_name, phase_tasks in execution_plan.get("phases", {}).items():
                for task in phase_tasks:
                    if task.get("priority") == "Critical":
                        actions.append({
                            "type": "notifications",
                            "action": "task_reminder",
                            "description": f"Reminder: {task['title']}",
                            "priority": "medium",
                            "data": {
                                "task_id": task.get("task_id"),
                                "task_title": task.get("title"),
                                "due_date": "1 week"
                            }
                        })
        
        # Always generate reports
        actions.append({
            "type": "report_generation",
            "action": "generate_financial_report",
            "description": "Generate comprehensive financial analysis report",
            "priority": "low",
            "data": {"report_type": "comprehensive", "format": "pdf"}
        })
        
        return actions
    
    def _execute_action(self, action: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action"""
        action_type = action["type"]
        action_name = action["action"]
        
        execution_result = {
            "action": action_name,
            "type": action_type,
            "status": "completed",
            "timestamp": "2024-01-01T12:00:00Z",  # In real implementation, use actual timestamp
            "details": {}
        }
        
        try:
            if action_type == "notifications":
                execution_result["details"] = self._execute_notification(action)
            
            elif action_type == "report_generation":
                execution_result["details"] = self._execute_report_generation(action, analysis_results)
            
            elif action_type == "savings_transfers":
                execution_result["details"] = self._simulate_savings_transfer(action)
                execution_result["status"] = "simulated"  # Would be "completed" with real API
            
            elif action_type == "portfolio_rebalancing":
                execution_result["details"] = self._simulate_portfolio_rebalancing(action)
                execution_result["status"] = "simulated"  # Would be "completed" with real API
            
            else:
                execution_result["status"] = "not_supported"
                execution_result["details"] = {"message": f"Action type {action_type} not yet supported"}
        
        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["details"] = {"error": str(e)}
            logger.error(f"Action execution failed: {e}")
        
        return execution_result
    
    def _execute_notification(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification action"""
        notification_data = action.get("data", {})
        
        # Simulate sending notification
        notification_id = f"notif_{hash(action['description'])}"
        
        return {
            "notification_id": notification_id,
            "message": action["description"],
            "priority": action["priority"],
            "delivery_method": "in_app",
            "status": "sent"
        }
    
    def _execute_report_generation(self, action: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation action"""
        report_data = action.get("data", {})
        
        # Generate comprehensive financial report
        report_content = {
            "report_id": f"report_{hash(str(analysis_results))}",
            "generated_at": "2024-01-01T12:00:00Z",
            "report_type": report_data.get("report_type", "standard"),
            "sections": [
                "Executive Summary",
                "Budget Analysis", 
                "Goal Progress",
                "Investment Performance",
                "Risk Assessment",
                "Recommendations"
            ],
            "file_format": report_data.get("format", "pdf"),
            "file_size_kb": 245,
            "download_url": "/api/reports/download/report_123456"
        }
        
        return report_content
    
    def _simulate_savings_transfer(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate savings transfer action"""
        transfer_data = action.get("data", {})
        
        return {
            "simulation": True,
            "transfer_amount": transfer_data.get("transfer_amount", 0),
            "from_account": "checking_001",
            "to_account": "savings_001",
            "purpose": transfer_data.get("goal_name", "General Savings"),
            "scheduled_date": "2024-01-15",
            "confirmation_code": "SIM_TRANSFER_123456"
        }
    
    def _simulate_portfolio_rebalancing(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate portfolio rebalancing action"""
        rebalancing_data = action.get("data", {})
        target_allocation = rebalancing_data.get("target_allocation", {})
        
        # Simulate current vs target allocation
        current_allocation = {
            "US_Stocks": 45,
            "International_Stocks": 15,
            "Bonds": 30,
            "REITs": 7,
            "Commodities": 3
        }
        
        trades_needed = []
        for asset, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset, 0)
            difference = target_pct - current_pct
            
            if abs(difference) > rebalancing_data.get("rebalancing_threshold", 5):
                action_type = "buy" if difference > 0 else "sell"
                trades_needed.append({
                    "asset": asset,
                    "action": action_type,
                    "amount_pct": abs(difference),
                    "estimated_value": abs(difference) * 100  # $100 per percentage point
                })
        
        return {
            "simulation": True,
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "trades_needed": trades_needed,
            "estimated_total_trades": len(trades_needed),
            "estimated_cost": sum([trade["estimated_value"] for trade in trades_needed]),
            "rebalancing_date": "2024-01-20"
        }
    
    def _create_execution_summary(self, executed_actions: List[Dict], suggested_actions: List[Dict]) -> Dict[str, Any]:
        """Create summary of action execution"""
        return {
            "total_executed": len(executed_actions),
            "total_suggested": len(suggested_actions),
            "execution_rate": len(executed_actions) / (len(executed_actions) + len(suggested_actions)) * 100 if (executed_actions or suggested_actions) else 0,
            "completed_actions": [action["action"] for action in executed_actions if action.get("status") == "completed"],
            "failed_actions": [action["action"] for action in executed_actions if action.get("status") == "failed"],
            "high_priority_suggestions": [action["description"] for action in suggested_actions if action.get("priority") == "high"],
            "next_steps": [
                "Review suggested actions for manual execution",
                "Enable automated execution for supported actions",
                "Monitor executed actions for effectiveness"
            ]
        }