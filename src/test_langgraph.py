#!/usr/bin/env python3
"""
Test script for the LangGraph implementation
"""
import os
from state import LangGraphState
from langgraph_flow import LangGraphFlow

def test_basic_flow():
    """Test the basic flow with a simple hint request"""
    
    # Initialize state
    initial_state = {
        "chat_history": [],
        "hint_level": 1,
        "last_question_id": "",
        "user_input": "",
        "current_hint": "",
        "formatted_output": ""
    }
    
    # Create flow
    flow = LangGraphFlow(initial_state)
    
    # Test with a hint request
    test_input = "I need a hint to find the bus token"
    print(f"Testing with input: '{test_input}'")
    
    try:
        result = flow.run(test_input)
        print(f"✅ Success! Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_non_hint_request():
    """Test with a non-hint request"""
    
    # Initialize state
    initial_state = {
        "chat_history": [],
        "hint_level": 1,
        "last_question_id": "",
        "user_input": "",
        "current_hint": "",
        "formatted_output": ""
    }
    
    # Create flow
    flow = LangGraphFlow(initial_state)
    
    # Test with a non-hint request
    test_input = "What's the weather like?"
    print(f"Testing with input: '{test_input}'")
    
    try:
        result = flow.run(test_input)
        print(f"✅ Success! Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LangGraph Flow...")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Run tests
    test1 = test_basic_flow()
    print()
    test2 = test_non_hint_request()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")
