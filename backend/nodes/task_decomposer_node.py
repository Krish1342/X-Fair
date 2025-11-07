"""
Task Decomposer Node - Multi-step Plans
Stage 3: Advanced - Task Decomposer
"""
import logging
import re
from typing import Dict, Any, List
from core.state import FinanceAgentState
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskDecomposerNode:
    """Decomposes complex financial tasks into actionable steps"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Decompose complex financial tasks"""
        try:
            user_query = state.get("user_query", "")
            analysis_results = state.get("analysis_results", {})
            
            # Identify task complexity and decompose
            task_analysis = self._analyze_task_complexity(user_query)
            decomposed_tasks = self._decompose_financial_task(user_query, task_analysis, analysis_results)
            execution_plan = self._create_execution_plan(decomposed_tasks)
            
            # Generate human-readable summary
            human_readable_summary = self._generate_plan_summary(user_query, decomposed_tasks, execution_plan)
            
            # Create structured JSON response
            state["analysis_results"]["task_decomposition"] = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "query": user_query,
                "task_analysis": task_analysis,
                "plan": {
                    "tasks": decomposed_tasks,
                    "execution": execution_plan,
                    "summary": human_readable_summary,
                    "metadata": {
                        "total_tasks": len(decomposed_tasks),
                        "estimated_duration": self._calculate_total_duration(decomposed_tasks),
                        "complexity_level": task_analysis["complexity_level"],
                        "critical_tasks": len([t for t in decomposed_tasks if t.get("priority") == "Critical"]),
                        "success_criteria": self._define_success_criteria(decomposed_tasks)
                    }
                }
            }
            
            state["tools_used"] = state.get("tools_used", []) + ["task_decomposer"]
            state["current_node"] = "task_decomposer"
            
            logger.info(f"Successfully decomposed task into {len(decomposed_tasks)} subtasks")
            
        except Exception as e:
            logger.error(f"Task decomposition error: {e}")
            state["error_message"] = str(e)
            state["analysis_results"]["task_decomposition"] = self._generate_error_response(e, user_query)
        
        return state
    
    def _analyze_task_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze the complexity of the financial task"""
        complexity_indicators = {
            "multi_step": ["plan", "strategy", "roadmap", "process", "steps"],
            "long_term": ["retirement", "decades", "years", "long term", "future"],
            "multi_goal": ["goals", "multiple", "various", "several", "different"],
            "optimization": ["optimize", "best", "maximize", "minimize", "efficient"],
            "complex_analysis": ["analyze", "evaluate", "assess", "compare", "review"]
        }
        
        query_lower = query.lower()
        complexity_score = 0
        identified_aspects = []
        
        for aspect, keywords in complexity_indicators.items():
            if any(keyword in query_lower for keyword in keywords):
                complexity_score += 1
                identified_aspects.append(aspect)
        
        # Determine complexity level
        if complexity_score >= 3:
            complexity_level = "high"
        elif complexity_score >= 2:
            complexity_level = "medium"
        else:
            complexity_level = "low"
        
        return {
            "complexity_level": complexity_level,
            "complexity_score": complexity_score,
            "identified_aspects": identified_aspects,
            "requires_decomposition": complexity_score >= 2
        }
    
    def _decompose_financial_task(self, query: str, task_analysis: Dict, analysis_results: Dict) -> List[Dict[str, Any]]:
        """Decompose financial task into manageable subtasks"""
        query_lower = query.lower()
        subtasks = []
        
        # Common financial task patterns
        if any(keyword in query_lower for keyword in ["retirement", "retire"]):
            subtasks.extend(self._decompose_retirement_planning())
        
        elif any(keyword in query_lower for keyword in ["house", "home", "buy"]):
            subtasks.extend(self._decompose_home_buying())
        
        elif any(keyword in query_lower for keyword in ["debt", "pay off", "eliminate"]):
            subtasks.extend(self._decompose_debt_elimination())
        
        elif any(keyword in query_lower for keyword in ["invest", "portfolio", "allocation"]):
            subtasks.extend(self._decompose_investment_strategy())
        
        elif any(keyword in query_lower for keyword in ["budget", "spending", "expense"]):
            subtasks.extend(self._decompose_budget_optimization())
        
        elif any(keyword in query_lower for keyword in ["tax", "optimize", "deduction"]):
            subtasks.extend(self._decompose_tax_optimization())
        
        else:
            # Generic financial planning decomposition
            subtasks.extend(self._decompose_general_financial_planning())
        
        # Add complexity-based additional tasks
        if task_analysis["complexity_level"] == "high":
            subtasks.extend(self._add_advanced_tasks(query_lower))
        
        return subtasks
    
    def _decompose_retirement_planning(self) -> List[Dict[str, Any]]:
        """Decompose retirement planning into subtasks"""
        return [
            {
                "task_id": "retirement_1",
                "title": "Calculate Retirement Needs",
                "description": "Determine how much money you'll need in retirement based on current expenses and lifestyle goals",
                "priority": "Critical",
                "estimated_time": "2-3 hours",
                "dependencies": [],
                "deliverables": ["Retirement income target", "Expense projections"],
                "tools_needed": ["Calculator", "Expense tracking"]
            },
            {
                "task_id": "retirement_2", 
                "title": "Assess Current Retirement Savings",
                "description": "Review all retirement accounts (401k, IRA, etc.) and calculate current savings rate",
                "priority": "Critical",
                "estimated_time": "1-2 hours",
                "dependencies": ["retirement_1"],
                "deliverables": ["Account summary", "Savings rate analysis"],
                "tools_needed": ["Account statements", "Savings calculator"]
            },
            {
                "task_id": "retirement_3",
                "title": "Optimize Retirement Contributions",
                "description": "Maximize employer matches and increase contribution rates to meet retirement goals",
                "priority": "High",
                "estimated_time": "1 hour",
                "dependencies": ["retirement_2"],
                "deliverables": ["Updated contribution plan", "Tax optimization strategy"],
                "tools_needed": ["Payroll system", "HR benefits portal"]
            },
            {
                "task_id": "retirement_4",
                "title": "Develop Investment Strategy",
                "description": "Create age-appropriate asset allocation and select low-cost investment options",
                "priority": "High",
                "estimated_time": "2-4 hours",
                "dependencies": ["retirement_2"],
                "deliverables": ["Asset allocation plan", "Investment selections"],
                "tools_needed": ["Investment research", "Risk assessment"]
            },
            {
                "task_id": "retirement_5",
                "title": "Create Monitoring System",
                "description": "Set up regular review schedule and progress tracking system",
                "priority": "Medium",
                "estimated_time": "30 minutes",
                "dependencies": ["retirement_3", "retirement_4"],
                "deliverables": ["Review schedule", "Progress tracking system"],
                "tools_needed": ["Calendar", "Spreadsheet or app"]
            }
        ]
    
    def _decompose_home_buying(self) -> List[Dict[str, Any]]:
        """Decompose home buying process"""
        return [
            {
                "task_id": "home_1",
                "title": "Determine Home Affordability",
                "description": "Calculate how much house you can afford based on income, debts, and down payment",
                "priority": "Critical",
                "estimated_time": "1-2 hours",
                "dependencies": [],
                "deliverables": ["Affordability range", "Monthly payment estimate"],
                "tools_needed": ["Mortgage calculator", "Income verification"]
            },
            {
                "task_id": "home_2",
                "title": "Save for Down Payment",
                "description": "Create savings plan for down payment and closing costs",
                "priority": "Critical",
                "estimated_time": "Ongoing",
                "dependencies": ["home_1"],
                "deliverables": ["Savings timeline", "Monthly savings target"],
                "tools_needed": ["Savings account", "Automatic transfers"]
            },
            {
                "task_id": "home_3",
                "title": "Improve Credit Score",
                "description": "Optimize credit score to qualify for better mortgage rates",
                "priority": "High",
                "estimated_time": "3-6 months",
                "dependencies": [],
                "deliverables": ["Credit report review", "Score improvement plan"],
                "tools_needed": ["Credit monitoring", "Debt paydown plan"]
            },
            {
                "task_id": "home_4",
                "title": "Get Pre-approved for Mortgage",
                "description": "Shop for mortgage rates and get pre-approval letter",
                "priority": "High",
                "estimated_time": "2-3 weeks",
                "dependencies": ["home_2", "home_3"],
                "deliverables": ["Pre-approval letter", "Rate comparison"],
                "tools_needed": ["Financial documents", "Lender applications"]
            }
        ]
    
    def _decompose_debt_elimination(self) -> List[Dict[str, Any]]:
        """Decompose debt elimination strategy"""
        return [
            {
                "task_id": "debt_1",
                "title": "List All Debts",
                "description": "Create comprehensive list of all debts with balances, rates, and minimum payments",
                "priority": "Critical",
                "estimated_time": "1 hour",
                "dependencies": [],
                "deliverables": ["Debt inventory", "Total debt amount"],
                "tools_needed": ["Statements", "Spreadsheet"]
            },
            {
                "task_id": "debt_2",
                "title": "Choose Payoff Strategy",
                "description": "Select between debt avalanche (highest rate first) or snowball (smallest balance first)",
                "priority": "High",
                "estimated_time": "30 minutes",
                "dependencies": ["debt_1"],
                "deliverables": ["Payoff strategy", "Prioritized debt list"],
                "tools_needed": ["Debt calculator", "Strategy comparison"]
            },
            {
                "task_id": "debt_3",
                "title": "Increase Available Payment Amount",
                "description": "Find extra money in budget to accelerate debt payoff",
                "priority": "High",
                "estimated_time": "2 hours",
                "dependencies": ["debt_1"],
                "deliverables": ["Budget optimization", "Extra payment amount"],
                "tools_needed": ["Budget analysis", "Expense cutting"]
            },
            {
                "task_id": "debt_4",
                "title": "Implement Payoff Plan",
                "description": "Set up automatic payments and track progress",
                "priority": "Medium",
                "estimated_time": "1 hour",
                "dependencies": ["debt_2", "debt_3"],
                "deliverables": ["Payment schedule", "Progress tracking"],
                "tools_needed": ["Banking system", "Tracking app"]
            }
        ]
    
    def _decompose_investment_strategy(self) -> List[Dict[str, Any]]:
        """Decompose investment strategy development"""
        return [
            {
                "task_id": "invest_1",
                "title": "Define Investment Goals",
                "description": "Clarify investment objectives, time horizon, and risk tolerance",
                "priority": "Critical",
                "estimated_time": "1 hour",
                "dependencies": [],
                "deliverables": ["Investment objectives", "Risk assessment"],
                "tools_needed": ["Goal worksheet", "Risk questionnaire"]
            },
            {
                "task_id": "invest_2",
                "title": "Determine Asset Allocation",
                "description": "Create target allocation between stocks, bonds, and other asset classes",
                "priority": "High",
                "estimated_time": "1-2 hours", 
                "dependencies": ["invest_1"],
                "deliverables": ["Asset allocation plan", "Target percentages"],
                "tools_needed": ["Allocation calculator", "Historical data"]
            },
            {
                "task_id": "invest_3",
                "title": "Select Investment Vehicles",
                "description": "Choose specific funds, ETFs, or individual securities",
                "priority": "High",
                "estimated_time": "2-3 hours",
                "dependencies": ["invest_2"],
                "deliverables": ["Investment selections", "Cost analysis"],
                "tools_needed": ["Investment research", "Fee comparison"]
            },
            {
                "task_id": "invest_4",
                "title": "Implement Investment Plan",
                "description": "Execute purchases and set up automatic investing",
                "priority": "Medium",
                "estimated_time": "1 hour",
                "dependencies": ["invest_3"],
                "deliverables": ["Portfolio implementation", "Automatic investing setup"],
                "tools_needed": ["Brokerage account", "Investment platform"]
            }
        ]
    
    def _decompose_budget_optimization(self) -> List[Dict[str, Any]]:
        """Decompose budget optimization"""
        return [
            {
                "task_id": "budget_1",
                "title": "Track Current Spending",
                "description": "Monitor and categorize all expenses for at least one month",
                "priority": "Critical",
                "estimated_time": "Ongoing for 1 month",
                "dependencies": [],
                "deliverables": ["Expense tracking data", "Spending categories"],
                "tools_needed": ["Expense tracking app", "Bank statements"]
            },
            {
                "task_id": "budget_2",
                "title": "Analyze Spending Patterns",
                "description": "Identify areas of overspending and potential savings opportunities",
                "priority": "High",
                "estimated_time": "2 hours",
                "dependencies": ["budget_1"],
                "deliverables": ["Spending analysis", "Savings opportunities"],
                "tools_needed": ["Spreadsheet", "Budget calculator"]
            },
            {
                "task_id": "budget_3",
                "title": "Create Optimized Budget",
                "description": "Design new budget with improved allocation and savings targets",
                "priority": "High",
                "estimated_time": "1-2 hours",
                "dependencies": ["budget_2"],
                "deliverables": ["New budget plan", "Savings targets"],
                "tools_needed": ["Budget template", "Goal setting"]
            }
        ]
    
    def _decompose_tax_optimization(self) -> List[Dict[str, Any]]:
        """Decompose tax optimization strategy"""
        return [
            {
                "task_id": "tax_1",
                "title": "Review Current Tax Situation",
                "description": "Analyze last year's tax return and current year projections",
                "priority": "High",
                "estimated_time": "1-2 hours",
                "dependencies": [],
                "deliverables": ["Tax analysis", "Current year projection"],
                "tools_needed": ["Tax returns", "Tax calculator"]
            },
            {
                "task_id": "tax_2",
                "title": "Maximize Deductions",
                "description": "Identify and implement strategies to increase tax deductions",
                "priority": "High",
                "estimated_time": "2 hours",
                "dependencies": ["tax_1"],
                "deliverables": ["Deduction optimization plan", "Documentation system"],
                "tools_needed": ["Deduction tracker", "Tax software"]
            },
            {
                "task_id": "tax_3",
                "title": "Optimize Retirement Contributions",
                "description": "Maximize tax-deferred retirement account contributions",
                "priority": "Medium",
                "estimated_time": "1 hour",
                "dependencies": ["tax_1"],
                "deliverables": ["Contribution optimization", "Tax savings estimate"],
                "tools_needed": ["Contribution calculator", "Payroll changes"]
            }
        ]
    
    def _decompose_general_financial_planning(self) -> List[Dict[str, Any]]:
        """Generic financial planning decomposition"""
        return [
            {
                "task_id": "general_1",
                "title": "Assess Current Financial Position",
                "description": "Calculate net worth and analyze cash flow",
                "priority": "Critical",
                "estimated_time": "2-3 hours",
                "dependencies": [],
                "deliverables": ["Net worth statement", "Cash flow analysis"],
                "tools_needed": ["Financial statements", "Calculator"]
            },
            {
                "task_id": "general_2",
                "title": "Set Financial Goals",
                "description": "Define short-term and long-term financial objectives",
                "priority": "High",
                "estimated_time": "1-2 hours",
                "dependencies": ["general_1"],
                "deliverables": ["Goal list", "Target timelines"],
                "tools_needed": ["Goal worksheet", "Planning tools"]
            },
            {
                "task_id": "general_3",
                "title": "Create Action Plan",
                "description": "Develop specific steps to achieve financial goals",
                "priority": "High",
                "estimated_time": "1-2 hours",
                "dependencies": ["general_2"],
                "deliverables": ["Action plan", "Implementation timeline"],
                "tools_needed": ["Planning template", "Task management"]
            }
        ]
    
    def _add_advanced_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Add advanced tasks for high complexity scenarios"""
        advanced_tasks = []
        
        if "optimize" in query:
            advanced_tasks.append({
                "task_id": "advanced_1",
                "title": "Perform Optimization Analysis",
                "description": "Use quantitative methods to optimize financial decisions",
                "priority": "Medium",
                "estimated_time": "2-4 hours",
                "dependencies": [],
                "deliverables": ["Optimization results", "Scenario analysis"],
                "tools_needed": ["Optimization software", "Financial modeling"]
            })
        
        if any(word in query for word in ["monitor", "track", "review"]):
            advanced_tasks.append({
                "task_id": "advanced_2",
                "title": "Implement Monitoring System",
                "description": "Set up automated tracking and alerting for key financial metrics",
                "priority": "Low",
                "estimated_time": "1-2 hours",
                "dependencies": [],
                "deliverables": ["Monitoring dashboard", "Alert system"],
                "tools_needed": ["Tracking tools", "Automation setup"]
            })
        
        return advanced_tasks
    
    def _create_execution_plan(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution plan from decomposed tasks"""
        # Sort tasks by priority and dependencies
        priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        sorted_tasks = sorted(subtasks, key=lambda x: priority_order.get(x["priority"], 5))
        
        # Calculate total estimated time
        total_time = self._calculate_total_duration(subtasks)
        
        # Create phases
        phases = {
            "Phase 1 - Foundation": [task for task in sorted_tasks if task["priority"] == "Critical"],
            "Phase 2 - Implementation": [task for task in sorted_tasks if task["priority"] == "High"],
            "Phase 3 - Optimization": [task for task in sorted_tasks if task["priority"] in ["Medium", "Low"]]
        }
        
        # Enhanced execution plan with more structured metadata
        return {
            "total_tasks": len(subtasks),
            "total_estimated_time_hours": total_time,
            "phases": phases,
            "critical_path": [task["task_id"] for task in sorted_tasks if task["priority"] == "Critical"],
            "timeline": self._generate_timeline(sorted_tasks),
            "success_criteria": self._define_success_criteria(subtasks),
            "risk_factors": self._identify_risk_factors(subtasks),
            "dependencies": self._analyze_dependencies(sorted_tasks)
        }
    
    def _generate_plan_summary(self, query: str, tasks: List[Dict[str, Any]], plan: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the financial plan"""
        
        summary_template = """
Financial Plan Summary for: {query}

Complexity Level: {complexity}
Total Tasks: {total_tasks}
Estimated Duration: {duration} hours

Key Phases:
{phases}

Critical Tasks:
{critical_tasks}

Timeline Overview:
{timeline}

Success Criteria:
{success_criteria}

Risk Factors to Consider:
{risks}
"""
        # Format phases
        phase_summary = []
        for phase_name, phase_tasks in plan["phases"].items():
            if phase_tasks:
                phase_summary.append(f"• {phase_name}: {len(phase_tasks)} tasks")
        
        # Format critical tasks
        critical_tasks = [task for task in tasks if task.get("priority") == "Critical"]
        critical_summary = "\n".join([f"• {task['title']}" for task in critical_tasks]) if critical_tasks else "No critical tasks identified"
        
        return summary_template.format(
            query=query,
            complexity=plan.get("complexity_level", "Medium"),
            total_tasks=plan["total_tasks"],
            duration=round(plan["total_estimated_time_hours"], 1),
            phases="\n".join(phase_summary),
            critical_tasks=critical_summary,
            timeline="\n".join([f"• {item}" for item in plan["timeline"]]),
            success_criteria="\n".join([f"• {item}" for item in plan["success_criteria"]]),
            risks="\n".join([f"• {item}" for item in plan["risk_factors"]])
        )
    
    def _calculate_total_duration(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate total duration in hours from task list"""
        return sum(self._parse_time_estimate(task.get("estimated_time", "1 hour")) for task in tasks)
    
    def _define_success_criteria(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Define clear success criteria based on tasks"""
        criteria = [
            "All critical tasks completed successfully",
            f"Minimum {len([t for t in tasks if t.get('priority') in ['Critical', 'High']])} high-priority tasks completed",
            "Key deliverables produced and verified",
            "No blocking issues remaining"
        ]
        
        # Add task-specific criteria
        for task in tasks:
            if task.get("deliverables"):
                for deliverable in task["deliverables"]:
                    criteria.append(f"Completed: {deliverable}")
        
        return list(set(criteria))  # Remove duplicates
    
    def _generate_timeline(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate a timeline of major milestones"""
        timeline = []
        current_week = 1
        current_phase = None
        
        for task in tasks:
            task_time = self._parse_time_estimate(task.get("estimated_time", "1 hour"))
            if task_time >= 8:  # Only include significant milestones (1+ day)
                timeline.append(f"Week {current_week}: {task['title']}")
                if task_time > 40:  # More than a week
                    current_week += int(task_time / 40)
            
            if task.get("priority") != current_phase:
                current_phase = task.get("priority")
                if current_phase:
                    timeline.append(f"Begin {current_phase} priority tasks")
        
        return timeline
    
    def _identify_risk_factors(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Identify potential risk factors in the plan"""
        risks = [
            "Market volatility and economic changes",
            "Changes in personal financial situation",
            "External dependencies and delays"
        ]
        
        # Add task-specific risks
        for task in tasks:
            if task.get("priority") == "Critical":
                risks.append(f"Failure to complete: {task['title']}")
            if task.get("dependencies"):
                risks.append(f"Dependency chain delays for: {task['title']}")
        
        return list(set(risks))  # Remove duplicates
    
    def _analyze_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze task dependencies and create dependency map"""
        dependency_map = []
        for task in tasks:
            if task.get("dependencies"):
                dependency_map.append({
                    "task_id": task["task_id"],
                    "title": task["title"],
                    "depends_on": task["dependencies"],
                    "estimated_start": self._calculate_earliest_start(task, tasks)
                })
        return dependency_map
    
    def _calculate_earliest_start(self, task: Dict[str, Any], all_tasks: List[Dict[str, Any]]) -> str:
        """Calculate earliest possible start time for a task based on dependencies"""
        if not task.get("dependencies"):
            return "Immediately"
            
        dependent_tasks = [t for t in all_tasks if t["task_id"] in task["dependencies"]]
        if not dependent_tasks:
            return "After prerequisite completion"
            
        total_prereq_time = sum(self._parse_time_estimate(t.get("estimated_time", "1 hour")) 
                               for t in dependent_tasks)
        
        if total_prereq_time < 8:
            return f"After {round(total_prereq_time, 1)} hours"
        elif total_prereq_time < 40:
            return f"After {round(total_prereq_time/8, 1)} days"
        else:
            return f"After {round(total_prereq_time/40, 1)} weeks"
    
    def _generate_error_response(self, error: Exception, query: str) -> Dict[str, Any]:
        """Generate a structured error response with fallback suggestions"""
        return {
            "status": "error",
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "fallback_suggestions": {
                "message": "Unable to create detailed plan. Consider breaking down your request:",
                "alternative_queries": [
                    f"What's the first step to {query.lower()}?",
                    "Can you explain the basic requirements?",
                    "What are the key components to consider?"
                ],
                "simplified_approach": [
                    "Start with a smaller scope",
                    "Focus on immediate next actions",
                    "Consult with a financial advisor"
                ]
            }
        }
    
    def _parse_time_estimate(self, time_str: str) -> float:
        """Parse time estimate string to hours"""
        try:
            time_str = str(time_str).lower()
            numbers = re.findall(r'\d+', time_str)
            
            if not numbers:
                return 1.0  # Default to 1 hour if no numbers found
                
            value = float(numbers[0])
            
            if "minute" in time_str:
                return value / 60
            elif "hour" in time_str:
                return value
            elif "day" in time_str:
                return value * 8  # 8 hours per day
            elif "week" in time_str:
                return value * 40  # 40 hours per week
            elif "month" in time_str:
                return value * 160  # 160 hours per month
            
            return value  # Default to treating number as hours
            
        except Exception as e:
            logger.warning(f"Error parsing time estimate '{time_str}': {e}")
            return 1.0  # Default to 1 hour on error