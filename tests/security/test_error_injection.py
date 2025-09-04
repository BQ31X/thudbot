#!/usr/bin/env python3
"""
Error Injection Testing for Thudbot

This script systematically tests error handling by intentionally breaking
different components to ensure the user never sees raw stack traces.
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from typing import Generator
import time
from datetime import datetime

# Add src to path for imports (from tests/security/ perspective)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from app import run_hint_request
    from api import app as fastapi_app
    from agent import get_direct_hint_with_context
    from fastapi.testclient import TestClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root with dependencies installed")
    sys.exit(1)

class ErrorInjectionTester:
    """Systematically test error scenarios to ensure graceful handling"""
    
    def __init__(self):
        self.results = []
        self.client = TestClient(fastapi_app)
        
    def run_all_error_tests(self):
        """Run comprehensive error injection testing"""
        print("🧪 Starting Error Injection Testing")
        print("=" * 60)
        
        # Test categories - comment out OpenAI tests if concerned about key exposure
        test_methods = [
            ("OpenAI API Failures", self.test_openai_failures),  # Uncomment if safe
            ("RAG System Failures", self.test_rag_failures), 
            ("State Corruption", self.test_state_corruption),
            ("Resource Exhaustion", self.test_resource_limits),
            ("Environment Issues", self.test_environment_issues),
            ("Frontend Error Handling", self.test_frontend_errors)
        ]
        
        for category, test_method in test_methods:
            print(f"\n🔍 Testing: {category}")
            print("-" * 40)
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test category failed: {e}")
                self.results.append({
                    "category": category,
                    "status": "CATEGORY_FAILURE", 
                    "error": str(e)
                })
        
        # Generate report
        self._generate_report()
    
    def test_openai_failures(self):
        """Test OpenAI API failure scenarios"""
        test_cases = [
            ("Invalid API Key", "invalid_api_key_12345"),
            ("Empty API Key", ""),
            ("Malformed API Key", "sk-malformed"),
            ("Rate Limit Key", "rate_limited_key")  # Would need actual rate limited key
        ]
        
        # Store original key securely (don't log this variable)
        original_key = os.environ.get('OPENAI_API_KEY')
        has_original_key = bool(original_key)  # Just track if we had one
        
        for case_name, bad_key in test_cases:
            print(f"  🔬 Testing: {case_name}")
            
            try:
                # Temporarily set bad API key
                os.environ['OPENAI_API_KEY'] = bad_key
                
                # Test direct function call
                response = run_hint_request("Help me find the bus token")
                
                # Check response doesn't contain stack trace
                contains_stack_trace = self._contains_stack_trace(response)
                has_user_friendly_message = self._has_user_friendly_error(response)
                
                result = {
                    "test": f"openai_{case_name.lower().replace(' ', '_')}",
                    "status": "PASS" if not contains_stack_trace and has_user_friendly_message else "FAIL",
                    "response_length": len(response),
                    "contains_stack_trace": contains_stack_trace,
                    "user_friendly": has_user_friendly_message,
                    "response_preview": response[:100]
                }
                self.results.append(result)
                
                print(f"    {'✅' if result['status'] == 'PASS' else '❌'} {case_name}: {result['status']}")
                
            except Exception as e:
                # Even exceptions should be caught gracefully
                result = {
                    "test": f"openai_{case_name.lower().replace(' ', '_')}",
                    "status": "FAIL",
                    "error": str(e),
                    "exception_type": type(e).__name__
                }
                self.results.append(result)
                print(f"    ❌ {case_name}: Uncaught exception - {type(e).__name__}")
            
            finally:
                # Restore original key (if we had one)
                if has_original_key and original_key:
                    os.environ['OPENAI_API_KEY'] = original_key
                elif 'OPENAI_API_KEY' in os.environ:
                    del os.environ['OPENAI_API_KEY']
                    
        # Clear the key from memory as soon as we're done
        if 'original_key' in locals():
            original_key = None
    
    def test_rag_failures(self):
        """Test RAG system failure scenarios"""
        print("  🔬 Testing: RAG Component Failures")
        
        # Test with mocked failures - fixed import path
        with patch('agent.get_direct_hint_with_context') as mock_rag:
            # Simulate RAG returning empty results
            mock_rag.return_value = {"response": "", "context": ""}
            
            try:
                response = run_hint_request("Help me with the alien puzzle")
                
                result = {
                    "test": "rag_empty_results",
                    "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                    "response_preview": response[:100]
                }
                self.results.append(result)
                print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Empty RAG Results: {result['status']}")
                
            except Exception as e:
                result = {
                    "test": "rag_empty_results", 
                    "status": "FAIL",
                    "error": str(e)
                }
                self.results.append(result)
                print(f"    ❌ Empty RAG Results: Uncaught exception")
        
        # Test RAG throwing exceptions - fixed import path
        with patch('agent.get_direct_hint_with_context') as mock_rag:
            mock_rag.side_effect = Exception("Simulated RAG failure")
            
            try:
                response = run_hint_request("Help me with the space station")
                
                result = {
                    "test": "rag_exception",
                    "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                    "response_preview": response[:100]
                }
                self.results.append(result)
                print(f"    {'✅' if result['status'] == 'PASS' else '❌'} RAG Exception: {result['status']}")
                
            except Exception as e:
                result = {
                    "test": "rag_exception",
                    "status": "FAIL", 
                    "error": str(e)
                }
                self.results.append(result)
                print(f"    ❌ RAG Exception: Uncaught exception")
    
    def test_state_corruption(self):
        """Test malformed state and input scenarios"""
        print("  🔬 Testing: State Corruption Scenarios")
        
        # Test input validation limits - should handle gracefully
        
        # Test empty input via API (should get 422 validation error)
        response = self.client.post("/api/chat", 
            json={"user_message": "", "session_id": "test"})
        
        result = {
            "test": "empty_input_api",
            "status": "PASS" if response.status_code == 422 else "FAIL",  # Should reject with 422
            "status_code": response.status_code,
            "response_preview": response.text[:100]
        }
        self.results.append(result)
        print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Empty Input API: {result['status']}")
        
        # Test max allowed input (5000 chars) - should work
        max_input = "Help me " * 625  # ~5000 characters  
        try:
            response = run_hint_request(max_input)
            result = {
                "test": "max_allowed_input",
                "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                "input_length": len(max_input),
                "response_preview": response[:100]
            }
            self.results.append(result)
            print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Max Allowed Input (5K): {result['status']}")
        except Exception as e:
            result = {"test": "max_allowed_input", "status": "FAIL", "error": str(e)}
            self.results.append(result)
            print(f"    ❌ Max Allowed Input: Uncaught exception")
        
        # Test oversized input via API (should get 422 validation error)
        oversized_input = "Attack " * 1000  # ~7K characters
        response = self.client.post("/api/chat", 
            json={"user_message": oversized_input, "session_id": "test"})
        
        result = {
            "test": "oversized_input_api",
            "status": "PASS" if response.status_code == 422 else "FAIL",  # Should reject with 422
            "status_code": response.status_code,
            "input_length": len(oversized_input),
            "response_preview": response.text[:100]
        }
        self.results.append(result)
        print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Oversized Input API (7K): {result['status']}")
        
        # Test direct function with oversized input (should handle gracefully or raise)
        massive_input = "Help me " * 10000  # ~70K characters
        try:
            response = run_hint_request(massive_input)
            result = {
                "test": "massive_input_direct",
                "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                "input_length": len(massive_input),
                "response_preview": response[:100]
            }
            self.results.append(result)
            print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Massive Input Direct (70K): {result['status']}")
        except Exception as e:
            result = {"test": "massive_input_direct", "status": "FAIL", "error": str(e)}
            self.results.append(result)
            print(f"    ❌ Massive Input Direct: Uncaught exception")
        
        # Test special characters and encoding issues
        special_inputs = [
            "🎮💥🚀👾🔥" * 100,  # Emoji overload
            "\x00\x01\x02\x03",   # Control characters
            "SELECT * FROM users; DROP TABLE users;",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "\\n\\r\\t" * 500     # Escape sequence spam
        ]
        
        for i, special_input in enumerate(special_inputs):
            try:
                response = run_hint_request(special_input)
                result = {
                    "test": f"special_input_{i}",
                    "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                    "response_preview": response[:100] if response else "EMPTY"
                }
                self.results.append(result)
                print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Special Input {i}: {result['status']}")
            except Exception as e:
                result = {"test": f"special_input_{i}", "status": "FAIL", "error": str(e)}
                self.results.append(result)
                print(f"    ❌ Special Input {i}: Uncaught exception")
    
    def test_resource_limits(self):
        """Test resource exhaustion scenarios"""
        print("  🔬 Testing: Resource Limit Scenarios")
        
        # Test rapid-fire requests (simulate high load)
        print("    Testing rapid requests...")
        for i in range(5):
            try:
                start_time = time.time()
                response = run_hint_request(f"Quick test {i}")
                duration = time.time() - start_time
                
                result = {
                    "test": f"rapid_request_{i}",
                    "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                    "duration": round(duration, 2),
                    "response_preview": response[:50] if response else "EMPTY"
                }
                self.results.append(result)
                
            except Exception as e:
                result = {"test": f"rapid_request_{i}", "status": "FAIL", "error": str(e)}
                self.results.append(result)
                print(f"    ❌ Rapid Request {i}: Uncaught exception")
            
            # Small delay to avoid overwhelming
            time.sleep(0.1)
        
        print(f"    ✅ Rapid requests completed")
    
    def test_environment_issues(self):
        """Test environment configuration problems"""
        print("  🔬 Testing: Environment Issues")
        
        # Test missing .env file - need to go up to project root
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        env_path = os.path.join(project_root, '.env')
        backup_path = os.path.join(project_root, '.env.backup')
        
        original_dotenv = os.path.exists(env_path)
        if original_dotenv:
            # Temporarily rename .env
            shutil.move(env_path, backup_path)
        
        try:
            response = run_hint_request("Test without .env")
            result = {
                "test": "missing_env_file",
                "status": "PASS" if not self._contains_stack_trace(response) else "FAIL",
                "response_preview": response[:100]
            }
            self.results.append(result)
            print(f"    {'✅' if result['status'] == 'PASS' else '❌'} Missing .env: {result['status']}")
            
        except Exception as e:
            result = {"test": "missing_env_file", "status": "FAIL", "error": str(e)}
            self.results.append(result)
            print(f"    ❌ Missing .env: Uncaught exception")
        
        finally:
            # Restore .env if it existed
            if original_dotenv and os.path.exists(backup_path):
                shutil.move(backup_path, env_path)
    
    
    def test_frontend_errors(self):
        """Test FastAPI error handling"""
        print("  🔬 Testing: Frontend API Error Handling")
        
        # Test API with extra field (api_key should be ignored)
        response = self.client.post("/api/chat", 
            json={"user_message": "test", "api_key": "should_be_ignored"})
        
        result = {
            "test": "api_extra_field_ignored",
            "status": "PASS" if response.status_code in [200, 400, 500] else "FAIL",  # Should process normally
            "status_code": response.status_code,
            "response_preview": response.text[:100]
        }
        self.results.append(result)
        print(f"    {'✅' if result['status'] == 'PASS' else '❌'} API Extra Field Ignored: {result['status']}")
        
        # Test API with malformed request (missing required field)
        response = self.client.post("/api/chat", json={"invalid": "request"})
        
        result = {
            "test": "api_malformed_request",
            "status": "PASS" if response.status_code in [400, 422] else "FAIL",  # Should reject bad requests
            "status_code": response.status_code,
            "response_preview": response.text[:100]
        }
        self.results.append(result)
        print(f"    {'✅' if result['status'] == 'PASS' else '❌'} API Malformed Request: {result['status']}")
        
        # Test API with missing environment variable (simulate no API key)
        original_key = os.environ.get('OPENAI_API_KEY')
        try:
            # Temporarily remove API key
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
            
            response = self.client.post("/api/chat", json={"user_message": "test without api key"})
            
            result = {
                "test": "api_no_env_key",
                "status": "PASS" if response.status_code == 503 else "FAIL",  # Should return 503 for missing key
                "status_code": response.status_code,
                "response_preview": response.text[:100]
            }
            self.results.append(result)
            print(f"    {'✅' if result['status'] == 'PASS' else '❌'} API No Env Key: {result['status']}")
            
        finally:
            # Restore original key
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key
    
    def _contains_stack_trace(self, response: str) -> bool:
        """Check if response contains raw stack trace indicators"""
        stack_trace_indicators = [
            "Traceback (most recent call last):",
            "File \"/", "File \"C:",  # File paths in stack traces
            "line ", " in ",  # Stack trace line indicators
            "AttributeError:", "TypeError:", "ValueError:",  # Common exception types
            "KeyError:", "IndexError:", "NameError:",
            "raise Exception", "Exception:", "Error:",
            "site-packages/", "python/lib/",  # Package paths
            "__traceback__", "tb_frame"
        ]
        
        response_lower = response.lower()
        return any(indicator.lower() in response_lower for indicator in stack_trace_indicators)
    
    def _has_user_friendly_error(self, response: str) -> bool:
        """Check if response has user-friendly error handling"""
        friendly_indicators = [
            "sorry", "error occurred", "try again",
            "something went wrong", "unable to", "cannot",
            "issue", "problem", "zelda", "assistant",
            "help", "clarification", "specific"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in friendly_indicators)
    
    def _generate_report(self):
        """Generate comprehensive error testing report"""
        print("\n" + "=" * 60)
        print("🧪 ERROR INJECTION TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.get("status") == "PASS"])
        failed = len([r for r in self.results if r.get("status") == "FAIL"])
        
        print(f"📊 Summary: {passed}/{total_tests} tests passed ({round(passed/total_tests*100, 1)}%)")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print(f"\n⚠️  FAILED TESTS (Raw stack traces may be exposed!):")
            for result in self.results:
                if result.get("status") == "FAIL":
                    print(f"  - {result['test']}: {result.get('error', 'See details above')}")
        
        # Generate timestamp and save to results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        filename = os.path.join(results_dir, f"error_injection_results_{timestamp}.log")
        
        print(f"\n📄 Full results saved to: {filename}")
        
        # Save detailed log with timestamp
        with open(filename, "w") as f:
            f.write(f"Error Injection Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for result in self.results:
                test_name = result.get('test', result.get('category', 'unknown_test'))
                f.write(f"Test: {test_name}\n")
                f.write(f"Status: {result.get('status', 'UNKNOWN')}\n")
                for key, value in result.items():
                    if key not in ['test', 'status', 'category']:
                        f.write(f"  {key}: {value}\n")
                f.write("\n")

def main():
    """Main entry point"""
    print("🚀 Thudbot Error Injection Testing")
    print("This will systematically test error scenarios to ensure graceful handling")
    print("=" * 60)
    
    # Load environment from project root
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=os.path.join(project_root, ".env"), override=True)
    except ImportError:
        print("⚠️  Warning: dotenv not available")
    
    tester = ErrorInjectionTester()
    tester.run_all_error_tests()

if __name__ == "__main__":
    main()
