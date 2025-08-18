#!/usr/bin/env python3
"""
Test script for the LangGraph implementation
"""
import os
from app import run_hint_request

def test_game_related_questions():
    """Test various game-related questions that should get hints"""
    
    game_questions = [
        "How do I find the token?",
        "Where is the bus?", 
        "I'm stuck on this puzzle",
        "Who is Zelda?",
        "How do I save the game?",
        "I need help in the Thirsty Tentacle",
        "What do I do next?"
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
        "Can you help me with my homework?"
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
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print(f"\n🎯 Off-topic questions success rate: {success_count}/{len(off_topic_questions)}")
    return success_count == len(off_topic_questions)

def test_basic_flow():
    """Test the basic flow with explicit hint request"""
    
    # Test with a clear hint request
    test_input = "I need a hint to find the bus token"
    print(f"Testing with input: '{test_input}'")
    
    try:
        result = run_hint_request(test_input)
        print(f"✅ Success! Result: {result}")
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
    
    print("\n" + "=" * 60)
    total_tests = 3
    passed_tests = sum([test1, test2, test3])
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Intent-based routing is working!")
    else:
        print(f"💥 {total_tests - passed_tests} out of {total_tests} tests failed!")
        print("Check the output above for details.")
