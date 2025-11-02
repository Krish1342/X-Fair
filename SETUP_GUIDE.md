# Dynamic Personal Finance Agent - Setup Instructions

## Overview

This is a complete restructure of your Dynamic Personal Finance Agent with:

### Backend (LangGraph + Groq API)

- **Multi-stage workflow** implementation matching your diagram
- **Groq API integration** for LLM-powered reasoning
- **Stage-based routing**: Started → MVP → Intermediate → Advanced
- **Comprehensive financial tools** for each stage
- **RESTful API** with FastAPI

### Frontend (React + Modern Architecture)

- **Clean component structure** with proper separation of concerns
- **State management** using React Context
- **Service layer** for API communication
- **Utility functions** for common operations
- **Responsive design** with Tailwind CSS

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp sample.env .env

# Edit .env with your API keys:
# GROQ_API_KEY=your_groq_api_key_here
# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
# FINNHUB_API_KEY=your_finnhub_key

# Run the server
python main.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Architecture Overview

### Backend Workflow Stages

#### Stage 1: Started

- **Onboarding**: User registration and consent
- **Goal**: Get user started with basic profile

#### Stage 2: MVP

- **Statement Parser**: Parse CSV/PDF financial data
- **Budget Analyzer**: Categorize and analyze spending
- **Goal Planner**: Simple interest calculations and goal tracking

#### Stage 3: Intermediate

- **RAG Knowledge Retriever**: Tax docs and FAQs
- **Reasoning Engine**: Structured financial plans

#### Stage 4: Advanced

- **Task Decomposer**: Multi-step financial strategies
- **ML Models**: Expense forecasting, portfolio optimization
- **Action Executor**: Automated financial actions (with consent)

### Frontend Structure

```
src/
├── components/          # Reusable UI components
│   ├── layout/         # Layout components (Header, Footer, etc.)
│   ├── ui/             # Basic UI components (Button, Input, etc.)
│   └── features/       # Feature-specific components
├── pages/              # Page components
├── services/           # API services
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── store/              # Global state management
└── assets/             # Static assets
```

## Key Features

### 1. Intelligent Routing

- **Intent Classification**: Rule-based + LLM classification
- **Stage-based Features**: Features unlock as user progresses
- **Context Awareness**: Maintains conversation and analysis state

### 2. Financial Tools

- **Budget Analysis**: Spending patterns, alerts, recommendations
- **Goal Planning**: Savings targets, progress tracking
- **Investment Analysis**: Portfolio optimization, risk assessment
- **Tax Optimization**: Deduction strategies, regulatory guidance
- **Market Intelligence**: Real-time data and forecasts

### 3. Modern UI/UX

- **Responsive Design**: Works on all devices
- **Interactive Charts**: Recharts for data visualization
- **Real-time Chat**: AI-powered financial assistant
- **Progressive Enhancement**: Features unlock based on user journey

## API Endpoints

### Core Endpoints

- `POST /api/v1/chat` - Main chat interface
- `POST /api/v1/onboarding` - Complete user onboarding
- `GET /api/v1/workflow/status/{user_id}` - Get workflow status
- `GET /api/v1/tools` - Available financial tools
- `GET /api/v1/examples` - Example queries by stage

### Authentication

- `POST /api/v1/login` - User login
- `POST /api/v1/register` - User registration
- `GET /api/v1/profile/{user_id}` - User profile

## Configuration

### Environment Variables

#### Backend (.env)

```env
# API Keys
GROQ_API_KEY=your_groq_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# Application
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
API_HOST=localhost
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./finance_agent.db

# Logging
LOG_LEVEL=INFO
```

#### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Development

### Backend Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host localhost --port 8000

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

### Frontend Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

## Testing

### Example Queries by Stage

#### Onboarding

- "Hello, I'm new to personal finance"
- "Help me get started with budgeting"

#### MVP Stage

- "Analyze my spending patterns"
- "Help me create a budget for $5000 monthly income"
- "I want to save $10,000 for a vacation"

#### Intermediate Stage

- "What tax deductions can I claim?"
- "Explain current market conditions"
- "Create a comprehensive financial plan"

#### Advanced Stage

- "Create a step-by-step retirement plan"
- "Predict my expenses for next year"
- "Optimize my investment portfolio"

## Deployment

### Backend Deployment

1. Set production environment variables
2. Use PostgreSQL for production database
3. Deploy with Gunicorn + Nginx
4. Configure CORS for production domain

### Frontend Deployment

1. Build production bundle: `npm run build`
2. Deploy to static hosting (Vercel, Netlify, etc.)
3. Update API base URL for production

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **API Key Errors**: Check .env file and Groq API key validity
3. **CORS Issues**: Verify frontend URL in backend CORS settings
4. **Port Conflicts**: Change ports in configuration if needed

### Logs

- Backend logs: Check console output or configure logging
- Frontend logs: Check browser console for errors

## Next Steps

1. **Add Real Authentication**: Implement JWT tokens and user sessions
2. **Database Integration**: Add PostgreSQL and user data persistence
3. **File Upload**: Implement CSV/PDF statement parsing
4. **Real API Integrations**: Connect to actual financial data providers
5. **Automated Actions**: Implement broker/bank API integrations
6. **Advanced ML**: Add trained models for better predictions
7. **Notifications**: Add email/SMS alert system
8. **Mobile App**: React Native or Flutter mobile version

## Support

For issues or questions:

1. Check the console logs for error messages
2. Verify API keys and environment variables
3. Ensure all dependencies are installed correctly
4. Test individual API endpoints using the /docs interface
