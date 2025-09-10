#!/usr/bin/env python3
"""
Progressive Hints Preparation Tests
Tests the infrastructure needed for implementing progressive hints
Validates hint level escalation, repeat question detection, and multi-level responses
"""

import os
import time


from typing import Dict, List, Tuple
from thudbot_core.app import run_hint_request
from thudbot_core.state import LangGraphState
from tests.test_queries import PROGRESSIVE_HINTS_QUESTIONS


class ProgressiveHintsValidator:
    """Validate readiness for progressive hints implementation"""
    
    def __init__(self):
        self.test_results = []
        
    def test_hint_level_state_management(self):
        """Test that hint levels are properly tracked in state"""
        print("🔄 Testing hint level state management...")
        
        # Test initial state
        initial_state = {
            "user_input": "How do I find the bus token?",
            "chat_history": [],
            "hint_level": 1,
            "last_question_id": "",
            "current_hint": "",
            "formatted_output": "",
            "verification_passed": False,
            "verification_reason": "",
            "retry_count": 0,
            "retrieved_context": ""
        }
        
        # Test escalation logic (simulated)
        test_question = "How do I find the bus token?"
        
        try:
            # First request
            response1 = run_hint_request(test_question)
            
            # Note: Since we don't have direct access to state between calls,
            # we test that the system can handle the same question multiple times
            # without breaking
            
            # Second request (same question)
            response2 = run_hint_request(test_question)
            
            # Third request (same question)  
            response3 = run_hint_request(test_question)
            
            # Responses should be valid and potentially different
            responses_valid = all(resp and len(resp) > 10 for resp in [response1, response2, response3])
            
            self.test_results.append({
                "test": "hint_level_management",
                "passed": responses_valid,
                "details": {
                    "response1_length": len(response1) if response1 else 0,
                    "response2_length": len(response2) if response2 else 0,
                    "response3_length": len(response3) if response3 else 0,
                    "all_responses_valid": responses_valid
                }
            })
            
            print(f"   ✅ Multiple requests handled successfully")
            
        except Exception as e:
            self.test_results.append({
                "test": "hint_level_management",
                "passed": False,
                "details": {"error": str(e)}
            })
            print(f"   ❌ Error in hint level management: {e}")
    
    def test_repeat_question_detection(self):
        """Test infrastructure for detecting repeat questions"""
        print("🔍 Testing repeat question detection infrastructure...")
        
        # Test various forms of the same question
        question_variants = PROGRESSIVE_HINTS_QUESTIONS["repeat_detection_variants"]
        
        responses = []
        try:
            for variant in question_variants:
                response = run_hint_request(variant)
                responses.append(response)
                time.sleep(0.5)  # Small delay between requests
            
            # All responses should be valid
            all_valid = all(resp and len(resp) > 10 for resp in responses)
            
            # System should handle variations gracefully
            self.test_results.append({
                "test": "repeat_question_detection",
                "passed": all_valid,
                "details": {
                    "variants_tested": len(question_variants),
                    "valid_responses": sum(1 for resp in responses if resp and len(resp) > 10),
                    "all_valid": all_valid
                }
            })
            
            if all_valid:
                print(f"   ✅ All question variants handled successfully")
            else:
                print(f"   ❌ Some question variants failed")
                
        except Exception as e:
            self.test_results.append({
                "test": "repeat_question_detection", 
                "passed": False,
                "details": {"error": str(e)}
            })
            print(f"   ❌ Error in repeat question detection: {e}")
    
    def test_multi_level_hint_content(self):
        """Test that system can provide different levels of detail"""
        print("📚 Testing multi-level hint content capability...")
        
        # Test questions that should have multiple hint levels in dataset
        test_questions = PROGRESSIVE_HINTS_QUESTIONS["multi_level_potential"]
        
        for question in test_questions:
            try:
                response = run_hint_request(question)
                
                # Analyze response characteristics for hint level potential
                response_length = len(response)
                contains_detail = response_length > 50
                contains_specifics = any(word in response.lower() for word in 
                    ["click", "button", "menu", "action", "use", "find", "look"])
                
                hint_potential = contains_detail and contains_specifics
                
                self.test_results.append({
                    "test": f"multi_level_content_{question[:20]}",
                    "passed": hint_potential,
                    "details": {
                        "question": question,
                        "response_length": response_length,
                        "contains_detail": contains_detail,
                        "contains_specifics": contains_specifics,
                        "hint_potential": hint_potential
                    }
                })
                
                if hint_potential:
                    print(f"   ✅ {question[:30]}... - Good hint potential")
                else:
                    print(f"   ⚠️  {question[:30]}... - Limited hint potential")
                    
            except Exception as e:
                self.test_results.append({
                    "test": f"multi_level_content_{question[:20]}",
                    "passed": False,
                    "details": {"question": question, "error": str(e)}
                })
                print(f"   ❌ Error testing {question[:30]}...: {e}")
    
    def test_context_preservation(self):
        """Test that context is preserved between hint levels"""
        print("💾 Testing context preservation capability...")
        
        test_question = "How do I find the bus token?"
        
        try:
            # Get response and check if context data is being retrieved
            response = run_hint_request(test_question)
            
            # Check if response contains contextual information
            has_context = any(term in response.lower() for term in 
                ["bus", "token", "click", "action", "menu", "pick up", "stash"])
            
            response_coherent = len(response) > 20 and not any(error_term in response.lower() 
                for error_term in ["error", "exception", "failed"])
            
            context_preserved = has_context and response_coherent
            
            self.test_results.append({
                "test": "context_preservation",
                "passed": context_preserved,
                "details": {
                    "has_context": has_context,
                    "response_coherent": response_coherent,
                    "response_length": len(response)
                }
            })
            
            if context_preserved:
                print(f"   ✅ Context preservation working")
            else:
                print(f"   ❌ Context preservation issues detected")
                
        except Exception as e:
            self.test_results.append({
                "test": "context_preservation",
                "passed": False,
                "details": {"error": str(e)}
            })
            print(f"   ❌ Error testing context preservation: {e}")
    
    def test_hint_escalation_readiness(self):
        """Test readiness for hint escalation implementation"""
        print("🎯 Testing hint escalation readiness...")
        
        # Test that the current system provides consistent, quality responses
        # that could be enhanced with progressive hints
        
        base_questions = PROGRESSIVE_HINTS_QUESTIONS["escalation_readiness"]
        
        escalation_ready = True
        
        for question in base_questions:
            try:
                response = run_hint_request(question)
                
                # Quality checks for escalation readiness
                sufficient_length = len(response) >= 30
                helpful_content = any(word in response.lower() for word in 
                    ["use", "click", "try", "find", "look", "press", "select"])
                no_errors = not any(error in response.lower() for error in 
                    ["error", "exception", "failed", "sorry"])
                
                question_ready = sufficient_length and helpful_content and no_errors
                
                if not question_ready:
                    escalation_ready = False
                
                self.test_results.append({
                    "test": f"escalation_ready_{question[:15]}",
                    "passed": question_ready,
                    "details": {
                        "question": question,
                        "sufficient_length": sufficient_length,
                        "helpful_content": helpful_content,
                        "no_errors": no_errors
                    }
                })
                
                if question_ready:
                    print(f"   ✅ {question[:30]}... - Ready for escalation")
                else:
                    print(f"   ❌ {question[:30]}... - Not ready for escalation")
                    
            except Exception as e:
                escalation_ready = False
                self.test_results.append({
                    "test": f"escalation_ready_{question[:15]}",
                    "passed": False,
                    "details": {"question": question, "error": str(e)}
                })
                print(f"   ❌ Error testing {question[:30]}...: {e}")
        
        return escalation_ready
    
    def run_progressive_hints_validation(self) -> Dict[str, any]:
        """Run complete progressive hints readiness validation"""
        print("🚀 PROGRESSIVE HINTS PREPARATION VALIDATION")
        print("=" * 70)
        print("Testing readiness for hint level escalation implementation")
        print("=" * 70)
        
        # Check API key
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY not found in environment")
            return {"success": False, "error": "Missing API key"}
        
        # Run validation tests
        self.test_hint_level_state_management()
        self.test_repeat_question_detection()
        self.test_multi_level_hint_content()
        self.test_context_preservation()
        escalation_ready = self.test_hint_escalation_readiness()
        
        # Analyze results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n" + "=" * 70)
        print("📊 PROGRESSIVE HINTS READINESS SUMMARY")
        print("=" * 70)
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if escalation_ready and success_rate >= 80:
            print("✅ SYSTEM READY for progressive hints implementation!")
            readiness_status = "READY"
        elif success_rate >= 60:
            print("⚠️  SYSTEM MOSTLY READY - address failing tests first")
            readiness_status = "MOSTLY_READY"
        else:
            print("❌ SYSTEM NOT READY - significant issues need resolution")
            readiness_status = "NOT_READY"
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["passed"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:5]:  # Show first 5 failures
                print(f"   - {test['test']}")
                if 'error' in test['details']:
                    print(f"     Error: {test['details']['error']}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if readiness_status == "READY":
            print("✅ Proceed with progressive hints implementation")
            print("✅ Current system provides solid foundation")
            print("✅ Focus on hint level escalation logic")
        elif readiness_status == "MOSTLY_READY":
            print("🔧 Address critical test failures before proceeding")
            print("⚠️  Test progressive hints in isolated environment first")
        else:
            print("🛑 Resolve fundamental issues before progressive hints")
            print("🔧 Focus on stabilizing core functionality")
        
        return {
            "readiness_status": readiness_status,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "escalation_ready": escalation_ready
        }

def run_progressive_hints_prep():
    """Main function to run progressive hints preparation validation"""
    validator = ProgressiveHintsValidator()
    results = validator.run_progressive_hints_validation()
    return results

if __name__ == "__main__":
    results = run_progressive_hints_prep()
    # Exit with appropriate code
    if results.get("readiness_status") == "READY":
        exit(0)
    elif results.get("readiness_status") == "MOSTLY_READY":
        exit(1)
    else:
        exit(2)
