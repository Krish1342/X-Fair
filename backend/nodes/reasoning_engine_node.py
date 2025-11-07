"""
Reasoning Engine Node - Planner and structured plans
Stage 2: Intermediate and Stage 3: Advanced
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from core.state import FinanceAgentState, SystemStage

logger = logging.getLogger(__name__)


class ReasoningEngineNode:
    """Advanced reasoning engine for financial planning"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Apply reasoning and planning logic with fallback handling"""
        try:
            stage = state.get("system_stage", SystemStage.INTERMEDIATE)
            analysis_results = state.get("analysis_results", {})
            
            # Check if we have enough data to proceed
            if not analysis_results:
                logger.warning("No analysis results available - using fallback response")
                state["analysis_results"]["reasoning_analysis"] = self._generate_fallback_response(state)
                return state
                
            # Proceed with normal reasoning if we have data
            if stage == SystemStage.INTERMEDIATE:
                reasoning_result = self._intermediate_reasoning(state)
            else:  # ADVANCED
                reasoning_result = self._advanced_reasoning(state)
            
            # Add recommendations based on financial health
            health_score = reasoning_result.get("context_analysis", {}).get("financial_health_score", 0)
            reasoning_result["health_based_recommendations"] = self._get_health_score_recommendations(health_score)
            
            state["analysis_results"]["reasoning_analysis"] = reasoning_result
            state["tools_used"] = state.get("tools_used", []) + ["reasoning_engine"]
            state["current_node"] = "reasoning_engine"
            
            logger.info(f"Reasoning engine completed for {stage} stage with health score {health_score}")
            
        except Exception as e:
            logger.error(f"Reasoning engine error: {e}")
            state["error_message"] = str(e)
            state["analysis_results"]["reasoning_analysis"] = self._generate_fallback_response(state)
        
        return state
    
    def _intermediate_reasoning(self, state: FinanceAgentState) -> Dict[str, Any]:
        """Intermediate stage reasoning with basic planning"""
        user_query = state.get("user_query", "")
        analysis_results = state.get("analysis_results", {})
        
        # Analyze available data
        context_analysis = self._analyze_financial_context(analysis_results)
        
        # Generate structured plan
        plan = self._create_intermediate_plan(user_query, context_analysis)
        
        # Create recommendations
        recommendations = self._generate_intermediate_recommendations(context_analysis)
        
        return {
            "reasoning_level": "intermediate",
            "context_analysis": context_analysis,
            "structured_plan": plan,
            "recommendations": recommendations,
            "confidence": 0.8
        }
    
    def _advanced_reasoning(self, state: FinanceAgentState) -> Dict[str, Any]:
        """Advanced stage reasoning with LLM and symbolic reasoning"""
        user_query = state.get("user_query", "")
        analysis_results = state.get("analysis_results", {})
        
        # Deep analysis with multiple perspectives
        context_analysis = self._analyze_financial_context(analysis_results)
        
        # Generate comprehensive strategic plan
        strategic_plan = self._create_strategic_plan(user_query, context_analysis)
        
        # LLM-enhanced reasoning
        llm_insights = self._llm_enhanced_reasoning(user_query, context_analysis)
        
        # Symbolic reasoning for optimization
        optimization_results = self._symbolic_reasoning(context_analysis)
        
        return {
            "reasoning_level": "advanced",
            "context_analysis": context_analysis,
            "strategic_plan": strategic_plan,
            "llm_insights": llm_insights,
            "optimization_results": optimization_results,
            "confidence": 0.95
        }
    
    def _analyze_financial_context(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the financial context from all available data with enhanced extraction"""
        context = {
            "financial_health_score": 0,
            "key_metrics": {},
            "risk_factors": [],
            "opportunities": [],
            "data_completeness": 0,
            "income_stability": "unknown",
            "debt_status": "unknown",
            "savings_rate": 0.0,
            "investment_diversification": "unknown",
            "emergency_fund_status": "unknown"
        }
        
        # Analyze budget data with enhanced metrics
        if "budget_analysis" in analysis_results:
            budget = analysis_results["budget_analysis"]
            
            # Core metrics
            monthly_income = budget.get("total_income", 0)
            monthly_expenses = budget.get("total_expenses", 0)
            context["key_metrics"].update({
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "expense_categories": len(budget.get("category_totals", {})),
                "discretionary_spending": budget.get("discretionary_spending", 0),
                "fixed_expenses": budget.get("fixed_expenses", 0)
            })
            
            # Calculate savings rate and financial health indicators
            if monthly_income > 0:
                savings_rate = (monthly_income - monthly_expenses) / monthly_income * 100
                context["savings_rate"] = round(savings_rate, 2)
                
                if savings_rate >= 20:
                    context["financial_health_score"] += 25
                    context["opportunities"].append("Strong savings rate")
                elif savings_rate < 10:
                    context["risk_factors"].append("Low savings rate")
            
            # Investment analysis
            investment_pct = budget.get("category_percentages", {}).get("Investment", 0)
            if investment_pct > 20:
                context["financial_health_score"] += 30
                context["opportunities"].append("Strong investment discipline")
            elif investment_pct < 10:
                context["risk_factors"].append("Low investment savings rate")
            
            context["data_completeness"] += 25
        
        # Analyze goal data
        if "goals_analysis" in analysis_results:
            goals = analysis_results["goals_analysis"]
            context["key_metrics"]["total_monthly_savings_needed"] = goals.get("total_monthly_required", 0)
            context["key_metrics"]["number_of_goals"] = len(goals.get("goals", []))
            
            if goals.get("total_monthly_required", 0) > 0:
                context["opportunities"].append("Clear financial goals defined")
                context["financial_health_score"] += 20
            
            context["data_completeness"] += 25
        
        # Analyze knowledge retrieval
        if "knowledge_retrieval" in analysis_results:
            knowledge = analysis_results["knowledge_retrieval"]
            if knowledge.get("knowledge_used"):
                context["opportunities"].append("Access to relevant financial knowledge")
                context["financial_health_score"] += 10
            
            context["data_completeness"] += 25
        
        # Risk assessment
        if context["financial_health_score"] < 30:
            context["risk_factors"].append("Below-average financial health indicators")
        
        return context
    
    def _create_intermediate_plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured plan for intermediate stage"""
        plan = {
            "phase_1": "Assessment and Foundation",
            "phase_2": "Implementation",
            "phase_3": "Monitoring and Adjustment",
            "timeline": "3-6 months",
            "steps": []
        }
        
        # Phase 1 steps
        plan["steps"].extend([
            {
                "phase": 1,
                "action": "Complete financial assessment",
                "description": "Gather all financial data including income, expenses, assets, and debts",
                "timeline": "Week 1-2"
            },
            {
                "phase": 1,
                "action": "Establish emergency fund target",
                "description": "Calculate 3-6 months of essential expenses",
                "timeline": "Week 2"
            }
        ])
        
        # Phase 2 steps based on context
        if context["key_metrics"].get("monthly_expenses", 0) > 0:
            plan["steps"].append({
                "phase": 2,
                "action": "Optimize budget allocation",
                "description": "Implement 50/30/20 rule or zero-based budgeting",
                "timeline": "Week 3-6"
            })
        
        if len(context["risk_factors"]) > 0:
            plan["steps"].append({
                "phase": 2,
                "action": "Address risk factors",
                "description": f"Focus on: {', '.join(context['risk_factors'][:2])}",
                "timeline": "Week 4-8"
            })
        
        # Phase 3 steps
        plan["steps"].extend([
            {
                "phase": 3,
                "action": "Monthly progress review",
                "description": "Track progress on goals and adjust as needed",
                "timeline": "Ongoing"
            },
            {
                "phase": 3,
                "action": "Quarterly plan optimization",
                "description": "Review and optimize financial strategy",
                "timeline": "Every 3 months"
            }
        ])
        
        return plan
    
    def _create_strategic_plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive strategic plan for advanced stage"""
        plan = {
            "strategy_type": "Comprehensive Financial Optimization",
            "time_horizon": "1-5 years",
            "phases": {
                "immediate": "0-3 months",
                "short_term": "3-12 months", 
                "medium_term": "1-3 years",
                "long_term": "3-5 years"
            },
            "strategic_pillars": []
        }
        
        # Define strategic pillars based on context
        if context["financial_health_score"] < 50:
            plan["strategic_pillars"].append({
                "pillar": "Financial Stabilization",
                "priority": "Critical",
                "objectives": [
                    "Establish emergency fund",
                    "Optimize cash flow",
                    "Reduce high-interest debt"
                ],
                "timeline": "immediate"
            })
        
        plan["strategic_pillars"].append({
            "pillar": "Investment Optimization",
            "priority": "High",
            "objectives": [
                "Maximize tax-advantaged accounts",
                "Optimize asset allocation",
                "Implement dollar-cost averaging"
            ],
            "timeline": "short_term"
        })
        
        plan["strategic_pillars"].append({
            "pillar": "Tax Optimization",
            "priority": "Medium",
            "objectives": [
                "Maximize deductions",
                "Optimize retirement contributions",
                "Consider tax-loss harvesting"
            ],
            "timeline": "medium_term"
        })
        
        plan["strategic_pillars"].append({
            "pillar": "Wealth Accumulation",
            "priority": "High", 
            "objectives": [
                "Diversify investment portfolio",
                "Consider alternative investments",
                "Plan for major financial goals"
            ],
            "timeline": "long_term"
        })
        
        return plan
    
    def _generate_intermediate_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate recommendations for intermediate stage"""
        recommendations = []
        
        health_score = context["financial_health_score"]
        
        if health_score < 30:
            recommendations.append("🚨 Focus on financial fundamentals: emergency fund and debt reduction")
        elif health_score < 60:
            recommendations.append("📈 Good foundation - now optimize investment strategy")
        else:
            recommendations.append("⭐ Strong financial position - consider advanced strategies")
        
        # Context-specific recommendations
        for opportunity in context["opportunities"]:
            recommendations.append(f"✅ Leverage: {opportunity}")
        
        for risk in context["risk_factors"]:
            recommendations.append(f"⚠️ Address: {risk}")
        
        return recommendations
    
    def _llm_enhanced_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for enhanced reasoning and insights"""
        # This would use the Groq LLM for deeper analysis
        # For now, return structured insights
        return {
            "strategic_insights": [
                "Market conditions favor long-term investment strategies",
                "Current tax environment benefits retirement account contributions",
                "Interest rate trends suggest refinancing opportunities"
            ],
            "personalized_advice": [
                "Based on your profile, consider increasing investment allocation",
                "Your risk tolerance aligns with moderate portfolio strategy",
                "Time horizon supports aggressive growth approach"
            ],
            "market_considerations": [
                "Inflation trends impact fixed-income strategies", 
                "Sector rotation opportunities in technology and healthcare",
                "Currency fluctuations affect international investments"
            ]
        }
    
    def _symbolic_reasoning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply symbolic reasoning for optimization"""
        optimization = {
            "budget_optimization": {},
            "tax_optimization": {},
            "investment_optimization": {}
        }
        
        # Budget optimization logic
        monthly_expenses = context["key_metrics"].get("monthly_expenses", 0)
        if monthly_expenses > 0:
            optimization["budget_optimization"] = {
                "recommended_emergency_fund": monthly_expenses * 6,
                "optimal_savings_rate": monthly_expenses * 0.2,
                "expense_reduction_target": monthly_expenses * 0.1
            }
        
        # Tax optimization
        optimization["tax_optimization"] = {
            "max_401k_contribution": 23000,  # 2024 limit
            "max_ira_contribution": 7000,   # 2024 limit
            "estimated_tax_savings": 7000   # Based on contributions
        }
        
        # Investment optimization
        optimization["investment_optimization"] = {
            "recommended_allocation": {
                "stocks": 70,
                "bonds": 20,
                "alternatives": 10
            },
            "rebalancing_frequency": "quarterly",
            "expected_annual_return": 7.5
        }
        
        return optimization
        
    def _generate_fallback_response(self, state: FinanceAgentState) -> Dict[str, Any]:
        """Generate a structured fallback response when analysis data is missing"""
        user_query = state.get("user_query", "")
        
        return {
            "reasoning_level": "basic",
            "status": "fallback",
            "timestamp": datetime.now().isoformat(),
            "message": "Unable to provide detailed analysis due to insufficient data",
            "context_analysis": {
                "financial_health_score": 0,
                "data_completeness": 0,
                "missing_data": ["budget", "goals", "transactions"],
                "required_actions": [
                    "Complete financial profile",
                    "Add monthly income and expenses",
                    "Set financial goals"
                ]
            },
            "basic_recommendations": [
                {
                    "type": "action",
                    "priority": "high",
                    "description": "Start by tracking your income and expenses",
                    "reason": "This will help us provide personalized recommendations"
                },
                {
                    "type": "information",
                    "priority": "medium",
                    "description": "Consider setting specific financial goals",
                    "reason": "Goals help guide better financial decisions"
                }
            ],
            "next_steps": {
                "immediate": "Complete your financial profile",
                "short_term": "Track expenses for at least one month",
                "support": "Contact support if you need help getting started"
            }
        }
    
    def _get_health_score_recommendations(self, health_score: float) -> List[Dict[str, Any]]:
        """Generate recommendations based on financial health score"""
        recommendations = []
        
        # Critical recommendations (health score < 30)
        if health_score < 30:
            recommendations.extend([
                {
                    "priority": "critical",
                    "category": "emergency_fund",
                    "action": "Build emergency fund immediately",
                    "target": "Save 3-6 months of expenses",
                    "reasoning": "Your financial security is at risk without an emergency fund"
                },
                {
                    "priority": "critical",
                    "category": "expense_management",
                    "action": "Review and cut non-essential expenses",
                    "target": "Reduce expenses by 20-30%",
                    "reasoning": "Your current spending patterns are unsustainable"
                }
            ])
        
        # Improvement recommendations (health score 30-60)
        elif health_score < 60:
            recommendations.extend([
                {
                    "priority": "high",
                    "category": "savings",
                    "action": "Increase savings rate",
                    "target": "Save 15-20% of income",
                    "reasoning": "Building stronger financial foundation"
                },
                {
                    "priority": "high",
                    "category": "debt_management",
                    "action": "Create debt reduction plan",
                    "target": "Pay off high-interest debt",
                    "reasoning": "Debt is limiting your financial growth"
                }
            ])
        
        # Optimization recommendations (health score 60-80)
        elif health_score < 80:
            recommendations.extend([
                {
                    "priority": "medium",
                    "category": "investment",
                    "action": "Optimize investment strategy",
                    "target": "Review and rebalance portfolio",
                    "reasoning": "Ensure investments align with goals"
                },
                {
                    "priority": "medium",
                    "category": "tax_planning",
                    "action": "Maximize tax advantages",
                    "target": "Review tax-advantaged accounts",
                    "reasoning": "Reduce tax burden and increase savings"
                }
            ])
        
        # Excellence recommendations (health score >= 80)
        else:
            recommendations.extend([
                {
                    "priority": "low",
                    "category": "wealth_building",
                    "action": "Consider advanced investment options",
                    "target": "Explore diversification opportunities",
                    "reasoning": "Ready for sophisticated strategies"
                },
                {
                    "priority": "low",
                    "category": "legacy_planning",
                    "action": "Develop estate plan",
                    "target": "Create or review estate documents",
                    "reasoning": "Protect and transfer wealth efficiently"
                }
            ])
        
        return recommendations