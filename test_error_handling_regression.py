#!/usr/bin/env python3
"""
Quick regression test for error handling changes
Run this to verify error handling didn't break normal operation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_normal_operations():
    """Test that normal operations still work"""
    print("🧪 Testing Normal Operations...")
    
    try:
        from app import run_hint_request
        
        # Test normal hint request
        response = run_hint_request("How do I find the bus token?")
        
        # Basic checks
        assert len(response) > 10, "Response too short"
        assert "🎯 Hint" in response, "Missing hint formatting"
        assert not response.startswith("Error"), "Response starts with Error"
        
        print("✅ Normal hint request: PASS")
        
        # Test off-topic request
        response2 = run_hint_request("What's the weather?")
        assert len(response2) > 10, "Off-topic response too short"
        assert "sweetie" in response2.lower() or "sorry" in response2.lower(), "Missing off-topic indicators"
        
        print("✅ Off-topic request: PASS")
        
        # Test vague request (should trigger error message node)
        response3 = run_hint_request("I'm stuck")
        assert len(response3) > 10, "Vague response too short"
        assert not "🎯 Hint" in response3, "Vague request shouldn't give specific hint"
        
        print("✅ Vague request (error message): PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Normal operations test failed: {e}")
        return False

def test_imports():
    """Test that all modified modules import correctly"""
    print("🧪 Testing Imports...")
    
    try:
        from generate_error_message_node import generate_error_message_node
        print("✅ generate_error_message_node import: PASS")
        
        from verify_correctness_node import verify_correctness_node
        print("✅ verify_correctness_node import: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_state_handling():
    """Test that state objects are handled correctly"""
    print("🧪 Testing State Handling...")
    
    try:
        from state import LangGraphState
        from generate_error_message_node import generate_error_message_node
        
        # Create test state
        test_state = LangGraphState(
            user_input="Test question",
            verification_reason="INSUFFICIENT_CONTEXT",
            formatted_output=""
        )
        
        # Run the node
        result_state = generate_error_message_node(test_state)
        
        # Check that formatted_output was set
        assert "formatted_output" in result_state, "formatted_output not in result state"
        assert len(result_state["formatted_output"]) > 0, "formatted_output is empty"
        assert "detective" in result_state["formatted_output"].lower(), "Response doesn't seem like Zelda"
        
        print("✅ State handling: PASS")
        return True
        
    except Exception as e:
        print(f"❌ State handling test failed: {e}")
        return False

def main():
    """Run all regression tests"""
    print("🚀 Error Handling Regression Tests")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  Warning: dotenv not available")
    
    tests = [
        ("Imports", test_imports),
        ("State Handling", test_state_handling), 
        ("Normal Operations", test_normal_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 REGRESSION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All regression tests PASSED! Your changes are safe.")
        return 0
    else:
        print("⚠️  Some regression tests FAILED. Review changes before proceeding.")
        return 1

if __name__ == "__main__":
    exit(main())
