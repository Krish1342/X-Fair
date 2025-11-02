"""
Intent Classifier Node - Uses Groq LLM to classify user intent
Routes to appropriate tools based on intent and system stage
"""
import logging
import json
from typing import Dict, Any
from core.state import FinanceAgentState, FinancialIntent

logger = logging.getLogger(__name__)


class IntentClassifierNode:
    """Classifies user intent using rule-based and LLM approaches"""
    
    def __init__(self, llm):
        self.llm = llm
        
        # Intent keywords mapping
        self.intent_keywords = {
            FinancialIntent.BUDGETING: [
                "budget", "spending", "expenses", "spend", "money", "cost", 
                "allocation", "track", "limit", "allowance"
            ],
            FinancialIntent.GOAL_PLANNING: [
                "goal", "save", "target", "plan", "future", "retirement", 
                "emergency fund", "vacation", "house", "car"
            ],
            FinancialIntent.BASIC_INSIGHTS: [
                "analyze", "insight", "report", "summary", "overview", 
                "health", "score", "trend", "pattern"
            ],
            FinancialIntent.TAX_ANALYSIS: [
                "tax", "deduction", "irs", "refund", "filing", "1099", 
                "w2", "write-off", "itemize"
            ],
            FinancialIntent.MARKET_DATA: [
                "market", "stock", "price", "nasdaq", "dow", "s&p", 
                "crypto", "bitcoin", "investment news"
            ],
            FinancialIntent.PORTFOLIO_TRACKING: [
                "portfolio", "investment", "return", "performance", 
                "asset", "allocation", "diversification", "roi"
            ],
            FinancialIntent.TASK_DECOMPOSITION: [
                "plan", "strategy", "step", "roadmap", "process", 
                "how to", "guide", "walkthrough"
            ],
            FinancialIntent.ML_FORECASTING: [
                "predict", "forecast", "future", "projection", "trend", 
                "estimate", "model", "ai prediction"
            ],
            FinancialIntent.PORTFOLIO_OPTIMIZATION: [
                "optimize", "rebalance", "best", "improve", "maximize", 
                "efficient", "allocate", "adjust"
            ],
            FinancialIntent.AUTOMATED_EXECUTION: [
                "execute", "buy", "sell", "trade", "transfer", "automate", 
                "action", "implement"
            ]
        }
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Classify user intent"""
        try:
            user_query = state.get("user_query", "").lower()
            
            # First try rule-based classification
            rule_based_intent, confidence = self._classify_with_rules(user_query)
            
            # If confidence is low, use LLM classification
            if confidence < 0.7:
                llm_intent, llm_confidence = self._classify_with_llm(user_query)
                if llm_confidence > confidence:
                    rule_based_intent = llm_intent
                    confidence = llm_confidence
            
            state["intent"] = rule_based_intent
            state["confidence_score"] = confidence
            state["tools_used"] = state.get("tools_used", []) + ["intent_classifier"]
            state["current_node"] = "intent_classifier"
            
            logger.info(f"Classified intent: {rule_based_intent} (confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            state["intent"] = FinancialIntent.UNKNOWN
            state["confidence_score"] = 0.0
            state["error_message"] = str(e)
        
        return state
    
    def _classify_with_rules(self, user_query: str) -> tuple[FinancialIntent, float]:
        """Rule-based intent classification using keyword matching"""
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in user_query:
                    # Weight longer keywords more heavily
                    score += len(keyword.split()) * 0.1
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return FinancialIntent.GENERAL_QUERY, 0.3
        
        # Get the highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent], 1.0)
        
        return best_intent, confidence
    
    def _classify_with_llm(self, user_query: str) -> tuple[FinancialIntent, float]:
        """LLM-based intent classification using Groq"""
        try:
            classification_prompt = f"""
            Classify the following financial query into one of these intents. 
            Respond with ONLY the intent name and confidence score (0.0-1.0) in JSON format.

            Available intents:
            - BUDGETING: Budget creation, spending analysis, expense tracking
            - GOAL_PLANNING: Financial goals, savings targets, planning
            - BASIC_INSIGHTS: Financial health, reports, summaries
            - TAX_ANALYSIS: Tax planning, deductions, filing
            - MARKET_DATA: Stock prices, market trends, financial news
            - PORTFOLIO_TRACKING: Investment performance, portfolio analysis
            - TASK_DECOMPOSITION: Step-by-step financial planning
            - ML_FORECASTING: Predictions, forecasts, projections
            - PORTFOLIO_OPTIMIZATION: Investment optimization, rebalancing
            - AUTOMATED_EXECUTION: Trading, transfers, automated actions
            - GENERAL_QUERY: General financial questions
            - UNKNOWN: Unclear or non-financial queries

            User query: "{user_query}"

            Response format: {{"intent": "INTENT_NAME", "confidence": 0.8}}
            """
            
            response = self.llm.invoke([{"role": "user", "content": classification_prompt}])
            result = json.loads(response.content)
            
            intent_name = result.get("intent", "UNKNOWN")
            confidence = float(result.get("confidence", 0.0))
            
            # Convert string to enum
            try:
                intent = FinancialIntent[intent_name]
            except KeyError:
                intent = FinancialIntent.UNKNOWN
                confidence = 0.0
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"LLM classification error: {e}")
            return FinancialIntent.UNKNOWN, 0.0