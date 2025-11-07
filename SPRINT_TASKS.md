# 2-Hour Sprint Task Assignment

**Sprint Date**: November 7, 2025  
**Duration**: 2 hours  
**Team Size**: 3 developers

---

## 👨‍💻 **Developer 1: Backend API & Data Layer**

### Priority Tasks (2 hours)

#### 1. Fix Dashboard Data Loading Issues (45 min)

- **File**: `backend/api/routers/system_router.py`
- **Objectives**:
  - Add error handling for missing user data in `/dashboard` endpoint
  - Ensure proper handling when no transactions/budgets/goals exist
  - Add default values to prevent frontend crashes
- **Testing**: Test with empty database and demo user

#### 2. Enhance Chat Action Execution (45 min)

- **File**: `backend/api/routers/chat_router.py`
- **Objectives**:
  - Add validation for `run_action()` function parameters
  - Improve error messages for failed action execution
  - Add success confirmation responses
- **Testing**: Test with various chat commands and edge cases

#### 3. Optimize Database Queries (30 min)

- **Files**:
  - `backend/api/routers/goals_router.py`
  - `backend/api/routers/recurring_router.py`
- **Objectives**:
  - Add `.limit()` to prevent loading too many records
  - Ensure all queries use proper indexes from `backend/db/models.py`
- **Testing**: Test query performance with large datasets

---

## 👨‍💻 **Developer 2: Frontend UI & User Experience**

### Priority Tasks (2 hours)

#### 1. Dashboard Loading States & Error Handling (50 min)

- **File**: `frontend/src/components/features/Dashboard.jsx`
- **Objectives**:
  - Add proper loading spinners for all data sections
  - Handle empty states gracefully (no transactions, goals, budgets)
  - Display user-friendly error messages
- **Testing**: Test with slow network, no data, and error responses

#### 2. ChatBot UI Improvements (40 min)

- **File**: `frontend/src/components/features/ChatBot.jsx`
- **Objectives**:
  - Fix HTML rendering for AI responses (currently shows raw HTML)
  - Add copy-to-clipboard for code snippets in responses
  - Improve quick action button styling
- **Testing**: Test with various AI response formats

#### 3. Demo Login Flow Enhancement (30 min)

- **File**: `frontend/src/components/features/LoginModal.jsx`
- **Objectives**:
  - Add loading state during demo login
  - Show success message after demo login
  - Auto-redirect to dashboard after 1 second
- **Testing**: Test demo login flow end-to-end

---

## 👨‍💻 **Developer 3: AI Workflow & Node Integration**

### Priority Tasks (2 hours)

#### 1. Task Decomposer Response Formatting (50 min)

- **File**: `backend/nodes/task_decomposer_node.py`
- **Objectives**:
  - Ensure execution plans are returned in structured JSON format
  - Add human-readable summaries for complex plans
  - Test with queries: "Plan my retirement", "Help me buy a house"
- **Testing**: Test with various complex financial planning queries

#### 2. Reasoning Engine Context Integration (40 min)

- **File**: `backend/nodes/reasoning_engine_node.py`
- **Objectives**:
  - Improve context extraction from user financial data
  - Add fallback responses when analysis_results are empty
  - Ensure recommendations match user's financial health score
- **Testing**: Test with different user financial profiles

#### 3. Intent Classifier Confidence Tuning (30 min)

- **File**: `backend/nodes/intent_classifier_node.py`
- **Objectives**:
  - Lower confidence threshold for demo users (0.5 instead of 0.7)
  - Add logging for misclassified intents
  - Test with example queries from `backend/api/routers/finance_router.py` line 290
- **Testing**: Test classification accuracy with various user queries

---

## 🚨 **Testing Checklist**

Each developer should test:

1. ✅ **Happy path**: Feature works with valid data
2. ✅ **Empty state**: Feature works with no data
3. ✅ **Error state**: Feature handles errors gracefully
4. ✅ **Demo account**: Feature works with demo user (email: `demo@example.com`)

---

## 🔧 **Development Environment Setup**

### Prerequisites

- Python virtual environment activated
- Node modules installed (`npm install` in frontend)
- Database seeded with demo data (`python backend/db/seed.py`)
- Environment variables configured (`.env` from `sample.env`)

### Running the Application

```bash
# Backend (Terminal 1)
cd backend
python main.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

---

## 📝 **Notes & Best Practices**

1. **Code Quality**: Follow existing code patterns and conventions
2. **Error Handling**: Always add try-catch blocks for async operations
3. **Testing**: Test thoroughly before marking task complete
4. **Communication**: Update team immediately if blocked
5. **Git**: Create feature branch for your tasks, commit frequently


**Good luck team! 🚀**
