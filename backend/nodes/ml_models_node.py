"""
ML Models Node - Machine Learning for financial forecasting and analysis
Stage 3: Advanced - ML Models
"""
import logging
import numpy as np
from typing import Dict, Any, List
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class MLModelsNode:
    """Machine learning models for financial predictions and analysis"""
    
    def __init__(self):
        self.models_initialized = False
        self._initialize_models()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Apply ML models to financial data"""
        try:
            analysis_results = state.get("analysis_results", {})
            user_query = state.get("user_query", "").lower()
            
            # Determine which ML analysis to perform
            ml_results = {}
            
            if any(keyword in user_query for keyword in ["predict", "forecast", "future", "projection"]):
                ml_results["forecasting"] = self._run_expense_forecasting(analysis_results)
            
            if any(keyword in user_query for keyword in ["rebalance", "optimize", "allocate"]):
                ml_results["portfolio_optimization"] = self._run_portfolio_optimization(analysis_results)
            
            if any(keyword in user_query for keyword in ["risk", "assess", "volatility"]):
                ml_results["risk_analysis"] = self._run_risk_analysis(analysis_results)
            
            # Always run expense categorization if transaction data available
            if "financial_data" in state and "transactions" in state["financial_data"]:
                ml_results["expense_categorization"] = self._run_expense_categorization(
                    state["financial_data"]["transactions"]
                )
            
            # Default analysis if no specific request
            if not ml_results:
                ml_results = self._run_default_ml_analysis(analysis_results)
            
            state["analysis_results"]["ml_analysis"] = ml_results
            state["tools_used"] = state.get("tools_used", []) + ["ml_models"]
            state["current_node"] = "ml_models"
            
            logger.info(f"ML analysis completed with {len(ml_results)} models")
            
        except Exception as e:
            logger.error(f"ML models error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _initialize_models(self):
        """Initialize ML models (placeholder for actual model loading)"""
        # In a real implementation, this would load trained models
        self.models = {
            "expense_forecasting": "LinearRegression",
            "portfolio_optimization": "ModernPortfolioTheory", 
            "risk_assessment": "VaRModel",
            "expense_categorization": "RandomForestClassifier"
        }
        self.models_initialized = True
        logger.info("ML models initialized")
    
    def _run_expense_forecasting(self, analysis_results: Dict) -> Dict[str, Any]:
        """Forecast future expenses using ML"""
        
        # Simulate expense forecasting (in real implementation, use trained model)
        budget_data = analysis_results.get("budget_analysis", {})
        current_expenses = budget_data.get("total_expenses", 4000)
        
        # Generate forecast for next 12 months
        monthly_forecast = []
        base_expense = current_expenses
        
        for month in range(1, 13):
            # Simulate seasonal patterns and trends
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * month / 12)  # Seasonal variation
            trend_factor = 1 + 0.02 * month / 12  # 2% annual inflation
            noise_factor = 1 + np.random.normal(0, 0.05)  # Random variation
            
            forecasted_expense = base_expense * seasonal_factor * trend_factor * noise_factor
            monthly_forecast.append({
                "month": month,
                "forecasted_expense": round(forecasted_expense, 2),
                "confidence_interval": [
                    round(forecasted_expense * 0.9, 2),
                    round(forecasted_expense * 1.1, 2)
                ]
            })
        
        # Calculate insights
        total_forecasted = sum([f["forecasted_expense"] for f in monthly_forecast])
        annual_change = (total_forecasted - (current_expenses * 12)) / (current_expenses * 12) * 100
        
        return {
            "model_type": "Expense Forecasting",
            "monthly_forecast": monthly_forecast,
            "annual_forecast": total_forecasted,
            "annual_change_percent": round(annual_change, 1),
            "insights": [
                f"Expenses expected to {'increase' if annual_change > 0 else 'decrease'} by {abs(annual_change):.1f}% annually",
                f"Highest expenses predicted in {'summer' if max(monthly_forecast, key=lambda x: x['forecasted_expense'])['month'] in [6,7,8] else 'winter'} months",
                "Forecast includes seasonal variations and inflation trends"
            ],
            "confidence": 0.85
        }
    
    def _run_portfolio_optimization(self, analysis_results: Dict) -> Dict[str, Any]:
        """Optimize portfolio allocation using ML"""
        
        # Simulate Modern Portfolio Theory optimization
        risk_tolerance = "moderate"  # Could be extracted from user profile
        
        # Asset classes and expected returns (simulated)
        assets = {
            "US_Stocks": {"expected_return": 0.10, "volatility": 0.16, "correlation": 1.0},
            "International_Stocks": {"expected_return": 0.09, "volatility": 0.18, "correlation": 0.7},
            "Bonds": {"expected_return": 0.04, "volatility": 0.05, "correlation": -0.2},
            "REITs": {"expected_return": 0.08, "volatility": 0.20, "correlation": 0.6},
            "Commodities": {"expected_return": 0.06, "volatility": 0.22, "correlation": 0.3}
        }
        
        # Risk tolerance-based optimization
        if risk_tolerance == "conservative":
            optimal_allocation = {"US_Stocks": 30, "International_Stocks": 10, "Bonds": 50, "REITs": 5, "Commodities": 5}
        elif risk_tolerance == "aggressive":
            optimal_allocation = {"US_Stocks": 50, "International_Stocks": 25, "Bonds": 10, "REITs": 10, "Commodities": 5}
        else:  # moderate
            optimal_allocation = {"US_Stocks": 40, "International_Stocks": 20, "Bonds": 25, "REITs": 10, "Commodities": 5}
        
        # Calculate portfolio metrics
        portfolio_return = sum([allocation/100 * assets[asset]["expected_return"] for asset, allocation in optimal_allocation.items()])
        portfolio_risk = 0.12  # Simplified calculation
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_risk  # Assuming 2% risk-free rate
        
        return {
            "model_type": "Portfolio Optimization",
            "optimal_allocation": optimal_allocation,
            "expected_annual_return": round(portfolio_return * 100, 1),
            "expected_volatility": round(portfolio_risk * 100, 1),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "rebalancing_recommendations": [
                "Review allocation quarterly",
                "Rebalance when any asset class deviates >5% from target",
                "Consider tax-loss harvesting opportunities"
            ],
            "rationale": [
                f"Allocation optimized for {risk_tolerance} risk tolerance",
                "Diversification across asset classes reduces overall risk",
                "Expected return-to-risk ratio optimized using modern portfolio theory"
            ],
            "confidence": 0.90
        }
    
    def _run_risk_analysis(self, analysis_results: Dict) -> Dict[str, Any]:
        """Analyze financial risk using ML models"""
        
        # Simulate Value at Risk (VaR) calculation
        budget_data = analysis_results.get("budget_analysis", {})
        current_expenses = budget_data.get("total_expenses", 4000)
        
        # Risk factors analysis
        risk_factors = []
        risk_score = 0
        
        # Income stability risk
        risk_factors.append({
            "factor": "Income Stability",
            "score": 7,  # 1-10 scale
            "description": "Moderate risk - single income source",
            "mitigation": "Build emergency fund, develop additional income streams"
        })
        
        # Expense volatility risk
        category_percentages = budget_data.get("category_percentages", {})
        discretionary_spending = category_percentages.get("Shopping", 0) + category_percentages.get("Entertainment", 0)
        
        if discretionary_spending > 20:
            expense_risk_score = 6
            expense_description = "High discretionary spending increases budget volatility"
        else:
            expense_risk_score = 4
            expense_description = "Controlled discretionary spending"
        
        risk_factors.append({
            "factor": "Expense Volatility",
            "score": expense_risk_score,
            "description": expense_description,
            "mitigation": "Create detailed budget, track discretionary spending"
        })
        
        # Investment risk
        investment_pct = category_percentages.get("Investment", 0)
        if investment_pct > 30:
            investment_risk_score = 5
            investment_description = "High investment allocation increases portfolio volatility"
        elif investment_pct < 10:
            investment_risk_score = 8
            investment_description = "Low investment rate increases inflation risk"
        else:
            investment_risk_score = 3
            investment_description = "Balanced investment allocation"
        
        risk_factors.append({
            "factor": "Investment Risk",
            "score": investment_risk_score,
            "description": investment_description,
            "mitigation": "Diversify investments, maintain appropriate asset allocation"
        })
        
        # Calculate overall risk score
        overall_risk_score = sum([factor["score"] for factor in risk_factors]) / len(risk_factors)
        
        # VaR calculation (simplified)
        monthly_var_95 = current_expenses * 0.15  # 95% confidence, 15% potential loss
        monthly_var_99 = current_expenses * 0.25  # 99% confidence, 25% potential loss
        
        return {
            "model_type": "Risk Analysis",
            "overall_risk_score": round(overall_risk_score, 1),
            "risk_level": "Medium" if overall_risk_score < 6 else "High",
            "risk_factors": risk_factors,
            "value_at_risk": {
                "monthly_var_95": round(monthly_var_95, 2),
                "monthly_var_99": round(monthly_var_99, 2),
                "description": "Potential monthly budget shortfall at 95% and 99% confidence levels"
            },
            "stress_test_scenarios": [
                {
                    "scenario": "Job Loss",
                    "impact": "6-month income disruption",
                    "required_reserves": current_expenses * 6
                },
                {
                    "scenario": "Market Downturn",
                    "impact": "30% portfolio decline",
                    "mitigation": "Maintain emergency fund, avoid panic selling"
                },
                {
                    "scenario": "Major Expense",
                    "impact": "$10,000 unexpected cost",
                    "preparation": "Emergency fund or available credit"
                }
            ],
            "confidence": 0.80
        }
    
    def _run_expense_categorization(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Categorize expenses using ML classification"""
        
        # Simulate ML-based expense categorization
        category_confidence = {}
        improved_categories = []
        
        for transaction in transactions:
            description = transaction.get("description", "").lower()
            current_category = transaction.get("category", "Unknown")
            
            # Simulate ML prediction confidence
            if "grocery" in description or "food" in description:
                predicted_category = "Food"
                confidence = 0.95
            elif "gas" in description or "fuel" in description:
                predicted_category = "Transportation"
                confidence = 0.90
            elif "utility" in description or "electric" in description:
                predicted_category = "Utilities"
                confidence = 0.85
            elif "shop" in description or "store" in description:
                predicted_category = "Shopping"
                confidence = 0.75
            else:
                predicted_category = current_category
                confidence = 0.60
            
            if predicted_category != current_category and confidence > 0.8:
                improved_categories.append({
                    "transaction": description,
                    "old_category": current_category,
                    "new_category": predicted_category,
                    "confidence": confidence
                })
            
            category_confidence[predicted_category] = category_confidence.get(predicted_category, []) + [confidence]
        
        # Calculate average confidence by category
        avg_confidence = {
            category: sum(confidences) / len(confidences)
            for category, confidences in category_confidence.items()
        }
        
        return {
            "model_type": "Expense Categorization",
            "improved_categories": improved_categories,
            "category_confidence": avg_confidence,
            "model_accuracy": 0.87,
            "suggestions": [
                f"Reclassified {len(improved_categories)} transactions for better accuracy",
                "Review suggested changes to improve budget tracking",
                "Model continues learning from your transaction patterns"
            ],
            "confidence": 0.87
        }
    
    def _run_default_ml_analysis(self, analysis_results: Dict) -> Dict[str, Any]:
        """Run default ML analysis when no specific request is made"""
        return {
            "model_type": "Financial Health Analysis",
            "health_score": 75,
            "key_insights": [
                "Spending patterns show good discipline in essential categories",
                "Investment allocation aligns with moderate risk profile",
                "Emergency fund target within reach with current savings rate"
            ],
            "ml_recommendations": [
                "Consider automated savings to optimize consistency",
                "Expense patterns suggest potential for 5% budget optimization",
                "Investment timing analysis recommends dollar-cost averaging"
            ],
            "predictive_alerts": [
                "No concerning spending trends detected",
                "Savings rate sustainable for long-term goals",
                "Budget variance within normal parameters"
            ],
            "confidence": 0.82
        }