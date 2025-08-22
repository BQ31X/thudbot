#!/usr/bin/env python3
"""
Comprehensive Test Battery for Thudbot Hint System
Tests edge cases, regression, user experience, verification system, and performance
Created for Demo Day preparation (8/25) with code freeze (8/21)
"""

import os
import time
import json
import csv
import hashlib
from typing import Dict, List, Tuple, Any
from pathlib import Path
from app import run_hint_request
from agent import get_direct_hint
import pandas as pd
from test_queries import (
    CORE_GAME_QUESTIONS, OFF_TOPIC_QUESTIONS, VAGUE_QUESTIONS, 
    SPECIFIC_GAME_QUESTIONS, VERIFICATION_EDGE_CASES, HALLUCINATION_RISK_QUESTIONS,
    UX_TEST_QUESTIONS, PERFORMANCE_TEST_QUESTIONS, EDGE_CASE_INPUTS, TEST_CONFIG
)

class TestResults:
    """Track and analyze test results"""
    def __init__(self):
        self.results = []
        self.performance_metrics = {}
        self.verification_stats = {}
        self.edge_case_failures = []
        
    def add_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Add a test result"""
        self.results.append({
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "edge_case_failures": len(self.edge_case_failures),
            "verification_stats": self.verification_stats,
            "performance_metrics": self.performance_metrics
        }

def setup_test_environment() -> bool:
    """Verify test environment is ready"""
    print("🔧 Setting up test environment...")
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    # Check required files
    required_files = [
        "data/Thudbot_Hint_Data_1.csv",
        "src/app.py",
        "src/agent.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file missing: {file_path}")
            return False
    
    print("✅ Test environment ready")
    return True

class EdgeCaseTests:
    """Test boundary conditions and unusual inputs"""
    
    def __init__(self, results: TestResults):
        self.results = results
    
    def test_empty_inputs(self):
        """Test empty and whitespace-only inputs"""
        test_cases = EDGE_CASE_INPUTS["empty_inputs"]
        
        for i, test_input in enumerate(test_cases):
            try:
                response = run_hint_request(test_input)
                # Should handle gracefully, not crash
                status = "PASS" if response else "FAIL"
                self.results.add_result(
                    f"empty_input_{i}",
                    status,
                    {"input": repr(test_input), "response": response}
                )
            except Exception as e:
                self.results.add_result(
                    f"empty_input_{i}",
                    "FAIL",
                    {"input": repr(test_input), "error": str(e)}
                )
    
    def test_extremely_long_inputs(self):
        """Test very long inputs that might break tokenization"""
        test_cases = EDGE_CASE_INPUTS["long_inputs"]
        
        for i, test_input in enumerate(test_cases):
            try:
                start_time = time.time()
                response = run_hint_request(test_input)
                duration = time.time() - start_time
                
                # Should handle within reasonable time (< 30 seconds)
                status = "PASS" if response and duration < 30 else "FAIL"
                self.results.add_result(
                    f"long_input_{i}",
                    status,
                    {
                        "input_length": len(test_input),
                        "response_length": len(response) if response else 0,
                        "duration": duration
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"long_input_{i}",
                    "FAIL",
                    {"input_length": len(test_input), "error": str(e)}
                )
    
    def test_special_characters(self):
        """Test inputs with special characters and encoding"""
        test_cases = EDGE_CASE_INPUTS["special_characters"]
        
        for i, test_input in enumerate(test_cases):
            try:
                response = run_hint_request(test_input)
                # Should handle gracefully and provide appropriate response
                status = "PASS" if response and len(response) > 10 else "FAIL"
                self.results.add_result(
                    f"special_chars_{i}",
                    status,
                    {"input": test_input, "response_length": len(response) if response else 0}
                )
            except Exception as e:
                self.results.add_result(
                    f"special_chars_{i}",
                    "FAIL",
                    {"input": test_input, "error": str(e)}
                )
    
    def test_ambiguous_pronouns(self):
        """Test questions with ambiguous pronouns and references"""
        test_cases = EDGE_CASE_INPUTS["ambiguous_pronouns"]
        
        for i, test_input in enumerate(test_cases):
            try:
                response = run_hint_request(test_input)
                # Should either ask for clarification or handle gracefully
                contains_clarification = any(word in response.lower() for word in 
                    ["clarification", "specific", "which", "what do you mean", "more details"])
                
                status = "PASS" if contains_clarification or "Listen sweetie" in response else "FAIL"
                self.results.add_result(
                    f"ambiguous_{i}",
                    status,
                    {"input": test_input, "asks_clarification": contains_clarification}
                )
            except Exception as e:
                self.results.add_result(
                    f"ambiguous_{i}",
                    "FAIL",
                    {"input": test_input, "error": str(e)}
                )

class RegressionTests:
    """Test that existing functionality still works after today's changes"""
    
    def __init__(self, results: TestResults):
        self.results = results
    
    def test_core_functionality(self):
        """Test core game questions that should always work"""
        core_questions = CORE_GAME_QUESTIONS
        
        for question, expected_keyword in core_questions:
            try:
                response = run_hint_request(question)
                contains_keyword = expected_keyword.lower() in response.lower()
                
                status = "PASS" if response and contains_keyword else "FAIL"
                self.results.add_result(
                    f"core_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "expected_keyword": expected_keyword,
                        "contains_keyword": contains_keyword,
                        "response_length": len(response) if response else 0
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"core_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
    
    def test_off_topic_routing(self):
        """Test that off-topic questions are properly routed"""
        off_topic_questions = OFF_TOPIC_QUESTIONS
        
        for question in off_topic_questions:
            try:
                response = run_hint_request(question)
                is_off_topic_response = any(phrase in response for phrase in 
                    ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                
                status = "PASS" if is_off_topic_response else "FAIL"
                self.results.add_result(
                    f"off_topic_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "is_off_topic_response": is_off_topic_response,
                        "response": response[:100] + "..." if len(response) > 100 else response
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"off_topic_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
    
    def test_zelda_guardrails(self):
        """Test that Zelda character guardrails work"""
        try:
            response = run_hint_request("Who is Zelda?")
            
            # Should NOT contain Legend of Zelda references
            forbidden_terms = ["legend of zelda", "hyrule", "princess", "nintendo", "triforce"]
            contains_forbidden = any(term in response.lower() for term in forbidden_terms)
            
            # Should contain Space Bar references
            space_bar_terms = ["space bar", "pda", "personal digital assistant", "detective"]
            contains_space_bar = any(term in response.lower() for term in space_bar_terms)
            
            status = "PASS" if not contains_forbidden and contains_space_bar else "FAIL"
            self.results.add_result(
                "zelda_guardrails",
                status,
                {
                    "contains_forbidden": contains_forbidden,
                    "contains_space_bar": contains_space_bar,
                    "response": response
                }
            )
        except Exception as e:
            self.results.add_result(
                "zelda_guardrails",
                "FAIL",
                {"error": str(e)}
            )

class VerificationSystemTests:
    """Test the verification system for hallucination detection and edge cases"""
    
    def __init__(self, results: TestResults):
        self.results = results
        self.verification_counts = {"VERIFIED": 0, "TOO_SPECIFIC": 0, "HALLUCINATED": 0, "INSUFFICIENT_CONTEXT": 0}
    
    def test_vague_question_handling(self):
        """Test that vague questions get appropriate responses"""
        vague_questions = VAGUE_QUESTIONS
        
        for question in vague_questions:
            try:
                response = run_hint_request(question)
                
                # Should either ask for clarification or give off-topic response
                asks_clarification = any(word in response.lower() for word in 
                    ["specific", "which", "more details", "clarification"])
                is_off_topic = any(phrase in response for phrase in 
                    ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                
                appropriate_response = asks_clarification or is_off_topic
                
                status = "PASS" if appropriate_response else "FAIL"
                self.results.add_result(
                    f"vague_question_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "asks_clarification": asks_clarification,
                        "is_off_topic": is_off_topic,
                        "response": response[:100] + "..." if len(response) > 100 else response
                    }
                )
                
                if not appropriate_response:
                    self.results.edge_case_failures.append({
                        "type": "vague_question_specificity",
                        "question": question,
                        "response": response
                    })
                    
            except Exception as e:
                self.results.add_result(
                    f"vague_question_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
    
    def test_specific_question_handling(self):
        """Test that specific questions get specific answers"""
        specific_questions = SPECIFIC_GAME_QUESTIONS
        
        for question, expected_keywords in specific_questions:
            try:
                response = run_hint_request(question)
                
                # Should contain relevant keywords
                contains_keywords = any(keyword.lower() in response.lower() 
                                      for keyword in expected_keywords)
                
                # Should not be off-topic response
                is_off_topic = any(phrase in response for phrase in 
                    ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                
                status = "PASS" if contains_keywords and not is_off_topic else "FAIL"
                self.results.add_result(
                    f"specific_question_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "expected_keywords": expected_keywords,
                        "contains_keywords": contains_keywords,
                        "is_off_topic": is_off_topic
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"specific_question_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
    
    def test_verification_edge_cases(self):
        """Test edge cases in the verification system"""
        print("🔍 Testing verification system edge cases...")
        
        # Test each verification outcome type
        verification_test_cases = VERIFICATION_EDGE_CASES
        
        for test_case in verification_test_cases:
            question = test_case["question"]
            expected_behavior = test_case["expected_behavior"]
            test_type = test_case["test_type"]
            
            try:
                response = run_hint_request(question)
                
                # Analyze response against expected behavior
                response_lower = response.lower()
                
                if expected_behavior == "clarification_or_off_topic":
                    # Should ask for clarification OR be off-topic response
                    asks_clarification = any(word in response_lower for word in 
                        ["specific", "which", "more details", "clarification"])
                    is_off_topic = any(phrase in response for phrase in 
                        ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                    
                    appropriate = asks_clarification or is_off_topic
                    
                elif expected_behavior == "specific_helpful_response":
                    # Should contain relevant information
                    is_helpful = len(response) > 30 and not any(error in response_lower 
                        for error in ["error", "exception", "failed"])
                    not_off_topic = not any(phrase in response for phrase in 
                        ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                    
                    appropriate = is_helpful and not_off_topic
                    
                elif expected_behavior == "character_information":
                    # Should contain character-related info
                    has_character_info = any(term in response_lower for term in 
                        ["assistant", "pda", "digital", "zelda"])
                    not_forbidden = not any(term in response_lower for term in 
                        ["princess", "hyrule", "legend of zelda"])
                    
                    appropriate = has_character_info and not_forbidden
                    
                elif expected_behavior == "insufficient_context_message":
                    # Should indicate lack of information or be off-topic
                    insufficient_indicated = any(phrase in response_lower for phrase in 
                        ["not enough", "insufficient", "don't have", "can't find"])
                    is_off_topic = any(phrase in response for phrase in 
                        ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                    
                    appropriate = insufficient_indicated or is_off_topic
                else:
                    appropriate = True  # Unknown test type
                
                status = "PASS" if appropriate else "FAIL"
                self.results.add_result(
                    f"verification_edge_{test_type.lower()}_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "test_type": test_type,
                        "expected_behavior": expected_behavior,
                        "appropriate_response": appropriate,
                        "response_length": len(response)
                    }
                )
                
                if appropriate:
                    print(f"   ✅ {test_type}: {question[:40]}...")
                    self.verification_counts[test_type] = self.verification_counts.get(test_type, 0) + 1
                else:
                    print(f"   ❌ {test_type}: {question[:40]}... - Unexpected response")
                    
            except Exception as e:
                self.results.add_result(
                    f"verification_edge_{test_type.lower()}_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "test_type": test_type, "error": str(e)}
                )
                print(f"   ❌ {test_type}: {question[:40]}... - Error: {e}")
    
    def test_hallucination_detection(self):
        """Test the system's ability to detect and handle hallucinated responses"""
        print("🚫 Testing hallucination detection...")
        
        # Questions that might lead to hallucinations if not properly controlled
        hallucination_risk_questions = HALLUCINATION_RISK_QUESTIONS
        
        for question in hallucination_risk_questions:
            try:
                response = run_hint_request(question)
                
                # Check for hallucination indicators
                response_lower = response.lower()
                
                # Should either be off-topic or indicate insufficient information
                is_off_topic = any(phrase in response for phrase in 
                    ["Listen sweetie", "Sorry hon", "I appreciate the chat"])
                indicates_no_info = any(phrase in response_lower for phrase in 
                    ["don't have", "not found", "insufficient", "not enough"])
                
                # Should NOT contain made-up detailed game information
                contains_details = any(suspicious in response_lower for suspicious in 
                    ["press the", "click on", "go to the", "use the", "find the"])
                
                # Appropriate response: off-topic OR indicates no info, but NOT detailed made-up info
                appropriate = (is_off_topic or indicates_no_info) and not contains_details
                
                status = "PASS" if appropriate else "FAIL"
                self.results.add_result(
                    f"hallucination_detection_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "is_off_topic": is_off_topic,
                        "indicates_no_info": indicates_no_info,
                        "contains_suspicious_details": contains_details,
                        "appropriate_response": appropriate
                    }
                )
                
                if appropriate:
                    print(f"   ✅ Handled appropriately: {question[:40]}...")
                else:
                    print(f"   ❌ Potential hallucination: {question[:40]}...")
                    
            except Exception as e:
                self.results.add_result(
                    f"hallucination_detection_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
                print(f"   ❌ Error testing: {question[:40]}... - {e}")

class UserExperienceTests:
    """Test real-world question patterns and response quality"""
    
    def __init__(self, results: TestResults):
        self.results = results
    
    def test_response_quality_metrics(self):
        """Test response quality characteristics"""
        test_questions = UX_TEST_QUESTIONS
        
        for question in test_questions:
            try:
                response = run_hint_request(question)
                
                # Quality metrics
                length_appropriate = 50 <= len(response) <= 500  # Reasonable length
                no_technical_errors = "error" not in response.lower() and "exception" not in response.lower()
                has_personality = any(word in response.lower() for word in 
                    ["sweetie", "hon", "zelda", "assistant", "help"])
                
                quality_score = sum([length_appropriate, no_technical_errors, has_personality])
                
                status = "PASS" if quality_score >= 2 else "FAIL"
                self.results.add_result(
                    f"quality_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "response_length": len(response),
                        "length_appropriate": length_appropriate,
                        "no_technical_errors": no_technical_errors,
                        "has_personality": has_personality,
                        "quality_score": quality_score
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"quality_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
    
    def test_response_consistency(self):
        """Test that same questions get consistent responses"""
        test_question = "How do I find the bus token?"
        responses = []
        
        # Ask the same question multiple times
        for i in range(3):
            try:
                response = run_hint_request(test_question)
                responses.append(response)
            except Exception as e:
                self.results.add_result(
                    f"consistency_{i}",
                    "FAIL",
                    {"question": test_question, "error": str(e)}
                )
                return
        
        # Check for consistency (allowing for some variation)
        # All responses should contain key terms
        key_terms = ["token", "bus"]
        all_contain_terms = all(
            any(term in response.lower() for term in key_terms)
            for response in responses
        )
        
        # Responses should not be identical (some variation is good)
        all_identical = len(set(responses)) == 1
        
        status = "PASS" if all_contain_terms and not all_identical else "FAIL"
        self.results.add_result(
            "consistency_test",
            status,
            {
                "question": test_question,
                "all_contain_terms": all_contain_terms,
                "all_identical": all_identical,
                "response_count": len(responses),
                "unique_responses": len(set(responses))
            }
        )

class PerformanceTests:
    """Test performance and establish baselines"""
    
    def __init__(self, results: TestResults):
        self.results = results
    
    def test_response_times(self):
        """Test response time performance"""
        test_questions = PERFORMANCE_TEST_QUESTIONS
        
        response_times = []
        
        for question in test_questions:
            try:
                start_time = time.time()
                response = run_hint_request(question)
                duration = time.time() - start_time
                
                response_times.append(duration)
                
                # Response should be under 15 seconds for good UX
                status = "PASS" if duration < 15.0 and response else "FAIL"
                self.results.add_result(
                    f"performance_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    status,
                    {
                        "question": question,
                        "duration": duration,
                        "response_length": len(response) if response else 0
                    }
                )
            except Exception as e:
                self.results.add_result(
                    f"performance_{hashlib.md5(question.encode()).hexdigest()[:8]}",
                    "FAIL",
                    {"question": question, "error": str(e)}
                )
        
        # Calculate performance metrics
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            self.results.performance_metrics = {
                "average_response_time": avg_time,
                "max_response_time": max_time,
                "min_response_time": min_time,
                "total_tests": len(response_times)
            }

def run_comprehensive_tests():
    """Run all test suites and generate comprehensive report"""
    
    print("🧪 THUDBOT COMPREHENSIVE TEST BATTERY")
    print("=" * 80)
    print("Testing edge cases, regression, verification, UX, and performance")
    print("Demo Day: 8/25 | Code Freeze: 8/21")
    print("=" * 80)
    
    # Setup
    if not setup_test_environment():
        return False
    
    # Initialize results tracker
    results = TestResults()
    
    # Run test suites
    print("\n🔬 Running Edge Case Tests...")
    edge_tests = EdgeCaseTests(results)
    edge_tests.test_empty_inputs()
    edge_tests.test_extremely_long_inputs()
    edge_tests.test_special_characters()
    edge_tests.test_ambiguous_pronouns()
    
    print("\n🔄 Running Regression Tests...")
    regression_tests = RegressionTests(results)
    regression_tests.test_core_functionality()
    regression_tests.test_off_topic_routing()
    regression_tests.test_zelda_guardrails()
    
    print("\n🔍 Running Verification System Tests...")
    verification_tests = VerificationSystemTests(results)
    verification_tests.test_vague_question_handling()
    verification_tests.test_specific_question_handling()
    verification_tests.test_verification_edge_cases()
    verification_tests.test_hallucination_detection()
    
    print("\n👥 Running User Experience Tests...")
    ux_tests = UserExperienceTests(results)
    ux_tests.test_response_quality_metrics()
    ux_tests.test_response_consistency()
    
    print("\n⚡ Running Performance Tests...")
    perf_tests = PerformanceTests(results)
    perf_tests.test_response_times()
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    summary = results.get_summary()
    
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    if summary['edge_case_failures']:
        print(f"\n⚠️  Edge Case Failures: {summary['edge_case_failures']}")
        for failure in results.edge_case_failures[:3]:  # Show first 3
            print(f"   - {failure['type']}: {failure['question']}")
    
    if summary['performance_metrics']:
        perf = summary['performance_metrics']
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Response Time: {perf.get('average_response_time', 0):.2f}s")
        print(f"   Max Response Time: {perf.get('max_response_time', 0):.2f}s")
        print(f"   Min Response Time: {perf.get('min_response_time', 0):.2f}s")
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "summary": summary,
            "detailed_results": results.results,
            "timestamp": timestamp,
            "test_environment": {
                "cache_enabled": os.path.exists("./cache/embeddings"),
                "data_file_size": os.path.getsize("data/Thudbot_Hint_Data_1.csv") if os.path.exists("data/Thudbot_Hint_Data_1.csv") else 0
            }
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if summary['success_rate'] >= 90:
        print("✅ System is ready for progressive hints implementation!")
    elif summary['success_rate'] >= 80:
        print("⚠️  Address critical failures before progressive hints")
    else:
        print("❌ Significant issues need resolution before proceeding")
    
    if summary['edge_case_failures'] > 0:
        print("🔧 Review edge case failures for robustness improvements")
    
    if summary['performance_metrics'].get('average_response_time', 0) > 10:
        print("⚡ Consider performance optimizations")
    
    print("\n🚀 Ready for Demo Day preparation!")
    return summary['success_rate'] >= 80

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
