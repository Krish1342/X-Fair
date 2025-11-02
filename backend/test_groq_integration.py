"""
Test script for the simplified Groq-based workflow
Verifies that the system works without HuggingFace dependency conflicts
"""
import asyncio
import os
from dotenv import load_dotenv
import sys
import json

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup...")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✅ GROQ_API_KEY found (length: {len(groq_key)})")
    else:
        print("❌ GROQ_API_KEY not found in environment variables")
        return False
    
    return True

def test_imports():
    """Test that all imports work without conflicts"""
    print("\n🔍 Testing Imports...")
    
    try:
        from core.groq_client import groq_client
        print("✅ Groq client imported successfully")
        
        from core.langgraph_workflow import finance_workflow, FinanceState
        print("✅ LangGraph workflow imported successfully")
        
        from agents.finance_agent import FinanceAgent
        print("✅ Finance agent imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

async def test_groq_client():
    """Test direct Groq API communication"""
    print("\n🔍 Testing Groq Client...")
    
    try:
        from core.groq_client import groq_client
        
        # Test basic chat
        response = await groq_client.chat("Hello, this is a test message")
        print(f"✅ Groq chat response: {response[:100]}...")
        
        # Test financial query
        financial_response = await groq_client.analyze_financial_query(
            "I want to create a budget for my monthly expenses"
        )
        print(f"✅ Financial analysis: {financial_response['intent']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq client error: {e}")
        return False

async def test_workflow():
    """Test the LangGraph workflow"""
    print("\n🔍 Testing LangGraph Workflow...")
    
    try:
        from core.langgraph_workflow import finance_workflow, FinanceState
        
        # Create test state for LangGraph
        state = FinanceState(
            user_id="test_user",
            user_query="I want help with budgeting",
            current_stage="started",
            system_stage="started",
            intent="",
            context={},
            response="",
            analysis_results={},
            next_action="",
            tools_used=[],
            messages=[],
            consent_given=False,
            profile_complete=False,
            execute_action=False
        )
        
        # Run workflow
        result = await finance_workflow.run_async(state)
        
        print(f"✅ LangGraph workflow executed successfully")
        print(f"   Intent: {result['intent']}")
        print(f"   Stage: {result['current_stage']}")
        print(f"   Tools Used: {result['tools_used']}")
        print(f"   Response: {result['response'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph workflow error: {e}")
        return False

async def test_finance_agent():
    """Test the finance agent"""
    print("\n🔍 Testing Finance Agent...")
    
    try:
        from agents.finance_agent import FinanceAgent
        
        agent = FinanceAgent()
        
        response = await agent.process_query(
            user_id="test_user",
            query="Help me create a budget",
            workflow_stage="Started"
        )
        
        print(f"✅ Finance agent response:")
        print(f"   Intent: {response.get('intent', 'N/A')}")
        print(f"   Stage: {response.get('workflow_stage', 'N/A')}")
        print(f"   Response: {response.get('response', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Finance agent error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Dynamic Personal Finance Agent - Groq Integration Test")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Groq Client", test_groq_client),
        ("LangGraph Workflow", test_workflow),
        ("Finance Agent", test_finance_agent),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The LangGraph Groq integration is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start the backend server: python main.py")
        print("   2. Start the frontend: cd ../frontend && npm run dev")
        print("   3. Test the full application at http://localhost:5173")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())