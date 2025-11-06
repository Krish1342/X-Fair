# Product Requirements Document (PRD)

# Dynamic Personal Finance Agent ("X-Fair")

Version: 1.0
Date: 2025-11-06
Status: In Active Development
Document Owner: Product / Engineering Collaboration

---

## 1. Executive Summary

X-Fair is a multi-stage, agentic AI Personal Finance platform combining a React frontend and FastAPI backend with a LangGraph-orchestrated workflow and Groq LLM integration. It progressively guides a user from onboarding and basic budgeting (Started/MVP) to intermediate tax & reasoning capabilities, and finally to advanced multi-step planning, ML forecasting, and optional automated execution with proper consent and audit trails. The product delivers contextual, trustworthy, actionable financial insights while architecting an extensible foundation for future broker/bank automation and continuous learning loops.

---

## 2. Vision & Mission

Vision: Enable every individual to make intelligent, confident, and automated financial decisions through transparent, adaptive AI orchestration.
Mission: Provide an end-to-end AI-driven finance assistant that evolves with user sophistication, unlocking deeper analytical and execution capabilities as trust, data richness, and maturity grow.

---

## 3. Problem Statement

Consumers lack integrated tooling that: (1) understands their stage of financial maturity; (2) consolidates budgets, goals, transactions, and investment context; (3) transforms raw statements into structured insights; (4) recommends and eventually executes optimized financial actions safely. Existing solutions are fragmented, reactive, and do not adapt to user maturity or provide multi-step reasoning & automation under explicit consent.

---

## 4. Product Goals

1. Progressive Enablement: Seamless stage progression (Started → MVP → Intermediate → Advanced) tied to data completeness & consent.
2. Trustworthy Insights: High-quality, explainable AI reasoning with audit trails of tools used and intermediate analyses.
3. Actionability: Provide concrete recommendations, next steps, and (in advanced stage) safe, consent-based execution.
4. Extensibility: Modular node & tool architecture for easy addition of new financial domains (e.g., insurance, tax optimization, ESG scoring).
5. Data Unification: Consolidate transactions, goals, budget, and later portfolio & market signals for holistic planning.
6. Continuous Improvement: Feedback & learning loop to refine recommendations and ML models over time.

---

## 5. Non-Goals (Current Release)

- Real money movement / live brokerage trade execution (placeholder for future APIs).
- Advanced regulatory compliance certification (e.g., SOC2) in v1.
- Full tax filing / official statements generation.
- Native mobile application delivery (web responsive only for v1).
- Personalized real-time market streaming (batch / periodic only initially).

---

## 6. Target Users & Personas

1. New Budgeter (Stage: Started/MVP): Wants basic expense categorization & goal setup.
2. Growing Planner (Stage: Intermediate): Seeks tax tips, trend reasoning, broader context.
3. Advanced Optimizer (Stage: Advanced): Requires multi-step plan decomposition, forecasting, scenario comparisons, potential automated execution.
4. Casual Inquirer: Ad-hoc queries (“How am I doing?”) needing summary health reports.

Each persona maps to system stage gating for feature access.

---

## 7. User Journey (High-Level)

1. Landing → Registration / Consent → Minimal Profile → Stage Determination.
2. Upload / Parse Statement (CSV/PDF) → Categorize Transactions → Budget & Goals → Basic Insights.
3. Additional Data Intake (Historical, Tax Docs, Market Queries) → RAG Knowledge + Reasoning Engine.
4. Advanced Tools Unlock (Task Decomposer, ML Models, Portfolio Optimization) → Action Executor (+2FA & audit) → Feedback Loop → Continuous Learning.

---

## 8. Scope (Functional)

In-Scope for v1:

- Stage-based workflow orchestration (LangGraph `workflow.py`).
- LLM-based intent classification with rule fallback (`intent_classifier_node.py`).
- Transaction parsing & categorical analytics (TransactionAnalyzerTool).
- Budget management & performance scoring (BudgetManagerTool).
- Goal planning & simple projections.
- RAG knowledge retrieval for tax/FAQ docs.
- Reasoning engine for structured multi-step narrative answers.
- Task decomposition for advanced planning strategies.
- ML Models placeholder (forecasting & portfolio optimization scaffolding).
- Action Executor stub (simulated audit trail & consent gating).
- REST API endpoints for chat, data CRUD (transactions, goals, budgets, recurring), workflow status.
- React frontend pages: Dashboard, Workflow visualization, AI chat, Transactions, Onboarding.

Out-of-Scope (v1): Real brokerage integration, external identity verification, encryption at field-level beyond transport, advanced personalization model training.

---

## 9. Detailed Workflow Stages

Stage 0 (Started): Onboarding node collects consent, minimal profile. Routes to Stage 1 when consent + basic profile captured.
Stage 1 (MVP): Statement parser → Budget analyzer → Goal planner → Generate response. Primary intents: budgeting, goals, basic insights.
Stage 2 (Intermediate): RAG Knowledge retriever feeds Reasoning Engine for tax docs, FAQs, market conceptual queries.
Stage 3 (Advanced): Task decomposer → Reasoning engine (advanced) → ML models → (conditional) Action executor → Response.

Routing: `determine_stage` sets `system_stage`. `intent_classifier` chooses next node based on (intent, confidence, stage). Action executor only if advanced + consent.

---

## 10. Core Nodes & Responsibilities

- determine_stage: Stage inference from profile & data richness.
- onboarding_node: Consent/profile capture.
- intent_classifier_node: Hybrid keyword + LLM classification returning `intent` + `confidence_score`.
- statement_parser_node: Normalizes CSV/PDF (future) into structured DataFrame.
- budget_analyzer_node: Category spending, overspending analysis, performance scoring.
- goal_planner_node: Goal progress, milestone projections (simple interest currently).
- rag_knowledge_node: Retrieval augmented responses for tax/FAQ content.
- reasoning_engine_node: Synthesis of multi-source analysis into actionable narrative.
- task_decomposer_node: Breaks complex tasks (e.g., retirement planning) into ordered steps.
- ml_models_node: Forecasting & portfolio optimization (placeholder; future advanced ML).
- action_executor_node: Simulate actionable operations (trade/transfer) with audit & 2FA checks.

---

## 11. State Model

File: `backend/core/state.py` defining `FinanceAgentState` (TypedDict) fields:

- user_profile (UserProfile dataclass: consent, stage, goals, risk tolerance)
- system_stage (Enum: STARTED/MVP/INTERMEDIATE/ADVANCED)
- messages (List[BaseMessage])
- user_query (str)
- intent (FinancialIntent Enum)
- confidence_score (float)
- context / financial_data (Dict)
- current_node (str)
- tools_used (List[str])
- analysis_results (Dict[str, Any])
- response (str)
- suggestions (List[str])
- visualizations (List[Dict])
- should_continue (bool), error_message, retry_count

---

## 12. Tooling Layer

Implemented in `backend/tools/`:

- TransactionAnalyzerTool: Keyword-driven selection of specialized analysis (food, monthly, category breakdown, totals, recent 30-day patterns).
- BudgetManagerTool: Overspending detection, remaining budget, performance classification, scoring, recommendations.
  Future Tools: InvestmentAnalyzer, RiskAssessment, MarketIntelligence (described in `AGENTIC_AI_FEATURES.md`).

All tools enrich `analysis_results` and append to `tools_used` list for transparency.

---

## 13. Intent Classification Logic

Priority: Rule-based keyword scoring → fallback to Groq LLM JSON classification if confidence < 0.7. Confidence informs routing; low confidence (<0.6) triggers direct response generation to minimize misrouting.

---

## 14. LLM Integration

Groq Client via `ChatGroq` (mixtral-8x7b-32768) low temperature (0.1) for deterministic, concise outputs. Response generation prompt enforces structured, actionable advice referencing tools used and analysis results.

---

## 15. Data Layer & Models

SQLAlchemy models: `User`, `Transaction`, `Goal`, `Budget`, `RecurringTransaction` with indexes and unique constraints for query optimization (e.g., `idx_transactions_user_date`, `uq_budgets_user_month_category`). Data seeding via `db/seed.py`. Pydantic schemas in `api/schemas.py` for request validation.

Non-persistent demo in-memory or SQLite for development; scalable to PostgreSQL (future). Recurring transactions materialization endpoint planned for generating future transaction instances.

---

## 16. API Surface (v1)

Base Prefix: `/api/v1`

- Chat: `POST /chat` → orchestrated workflow invocation.
- Workflow: `GET /workflow/status/{user_id}` (present)/`GET /workflow` (summary).
- Auth (legacy): `POST /auth/login`, `POST /auth/register`, `GET /auth/verify`.
- Transactions: CRUD endpoints, recurring preview and generation.
- Goals: CRUD.
- Budgets: CRUD.
- Recurring: CRUD + preview/generate.
- System health: `/health`, root `/` metadata.

Response Example (Chat): `{ response, intent, stage, tools_used, analysis_results, suggestions, visualizations, error }`.

---

## 17. Frontend Architecture

React (Vite) with Context-based global state (`store/AppContext.jsx`), modular pages (`pages/`), feature components (`components/features`), UI primitives (`components/ui`). Routing in `App.jsx` using `react-router-dom` with protected route gating based on authenticated user in context. Authentication token persistence in `localStorage` and verification on mount. Dashboard, AI Chat, Workflow visualization, Transactions & Onboarding screens.

---

## 18. UX Principles

- Progressive Disclosure: Show advanced features only after criteria.
- Transparency: Display tools used in a response.
- Action Focus: Provide next-step recommendations & potential automated action preview (before execution).
- Feedback Loop: Users can accept/reject suggestions (future instrumentation) feeding continuous learning.

---

## 19. Security & Privacy

Current Measures:

- JWT-based (planned/legacy) auth endpoints.
- CORS controlled origins (settings.cors_origins).
- Password hashing (passlib/bcrypt) placeholder.
- No PII beyond minimal profile; consent flag tracked.
  Planned Enhancements:
- Role-based scopes, rate limiting, audit log persistence beyond transient.
- Field-level encryption for sensitive financial data in DB.
- Multi-factor challenge for any execution node (ActionExecutor).

---

## 20. Compliance & Legal (Future Planning)

- Consent tracking for execution actions.
- Logging for potential financial advisory disclaimers.
- Separation between informational suggestions vs. fiduciary advice (explicit disclaimers appended).

---

## 21. Performance Targets

- P95 chat response latency < 3.5s (MVP stage) and < 5s (Advanced with multi-node execution) under dev environment.
- Node execution parallelization for independent analyses (future optimization).
- DB queries: indexed lookups return < 100ms for typical user dataset (<10k transactions).

---

## 22. Reliability & Observability

Logging: Python `logging` + planned structured log output (loguru already in requirements). Health endpoint for service status & Groq API key presence. Future: metrics (Prometheus), tracing (OpenTelemetry), alerting.

---

## 23. ML & Advanced Analytics Roadmap

Phase 1: Rule + LLM + heuristic scoring.
Phase 2: Add forecasting models (Prophet/LSTM) for cash flow & expense predictions.
Phase 3: Portfolio optimization (risk-adjusted returns, diversification metrics, rebalance suggestions).
Phase 4: Reinforcement learning for personalized recommendation ranking (feedback loop).

Model Evaluation Metrics:

- Intent classification accuracy (manual validation set, target >85%).
- Recommendation acceptance rate.
- Budget overspending reduction after advice (delta month-over-month).
- Forecast MAE for expense prediction (<15% after sufficient history).

---

## 24. Risks & Mitigations

| Risk                                    | Impact                              | Mitigation                                                                    |
| --------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------- |
| Misclassified Intent                    | Incorrect routing, user frustration | Confidence threshold fallback to general response; highlight uncertainty      |
| Data Quality (parsed statements)        | Incorrect analysis                  | Validation & anomaly detection (e.g., duplicate transactions, outlier spend)  |
| Overreliance on LLM hallucinations      | Poor advice                         | Constrain prompt, inject structured numeric context, enforce disclaimers      |
| Performance Degradation with More Nodes | Slow UX                             | Lazy execution; stage-based gating; caching repeated computations             |
| Unauthorized Action Execution           | Security breach                     | Consent flag + 2FA + tiered permissions before enabling ActionExecutor        |
| Regulatory non-compliance (future)      | Legal risk                          | Early inclusion of consent/audit structure; modular compliance logging design |

---

## 25. Edge Cases & Error Modes

Edge Cases:

- Empty transaction dataset (return baseline prompts to upload statement).
- Extremely high-volume transactions (>100k) (future batching/pagination strategy).
- Conflicting goals (e.g., aggressive saving vs. high discretionary spend) flagged by reasoning engine.
- Timezone mismatches (standardize to UTC for DB; convert on client).
- Low confidence intent classification (<0.3) – ask clarifying question.
  Error Handling:
- Node exceptions captured; `error_message` populated; graceful fallback response.
- Retry logic (configurable `max_retries` planned via `WorkflowConfig`).

---

## 26. Analytics & Metrics

Core KPIs:

- Stage progression conversion (Started → MVP → Intermediate → Advanced).
- Query volume & tool utilization distribution.
- Average response latency by stage & intent.
- Recommendation acceptance / dismissal rates.
- Budget adherence improvement after usage periods.
- User retention (weekly active users by stage).

---

## 27. Release Plan (Phased)

Phase 1 (Current): MVP stage complete (budget, goals, basic insights), onboarding, chat, CRUD endpoints.
Phase 2: Intermediate (RAG + reasoning) fully stable, add tax FAQ dataset ingestion.
Phase 3: Advanced planning nodes (task decomposition + ML forecasting prototypes) & action executor simulation.
Phase 4: Real external portfolio data & predictive models; feedback loop instrumentation.
Phase 5: Execution integrations (broker APIs) behind feature flags + compliance review.

---

## 28. Dependencies & External Integrations

- Groq LLM (`groq_api_key` required).
- Potential financial data sources (yfinance, alpha-vantage in requirements but not fully integrated yet).
- Future: Broker APIs (Alpaca, Robinhood, Plaid), Notification services (SendGrid, Twilio).

---

## 29. Architectural Principles

- Modular Node Design: Each financial function isolated for testability & replacement.
- Progressive Complexity: Avoid overwhelming early-stage users.
- Observability Hooks: Each tool appends name to `tools_used` list.
- Declarative State Transitions: Centralized in LangGraph `workflow.py` with conditional edges.

---

## 30. Testing Strategy

Unit: Each node & tool logic (categorization, budget ratios).
Integration: Full workflow invocation across stages with synthetic states.
API: Endpoint contract tests using Pydantic schemas.
Performance: Load simulation for chat endpoint with increasing tool chains.
Security: Auth flows, permission gating for advanced actions.
Future: E2E with Cypress for frontend flows.

---

## 31. Glossary

- LangGraph: Workflow orchestration library enabling conditional stateful execution graphs.
- RAG: Retrieval Augmented Generation; uses external corpus to ground LLM outputs.
- Action Executor: Node performing (simulated) financial actions; future real execution.
- Stage: System maturity level dictating available capabilities.
- Intent: Classified user goal driving routing/path selection.

---

## 32. Open Questions

- What minimum data thresholds promote user from MVP → Intermediate? (Define transaction volume + successful goal tracking criteria.)
- Consent granularity: Separate toggles for analysis vs. execution vs. data sharing.
- Market data freshness requirements: Real-time vs. daily snapshot.
- Portfolio risk model selection (mean-variance vs. factor model) for optimization stage.

---

## 33. Roadmap (High-Level Next 12 Months)

Q1: Stabilize intermediate reasoning; add tax & FAQ corpus ingestion UI.
Q2: Launch basic ML forecasting (cash flow) + portfolio allocation suggestion prototype.
Q3: Add user feedback instrumentation & reinforcement ranking of recommendations.
Q4: Pilot execution with sandbox brokerage; start compliance review for production-grade automation.

---

## 34. Acceptance Criteria (Initial Release)

- User can onboard, create goals, budgets, and view categorized transactions.
- Chat returns responses referencing tools used & includes at least one actionable recommendation.
- Intent classifier returns confidence score; low confidence path triggers fallback explanatory answer.
- State transitions through at least first two stages with sample data seeding.
- API documented at `/docs`; successful CRUD operations for transactions, goals, budgets, recurring.

---

## 35. Success Definition

Achieve active usage through complete Stage 1 workflows with >70% of queries receiving at least one user-marked "helpful" recommendation; demonstrate successful Stage 2 reasoning sessions with tax FAQ grounding; maintain P95 latency targets while scaling initial user base.

---

## 36. Appendices

A. Source Files Referenced:

- Workflow: `backend/core/workflow.py`
- State: `backend/core/state.py`
- Intent Classification: `backend/nodes/intent_classifier_node.py`
- Tools: `backend/tools/transaction_analyzer.py`, `backend/tools/budget_manager.py`
- Models: `backend/db/models.py`
- API Routers: `backend/api/routers/*`
- Frontend root: `frontend/src/App.jsx`

B. Diagram Summary (Provided Image): Staged funnel from User Input → System Stage decision → Stage-specific nodes (Onboarding, Parser/Analyzer/Planner, Retriever/Reasoner, Decomposer/ML/Executor) → Dashboard & Notifications → Feedback loop → Autonomous Actions.

C. Future Data Entities: Portfolio holdings, risk scores, health score snapshots, execution audit entries.

---

End of Document.
