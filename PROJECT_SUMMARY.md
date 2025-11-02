# 🚀 Personal Finance Agent - LangGraph Implementation

## Project Overview

This is a comprehensive **LangGraph-based Personal Finance Agent** that demonstrates advanced Agentic AI capabilities with tool use and workflow orchestration. The system combines React frontend with FastAPI backend to provide intelligent financial analysis and insights.

## 🏗️ Architecture

### Core Components

**LangGraph Workflow Engine**

- StateGraph-based workflow orchestration
- Multi-node processing pipeline
- Intent classification and routing
- Context-aware response synthesis

**Financial Analysis Tools**

- TransactionAnalyzer: Expense tracking and categorization
- BudgetManager: Budget analysis and monitoring
- InvestmentAnalyzer: Portfolio performance tracking
- GoalTracker: Financial goal progress monitoring
- FinancialInsights: AI-powered recommendations

**Full-Stack Integration**

- React.js frontend with real-time chat interface
- FastAPI backend with comprehensive API endpoints
- Real-time data processing and analysis
- Session management and conversation tracking

## 🎯 Key Features

### Intelligent Intent Classification

The agent automatically classifies user queries into financial categories:

- Expense Tracking
- Budget Analysis
- Investment Monitoring
- Goal Tracking
- General Financial Inquiry

### Comprehensive Financial Tools

- **Transaction Analysis**: Categorized spending insights
- **Budget Management**: Real-time budget tracking and alerts
- **Investment Portfolio**: Performance monitoring and recommendations
- **Goal Tracking**: Progress tracking toward financial objectives
- **Financial Insights**: AI-powered recommendations and advice

### Real-Time Chat Interface

- Context-aware conversations
- Tool usage transparency
- Session persistence
- Rich financial data visualization

## 📊 Data Layer

### Mock Financial Data

- **Transactions**: 51+ realistic transactions across categories
- **Investments**: 5 diverse investment holdings with real-time metrics
- **Goals**: 5 financial goals with progress tracking
- **Budget**: Monthly budget allocations and spending tracking

### Data Files

```
backend/data/
├── transactions.csv    # Transaction history with categories
├── investments.json    # Investment portfolio data
├── goals.json         # Financial goals and progress
└── budget.json        # Budget allocations and tracking
```

## 🔧 Technical Stack

### Backend (Python)

- **LangGraph 0.6.7**: Workflow orchestration
- **LangChain 0.3.27**: LLM integration
- **FastAPI**: REST API framework
- **Pandas**: Data analysis
- **Pydantic**: Data validation

### Frontend (JavaScript)

- **React.js**: Component-based UI
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling framework
- **Modern ES6+**: Latest JavaScript features

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key (optional for full LLM features)

### Quick Start

1. **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
python simple_server.py
```

2. **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

3. **Access Application**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 📋 API Endpoints

### Core Endpoints

- `POST /api/v1/chat` - Main chat interface with LangGraph agent
- `GET /api/v1/workflow` - Workflow information and status
- `GET /api/v1/examples` - Example queries for testing

### Data Endpoints

- `GET /api/v1/data/transactions` - Transaction data
- `GET /api/v1/data/investments` - Investment portfolio
- `GET /api/v1/data/goals` - Financial goals
- `GET /api/v1/data/budget` - Budget information

### User-scoped CRUD (Demo/In-memory)

These endpoints store data per user in memory for demo purposes. Replace with a database in production.

- Transactions

  - `GET /api/v1/transactions/{user_id}` — list
  - `POST /api/v1/transactions/{user_id}` — create
  - `GET /api/v1/transactions/{user_id}/{id}` — retrieve
  - `PUT /api/v1/transactions/{user_id}/{id}` — update
  - `DELETE /api/v1/transactions/{user_id}/{id}` — delete

- Goals

  - `GET /api/v1/goals/{user_id}` — list
  - `POST /api/v1/goals/{user_id}` — create
  - `GET /api/v1/goals/{user_id}/{id}` — retrieve
  - `PUT /api/v1/goals/{user_id}/{id}` — update
  - `DELETE /api/v1/goals/{user_id}/{id}` — delete

- Budgets

  - `GET /api/v1/budgets/{user_id}` — list
  - `POST /api/v1/budgets/{user_id}` — create
  - `GET /api/v1/budgets/{user_id}/{id}` — retrieve
  - `PUT /api/v1/budgets/{user_id}/{id}` — update
  - `DELETE /api/v1/budgets/{user_id}/{id}` — delete

- Recurring Transactions
  - `GET /api/v1/recurring/{user_id}` — list
  - `POST /api/v1/recurring/{user_id}` — create
  - `GET /api/v1/recurring/{user_id}/{id}` — retrieve
  - `PUT /api/v1/recurring/{user_id}/{id}` — update
  - `DELETE /api/v1/recurring/{user_id}/{id}` — delete
  - `GET /api/v1/recurring/{user_id}/preview?periods=N` — preview next N dates
  - `POST /api/v1/recurring/{user_id}/generate?up_to=YYYY-MM-DD` — materialize due transactions

### Analytics Endpoints

- `GET /api/v1/analytics/summary` - Financial overview

## 🧪 Testing

### Automated Tests

```bash
# Test data layer
python data_test.py

# Test individual tools (requires OpenAI API key)
python test_agent.py
```

### Sample Queries

- "What did I spend on dining this month?"
- "How is my budget looking?"
- "Show me my investment portfolio performance"
- "How close am I to my savings goals?"
- "Give me a financial overview"

## 🎨 User Interface

### Dashboard Features

- **Financial Overview**: Key metrics and KPIs
- **Expense Categories**: Detailed spending breakdown
- **Investment Portfolio**: Real-time performance tracking
- **Goal Progress**: Visual progress indicators
- **Budget Status**: Category-wise budget utilization

### Chat Interface

- **Real-time Conversations**: Interactive financial assistant
- **Intent Recognition**: Automatic query classification
- **Tool Transparency**: Shows which tools are used
- **Session Management**: Persistent conversation context

## 🔐 Security & Privacy

- Environment-based configuration
- CORS protection for API endpoints
- Input validation and sanitization
- Session isolation

## 🚀 Deployment Ready

### Configuration

- Environment-based settings
- Configurable API endpoints
- CORS configuration for production
- Health check endpoints

### Scalability

- Modular tool architecture
- Extensible workflow design
- Database-ready structure
- Cloud deployment compatible

## 📈 Future Enhancements

### Planned Features

- User authentication and authorization
- Real-time financial data integration
- Advanced ML-based predictions
- Multi-user support
- Mobile responsive design

### Technical Improvements

- Redis session storage
- PostgreSQL database integration
- Docker containerization
- CI/CD pipeline
- Comprehensive test suite

## 🎯 LangGraph Demonstration

This project specifically demonstrates:

1. **Workflow Orchestration**: Complex multi-step financial analysis workflows
2. **Tool Integration**: Multiple specialized financial analysis tools
3. **State Management**: Persistent conversation state across interactions
4. **Conditional Routing**: Intent-based workflow navigation
5. **Real-world Application**: Practical financial use case implementation

## 🏆 Success Metrics

### Functional Achievements

✅ Complete LangGraph workflow implementation  
✅ 5 specialized financial analysis tools  
✅ Real-time chat interface with backend integration  
✅ Comprehensive mock financial data  
✅ Full-stack application with modern architecture  
✅ Production-ready API design  
✅ Responsive user interface  
✅ Session management and state persistence

### Technical Excellence

- Clean, maintainable code architecture
- Comprehensive error handling
- Real-time data processing
- Scalable design patterns
- Modern development practices

## 📞 Support

For questions or issues:

- Check the API documentation at `/docs`
- Review the example queries at `/api/v1/examples`
- Test individual components using provided test scripts

---

**Built with ❤️ using LangGraph, React, and FastAPI**

_This Personal Finance Agent demonstrates the power of Agentic AI in practical financial applications, showcasing advanced workflow orchestration and tool integration capabilities._
