# Dynamic Personal Finance Agent

A comprehensive AI-powered personal finance management system built with LangGraph workflow orchestration, Groq API integration, and modern React frontend.

## 🚀 System Overview

This application implements a sophisticated financial assistant that guides users through a progressive workflow from basic expense tracking to advanced investment planning. The system uses LangGraph for intelligent workflow orchestration and Groq API for AI-powered financial insights.

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  LangGraph Core │
│                 │◄──►│                 │◄──►│                 │
│  • Modern UI    │    │  • REST API     │    │  • Workflow     │
│  • Real-time    │    │  • Authentication│    │  • State Mgmt   │
│  • Responsive   │    │  • Data Layer   │    │  • AI Integration│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Workflow Stages

1. **Started** - Initial onboarding and profile setup
2. **MVP** - Basic expense tracking and categorization
3. **Intermediate** - Smart budgeting with AI recommendations
4. **Advanced** - Investment planning and portfolio management

## 🛠 Technology Stack

### Backend

- **Framework**: FastAPI
- **Workflow Engine**: LangGraph v0.2.0+
- **AI Integration**: Groq API
- **Database**: SQLAlchemy with PostgreSQL
- **Authentication**: JWT with passlib/bcrypt
- **Caching**: Redis
- **Analytics**: Pandas, NumPy, Scikit-learn

### Frontend

- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **State Management**: React Context + useReducer
- **HTTP Client**: Axios
- **Charts**: Recharts/Chart.js

## 📁 Project Structure

```
Dynamic-Personal-Finance-Agent/
├── backend/
│   ├── core/
│   │   ├── workflow.py          # Main LangGraph workflow
│   │   ├── state.py            # Workflow state management
│   │   └── llm.py              # Groq LLM integration
│   ├── nodes/
│   │   ├── onboarding.py       # User onboarding flow
│   │   ├── intent_classifier.py # Intent classification
│   │   ├── statement_parser.py  # Financial statement parsing
│   │   ├── budget_analyzer.py   # Budget analysis
│   │   ├── goal_planner.py     # Goal planning
│   │   ├── rag_knowledge.py    # RAG knowledge base
│   │   ├── reasoning_engine.py # AI reasoning
│   │   ├── task_decomposer.py  # Task decomposition
│   │   ├── ml_models.py        # ML model integration
│   │   └── action_executor.py  # Action execution
│   ├── api/
│   │   ├── auth_router.py      # Authentication endpoints
│   │   └── finance_router.py   # Finance endpoints
│   ├── tools/                  # Financial analysis tools
│   ├── agents/                 # Agent implementations
│   ├── config/
│   │   └── settings.py         # Configuration
│   └── main.py                 # FastAPI application
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/             # Reusable UI components
│   │   │   ├── layout/         # Layout components
│   │   │   └── features/       # Feature-specific components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── hooks/              # Custom React hooks
│   │   ├── utils/              # Utility functions
│   │   ├── store/              # State management
│   │   └── App.jsx             # Main app component
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (optional, can use SQLite for development)
- Redis (optional, for caching)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp sample.env .env

# Edit .env file with your configuration
# Required: GROQ_API_KEY, DATABASE_URL, SECRET_KEY
```

### 2. Environment Configuration

Create `.env` file in the backend directory:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Database
DATABASE_URL=sqlite:///./finance_app.db
# Or for PostgreSQL: postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start the Application

#### Backend (Terminal 1)

```bash
cd backend
python main.py
```

#### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The application will be available at:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🎯 Key Features

### 1. Progressive Workflow System

- **Adaptive Learning**: System adapts to user's financial sophistication
- **Stage-based Progression**: Natural advancement through complexity levels
- **Intelligent Routing**: LangGraph orchestrates optimal user experience

### 2. AI-Powered Insights

- **Groq Integration**: Fast, accurate AI responses for financial queries
- **Context-Aware**: Maintains conversation context and user preferences
- **Personalized Recommendations**: Tailored advice based on user profile

### 3. Comprehensive Financial Tools

- **Budget Management**: Smart categorization and spending analysis
- **Goal Tracking**: Progress monitoring with milestone celebrations
- **Investment Analysis**: Portfolio optimization and risk assessment
- **Market Intelligence**: Real-time market data and trend analysis

### 4. Modern User Experience

- **Responsive Design**: Works seamlessly across all devices
- **Real-time Updates**: Live data synchronization
- **Interactive Chat**: Conversational interface for natural interaction
- **Progressive Enhancement**: Features unlock as users advance

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **API Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive data validation
- **CORS Configuration**: Proper cross-origin request handling

## 📊 API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/verify` - Token verification

### Finance

- `GET /finance/dashboard` - Dashboard data
- `POST /finance/chat` - Chat with AI assistant
- `POST /finance/onboarding` - Complete onboarding
- `GET /finance/transactions` - Transaction history
- `POST /finance/goals` - Create financial goals
- `GET /finance/budget` - Budget information

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Start both backend and frontend
npm run test:e2e
```

## 🚀 Deployment

### Backend Deployment

1. Set production environment variables
2. Configure production database
3. Use production WSGI server (gunicorn)

```bash
gunicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

1. Build production bundle
2. Configure environment variables
3. Deploy to CDN or static hosting

```bash
npm run build
```

## � Troubleshooting

### Common Issues

**Backend won't start:**

- Verify Python dependencies are installed
- Check environment variables in `.env`
- Ensure database is accessible

**Frontend build errors:**

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify all path aliases are correctly configured

**Database connection errors:**

- Verify DATABASE_URL in `.env`
- Ensure database server is running
- Check firewall and network settings

**API authentication errors:**

- Verify SECRET_KEY is set
- Check token expiration settings
- Ensure proper CORS configuration

## 📞 Contact

For questions or support, please contact the development team or open an issue on GitHub.

**Happy Financial Management! 💰📈**
