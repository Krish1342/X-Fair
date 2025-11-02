"""
RAG Knowledge Retriever Node - Tax docs and FAQs retrieval
Stage 2: Intermediate - RAG Knowledge Retriever
"""
import logging
from typing import Dict, Any, List
from core.state import FinanceAgentState

logger = logging.getLogger(__name__)


class RAGKnowledgeNode:
    """Retrieves knowledge from tax documents and FAQs"""
    
    def __init__(self, llm):
        self.llm = llm
        self.knowledge_base = self._initialize_knowledge_base()
    
    def __call__(self, state: FinanceAgentState) -> FinanceAgentState:
        """Retrieve relevant knowledge for user query"""
        try:
            user_query = state.get("user_query", "").lower()
            intent = state.get("intent")
            
            # Retrieve relevant knowledge
            relevant_docs = self._retrieve_documents(user_query, intent)
            
            state["analysis_results"]["knowledge_retrieval"] = {
                "retrieved_documents": relevant_docs,
                "knowledge_used": True,
                "sources": [doc["source"] for doc in relevant_docs]
            }
            
            state["tools_used"] = state.get("tools_used", []) + ["rag_knowledge"]
            state["current_node"] = "rag_knowledge"
            
            logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
            
        except Exception as e:
            logger.error(f"Knowledge retrieval error: {e}")
            state["error_message"] = str(e)
        
        return state
    
    def _initialize_knowledge_base(self) -> Dict[str, List[Dict]]:
        """Initialize the knowledge base with financial documents and FAQs"""
        return {
            "tax_documents": [
                {
                    "title": "2024 Tax Deduction Guide",
                    "content": "Common tax deductions include mortgage interest, charitable donations, state and local taxes (up to $10,000), and business expenses. The standard deduction for 2024 is $14,600 for single filers and $29,200 for married filing jointly.",
                    "source": "IRS Publication 502",
                    "keywords": ["deduction", "tax", "standard", "itemize", "mortgage", "charitable"]
                },
                {
                    "title": "401(k) Contribution Limits",
                    "content": "For 2024, the 401(k) contribution limit is $23,000 for employees under 50, and $30,500 for those 50 and older (with $7,500 catch-up contribution). Employer matches don't count toward these limits.",
                    "source": "IRS Notice 2023-75",
                    "keywords": ["401k", "retirement", "contribution", "limit", "catch-up", "employer match"]
                },
                {
                    "title": "IRA Rules and Limits",
                    "content": "Traditional and Roth IRA contribution limits for 2024 are $7,000 ($8,000 if 50 or older). Roth IRA has income limits: phase-out begins at $138,000 for single filers and $218,000 for married filing jointly.",
                    "source": "IRS Publication 590-A",
                    "keywords": ["ira", "roth", "traditional", "income limit", "contribution", "phase-out"]
                }
            ],
            "investment_faqs": [
                {
                    "title": "Asset Allocation by Age",
                    "content": "A common rule of thumb is to subtract your age from 100 to determine stock allocation percentage. For example, a 30-year-old might have 70% stocks and 30% bonds. However, this should be adjusted based on risk tolerance and goals.",
                    "source": "Investment FAQ",
                    "keywords": ["asset allocation", "age", "stocks", "bonds", "portfolio", "risk tolerance"]
                },
                {
                    "title": "Emergency Fund Guidelines",
                    "content": "Financial experts recommend keeping 3-6 months of living expenses in an easily accessible savings account. This should be separate from investment accounts and cover essential expenses like housing, food, and utilities.",
                    "source": "Financial Planning FAQ",
                    "keywords": ["emergency fund", "savings", "months", "expenses", "accessible", "essential"]
                },
                {
                    "title": "Dollar-Cost Averaging",
                    "content": "Dollar-cost averaging involves investing a fixed amount regularly regardless of market conditions. This strategy can help reduce the impact of market volatility and remove emotion from investment decisions.",
                    "source": "Investment Strategy FAQ",
                    "keywords": ["dollar cost averaging", "regular investing", "volatility", "market", "strategy"]
                }
            ],
            "budgeting_guides": [
                {
                    "title": "50/30/20 Budget Rule",
                    "content": "The 50/30/20 rule suggests allocating 50% of after-tax income to needs (housing, utilities, groceries), 30% to wants (entertainment, dining out), and 20% to savings and debt repayment.",
                    "source": "Budgeting Guide",
                    "keywords": ["50/30/20", "budget", "needs", "wants", "savings", "allocation"]
                },
                {
                    "title": "Zero-Based Budgeting",
                    "content": "Zero-based budgeting means assigning every dollar a purpose before spending it. Income minus expenses should equal zero, ensuring all money is allocated to specific categories including savings.",
                    "source": "Advanced Budgeting Guide",
                    "keywords": ["zero based", "budgeting", "every dollar", "purpose", "allocation", "categories"]
                }
            ]
        }
    
    def _retrieve_documents(self, user_query: str, intent) -> List[Dict]:
        """Retrieve relevant documents based on query and intent"""
        relevant_docs = []
        
        # Search all knowledge base categories
        for category, documents in self.knowledge_base.items():
            for doc in documents:
                relevance_score = self._calculate_relevance(user_query, doc)
                if relevance_score > 0.3:  # Threshold for relevance
                    doc_with_score = doc.copy()
                    doc_with_score["relevance_score"] = relevance_score
                    doc_with_score["category"] = category
                    relevant_docs.append(doc_with_score)
        
        # Sort by relevance score
        relevant_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Return top 3 most relevant documents
        return relevant_docs[:3]
    
    def _calculate_relevance(self, query: str, document: Dict) -> float:
        """Calculate relevance score between query and document"""
        query_words = set(query.lower().split())
        doc_keywords = set(document["keywords"])
        doc_content_words = set(document["content"].lower().split())
        
        # Keyword match score (weighted more heavily)
        keyword_matches = len(query_words.intersection(doc_keywords))
        keyword_score = keyword_matches / len(doc_keywords) if doc_keywords else 0
        
        # Content match score
        content_matches = len(query_words.intersection(doc_content_words))
        content_score = content_matches / len(doc_content_words) if doc_content_words else 0
        
        # Combined relevance score
        relevance = (keyword_score * 0.7) + (content_score * 0.3)
        
        return relevance