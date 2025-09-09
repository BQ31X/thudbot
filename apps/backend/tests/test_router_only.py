#!/usr/bin/env python3
"""
Router-Only Test Script
Tests just the classifier without running the full LangGraph pipeline
Perfect for testing nano vs mini model performance
"""

import os
import sys
import time
import pytest

skip_in_ci = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skip OpenAI-dependent test in CI (no API key)"
)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'thudbot_core'))

# Environment loading handled by conftest.py

from langgraph_flow import classify_intent

@skip_in_ci
def test_router_classification():
    """Test router classification on a variety of questions"""
    
    test_cases = [
        # Game-related questions (should be GAME_RELATED)
        ("How do I find the bus token?", "GAME_RELATED"),
        ("Who is Zelda?", "GAME_RELATED"),
        ("Where is the Thirsty Tentacle?", "GAME_RELATED"),
        ("How do I open the locker?", "GAME_RELATED"),
        ("What should I do with Thud?", "GAME_RELATED"),
        ("How do I save the game?", "GAME_RELATED"),
        ("Where can I find money?", "GAME_RELATED"),
        ("How do I solve this puzzle?", "GAME_RELATED"),
        
        # Off-topic questions (should be OFF_TOPIC)
        ("What's the weather like?", "OFF_TOPIC"),
        ("How do I install Python?", "OFF_TOPIC"),
        ("Tell me a joke", "OFF_TOPIC"),
        ("What's your favorite color?", "OFF_TOPIC"),
        ("What's the latest news?", "OFF_TOPIC"),
        ("Hello, how are you?", "OFF_TOPIC"),
        ("Help me with my homework", "OFF_TOPIC"),
        
        # Edge cases
        ("I'm stuck", "OFF_TOPIC"),  # Too vague
        ("What should I do?", "OFF_TOPIC"),  # Too vague
        ("How do I cast spells?", "GAME_RELATED"),  # Game-ish but not in Space Bar
    ]
    
    print("🎯 ROUTER CLASSIFICATION TEST")
    print("=" * 80)
    print(f"{'QUESTION':<40} {'EXPECTED':<15} {'ACTUAL':<15} {'✓/✗':<5}")
    print("-" * 80)
    
    correct = 0
    total = len(test_cases)
    start_time = time.time()
    
    for question, expected in test_cases:
        try:
            actual = classify_intent(question)
            is_correct = actual == expected
            correct += is_correct
            
            status = "✓" if is_correct else "✗"
            print(f"{question[:39]:<40} {expected:<15} {actual:<15} {status:<5}")
            
        except Exception as e:
            print(f"{question[:39]:<40} {expected:<15} {'ERROR':<15} {'✗':<5}")
            print(f"   Error: {e}")
    
    duration = time.time() - start_time
    accuracy = (correct / total) * 100
    
    print("-" * 80)
    print(f"📊 RESULTS:")
    print(f"   Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"   Duration: {duration:.2f}s ({duration/total:.3f}s per question)")
    print(f"   Model: Check src/langgraph_flow.py line 23 for current model")
    
    if accuracy >= 95:
        print("🎉 EXCELLENT: Router performing very well!")
    elif accuracy >= 90:
        print("✅ GOOD: Router performing adequately")
    elif accuracy >= 80:
        print("⚠️  CONCERN: Router accuracy could be better")
    else:
        print("❌ ISSUE: Router needs attention")
    
    # Use assertions instead of return for pytest compatibility
    assert accuracy >= 80, f"Router accuracy too low: {accuracy:.1f}% (expected >= 80%)"
    assert duration < 30, f"Router too slow: {duration:.2f}s (expected < 30s)"
    


def test_consistency():
    """Test the same question multiple times to check for consistency"""
    test_question = "How do I find the bus token?"
    iterations = 5
    
    print(f"\n🔄 CONSISTENCY TEST")
    print("=" * 50)
    print(f"Testing '{test_question}' {iterations} times...")
    
    results = []
    for i in range(iterations):
        result = classify_intent(test_question)
        results.append(result)
        print(f"   Run {i+1}: {result}")
    
    unique_results = set(results)
    consistency = len(unique_results) == 1
    
    print(f"\n📊 Consistency: {'✓ CONSISTENT' if consistency else '✗ INCONSISTENT'}")
    if not consistency:
        print(f"   Got different results: {list(unique_results)}")
    
    # Use assertion instead of return for pytest compatibility
    assert consistency, f"Router inconsistent: got different results {list(unique_results)}"
    

def main():
    """Main test runner"""
    print("🚀 Starting Router-Only Testing")
    print(f"   Working directory: {os.getcwd()}")
    print(f"   Testing classification function directly (no full pipeline)")
    print()
    
    # Test classification accuracy
    accuracy, duration = test_router_classification()
    
    # Test consistency
    consistency = test_consistency()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Speed: {duration:.2f}s total")
    print(f"   Consistency: {'✓' if consistency else '✗'}")
    
    if accuracy >= 95 and consistency:
        print("✅ ROUTER READY: Good to use this model!")
    else:
        print("⚠️  ROUTER NEEDS REVIEW: Consider model adjustment")

if __name__ == "__main__":
    main()
