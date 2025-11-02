"""
Reasoning Engine Node - Planner and structured plans
Stage 2: Intermediate and Stage 3: Advanced
"""
import logging
from typing import Dict, Any, List
from core.state import FinanceAgentState, SystemStage

logger = logging.getLogger(__name__)


class ReasoningEngineNode:
    """Advanced reasoning engine for financial planning"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Apply reasoning and planning logic"""
        try:
            stage = state.get("system_stage", SystemStage.INTERMEDIATE)
            
            if stage == SystemStage.INTERMEDIATE:
                reasoning_result = self._intermediate_reasoning(state)
            else:  # ADVANCED
                reasoning_result = self._advanced_reasoning(state)
            
            state["analysis_results"]["reasoning_analysis"] = reasoning_result
            state["tools_used"] = state.get("tools_used", []) + ["reasoning_engine"]
            state["current_node"] = "reasoning_engine"
            
            logger.info(f"Reasoning engine completed for {stage} stage")
            
        except Exception as e:
            logger.error(f"Reasoning engine error: {e}")
            state["error_message"] = str(e)
        
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
        """Analyze the financial context from all available data"""
        context = {
            "financial_health_score": 0,
            "key_metrics": {},
            "risk_factors": [],
            "opportunities": [],
            "data_completeness": 0
        }
        
        # Analyze budget data
        if "budget_analysis" in analysis_results:
            budget = analysis_results["budget_analysis"]
            context["key_metrics"]["monthly_expenses"] = budget.get("total_expenses", 0)
            context["key_metrics"]["expense_categories"] = len(budget.get("category_totals", {}))
            
            # Calculate financial health indicators
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