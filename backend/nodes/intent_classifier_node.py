"""
Intent Classifier Node - Uses Groq LLM to classify user intent
Routes to appropriate tools based on intent and system stage
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, cast
from core.state import FinanceAgentState, FinancialIntent, UserState

logger = logging.getLogger(__name__)

class IntentClassifierNode:
    """Classifies user intent using rule-based and LLM approaches"""
    
    def _is_demo_user(self, state: FinanceAgentState) -> bool:
        """Check if the current user is a demo user"""
        user_profile = state.get("user_profile")
        if user_profile and user_profile.email:
            return user_profile.email.endswith("@example.com")
        return False
    
    def _log_classification_result(self, query: str, intent: str, confidence: float,
                                method: str, is_demo: bool, threshold: float) -> None:
        """Log detailed classification results for analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "assigned_intent": intent,
            "confidence": confidence,
            "classification_method": method,
            "is_demo_user": is_demo,
            "confidence_threshold": threshold,
            "met_threshold": confidence >= threshold
        }
        logger.info(f"Intent Classification: {json.dumps(log_entry, indent=2)}")
    
    def _log_potential_misclassification(self, query: str, assigned_intent: str,
                                     confidence: float, state: FinanceAgentState) -> None:
        """Log queries that might be misclassified for further analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "assigned_intent": assigned_intent,
            "confidence": confidence,
            "user_type": "demo" if self._is_demo_user(state) else "standard",
            "context": {
                "system_stage": state.get("system_stage", "unknown"),
                "previous_intent": state.get("previous_intent", "none")
            }
        }
        logger.warning(f"Potential Misclassification: {json.dumps(log_entry, indent=2)}")
    
    def _log_classification_error(self, query: str, error: Exception) -> None:
        """Log classification errors for debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        logger.error(f"Classification Error: {json.dumps(log_entry, indent=2)}")
    
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
        """Classify user intent with enhanced demo user support and logging"""
        try:
            # Input validation
            if not isinstance(state, dict):
                raise ValueError(f"Invalid state type: {type(state)}")
                
            user_query = str(state.get("user_query", "")).lower().strip()
            if not user_query:
                logger.warning("Empty user query")
                state.update({
                    "intent": str(FinancialIntent.UNKNOWN.value),
                    "confidence_score": 0.0,
                    "error_message": "Empty query provided"
                })
                return state
            
            is_demo_user = self._is_demo_user(state)
            
            # Adjust confidence threshold based on user type
            confidence_threshold = 0.5 if is_demo_user else 0.7
            logger.info(f"Processing query '{user_query}' with threshold {confidence_threshold} (Demo user: {is_demo_user})")
            
            # First try rule-based classification with timing
            start_time = datetime.now()
            rule_based_intent, confidence = self._classify_with_rules(user_query)
            classification_method = "rule_based"
            
            # If confidence is low, use LLM classification
            if confidence < confidence_threshold:
                llm_intent, llm_confidence = self._classify_with_llm(user_query)
                if llm_confidence > confidence:
                    rule_based_intent = llm_intent
                    confidence = llm_confidence
                    classification_method = "llm"
                    
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get intent as string for consistency
            intent_str = str(rule_based_intent.value)
            
            # Update state fields individually to maintain typing
            state["intent"] = intent_str
            state["confidence_score"] = confidence
            state["tools_used"] = state.get("tools_used", []) + ["intent_classifier"]
            state["current_node"] = "intent_classifier"
            
            # Update context separately to maintain type safety
            current_context = state.get("context", {})
            current_context.update({
                "classification_method": classification_method,
                "processing_time": processing_time,
                "user_type": "demo" if is_demo_user else "standard",
                "threshold_used": confidence_threshold,
                "threshold_met": confidence >= confidence_threshold
            })
            state["context"] = current_context
            
            # Log comprehensive classification results
            self._log_classification_result(
                query=user_query,
                intent=intent_str,
                confidence=confidence,
                method=classification_method,
                is_demo=is_demo_user,
                threshold=confidence_threshold
            )
            
            # If confidence is still low, log as potential misclassification
            if confidence < confidence_threshold:
                self._log_potential_misclassification(
                    query=user_query,
                    assigned_intent=intent_str,
                    confidence=confidence,
                    state=state
                )
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            state["intent"] = str(FinancialIntent.UNKNOWN.value)
            state["confidence_score"] = 0.0
            state["error_message"] = str(e)
            
            # Log classification failure
            self._log_classification_error(user_query, e)
        
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
        best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
        confidence = min(float(intent_scores[best_intent]), 1.0)
        
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
            try:
                result = json.loads(response.content if isinstance(response.content, str) else str(response.content))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                return FinancialIntent.UNKNOWN, 0.0
                
            # Validate response structure
            if not isinstance(result, dict):
                logger.error(f"Invalid response format: {result}")
                return FinancialIntent.UNKNOWN, 0.0
                
            intent_name = str(result.get("intent", "UNKNOWN")).upper()
            try:
                confidence = float(result.get("confidence", 0.0))
                if not 0.0 <= confidence <= 1.0:
                    logger.warning(f"Invalid confidence value: {confidence}")
                    confidence = 0.0
            except (TypeError, ValueError) as e:
                logger.error(f"Invalid confidence value: {e}")
                confidence = 0.0
            
            # Convert string to enum with validation
            try:
                intent = FinancialIntent[intent_name]
                return intent, confidence
            except KeyError:
                logger.warning(f"Unknown intent type: {intent_name}")
                return FinancialIntent.UNKNOWN, 0.0
            
        except Exception as e:
            logger.error(f"LLM classification error: {e}")
            return FinancialIntent.UNKNOWN, 0.0