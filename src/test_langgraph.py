#!/usr/bin/env python3
"""
Test script for the LangGraph implementation
"""
import os
from app import run_hint_request

def test_basic_flow():
    """Test the basic flow with a simple hint request"""
    
    # Test with a hint request
    test_input = "I need a hint to find the bus token"
    print(f"Testing with input: '{test_input}'")
    
    try:
        result = run_hint_request(test_input)
        print(f"✅ Success! Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_game_related_questions():
    """Test various game-related questions that should get hints"""
    
    game_questions = [
        "How do I find the token?",
        "Where is the bus?", 
        "I'm stuck on this puzzle",
        "Who is Zelda?",
        "How do I save the game?",
        "How do I open the locker?",
        "How do I do empathy telepathy?",
        "How do I start a flashback?"
    ]
    
    print("🎮 Testing game-related questions...")
    success_count = 0
    
    for question in game_questions:
        print(f"\n--- Testing: '{question}' ---")
        try:
            result = run_hint_request(question)
            # Should NOT contain Zelda's off-topic responses
            if any(phrase in result for phrase in ["Listen sweetie", "Sorry hon", "I appreciate the chat"]):
                print(f"❌ Failed: Got off-topic response for game question")
                return False
            else:
                print(f"✅ Success: Routed to hints")
                success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print(f"\n🎯 Game questions success rate: {success_count}/{len(game_questions)}")
    return success_count == len(game_questions)

def test_off_topic_questions():
    """Test off-topic questions that should get polite rejections"""
    
    off_topic_questions = [
        "What's the weather like?",
        "Tell me a joke",
        "How do I play Minecraft?", 
        "What's 2+2?",
        "Hello, how are you?",
        "I'm stuck on this puzzle",  # Too vague - no specific element
        "How do I solve a puzzle?",  # Too vague - which puzzle?
        "Help me with this",         # Too vague
        "What should I do?"          # Too vague
    ]
    
    print("🚫 Testing off-topic questions...")
    success_count = 0
    
    for question in off_topic_questions:
        print(f"\n--- Testing: '{question}' ---")
        try:
            result = run_hint_request(question)
            # Should contain one of Zelda's off-topic responses
            if any(phrase in result for phrase in ["Listen sweetie", "Sorry hon", "I appreciate the chat"]):
                print(f"✅ Success: Got appropriate off-topic response")
                success_count += 1
            else:
                print(f"❌ Failed: Did not get off-topic response")
                print(f"    Got: {result}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print(f"\n🎯 Off-topic questions success rate: {success_count}/{len(off_topic_questions)}")
    return success_count == len(off_topic_questions)

def test_zelda_guardrail():
    """Test that Zelda stays in character for The Space Bar, not Legend of Zelda"""
    
    print("🛡️ Testing Zelda character guardrail...")
    
    # Test the specific question that was problematic
    question = "Who is Zelda?"
    print(f"\n--- Testing: '{question}' ---")
    
    try:
        result = run_hint_request(question)
        
        # Check for forbidden Legend of Zelda content
        forbidden_terms = ["legend of zelda", "hyrule", "princess", "nintendo", "triforce"]
        result_lower = result.lower()
        
        if any(term in result_lower for term in forbidden_terms):
            print(f"❌ Failed: Response contains Legend of Zelda references")
            print(f"    Got: {result}")
            return False
        
        # Check for Space Bar game references (positive indicators)
        space_bar_terms = ["space bar", "pda", "personal digital assistant", "detective", "alias node"]
        if any(term in result_lower for term in space_bar_terms):
            print(f"✅ Success: Response correctly identifies Space Bar Zelda")
            return True
        else:
            print(f"⚠️  Warning: Response doesn't clearly identify Space Bar context")
            print(f"    Got: {result}")
            # Still pass if no forbidden content, but warn
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LangGraph Intent-Based Router...")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Run tests
    print("1️⃣ Testing basic hint flow...")
    test1 = test_basic_flow()
    print()
    
    print("2️⃣ Testing game-related questions...")
    test2 = test_game_related_questions()
    print()
    
    print("3️⃣ Testing off-topic questions...")
    test3 = test_off_topic_questions()
    print()
    
    print("4️⃣ Testing Zelda character guardrail...")
    test4 = test_zelda_guardrail()
    
    print("\n" + "=" * 60)
    total_tests = 4
    passed_tests = sum([test1, test2, test3, test4])
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Intent-based routing is working!")
    else:
        print(f"💥 {total_tests - passed_tests} out of {total_tests} tests failed!")
        print("Check the output above for details.")
