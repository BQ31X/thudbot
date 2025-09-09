#!/usr/bin/env python3
"""
Security Test Runner for Thudbot

This script runs security tests to validate that the application is hardened
against common vulnerabilities before production deployment.
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path for test imports
sys.path.insert(0, os.path.dirname(__file__))

# Add src to path for imports (same pattern as regression runner)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'thudbot_core'))

try:
    # Test that we can import the API for testing
    from api import app
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root with the venv activated")
    sys.exit(1)

class SecurityTestRunner:
    """Runs security tests and generates vulnerability reports"""
    
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def run_all_tests(self):
        """Run all security tests and generate report"""
        print(f"🔒 Starting Security Test Suite - {self.timestamp}")
        print("=" * 60)
        
        # Import and run each test
        try:
            from test_security import (
                test_cors_configuration,
                test_api_key_not_in_request_body,
                test_environment_not_polluted,
                test_cors_methods_restricted,
                test_session_hijacking_protection
            )
        except ImportError as e:
            print(f"❌ Failed to import security tests: {e}")
            print("Make sure test_security.py is in the same directory")
            sys.exit(1)
        
        tests = [
            ("CORS Configuration", test_cors_configuration),
            ("API Key Exposure", test_api_key_not_in_request_body),
            ("Environment Pollution", test_environment_not_polluted),
            ("HTTP Methods", test_cors_methods_restricted),
            ("Session Security", test_session_hijacking_protection)
        ]
        
        print(f"📋 Running {len(tests)} security tests")
        
        # Run each test
        for i, (test_name, test_func) in enumerate(tests, 1):
            print(f"\n🔍 {i}/{len(tests)}: {test_name}")
            result = self._run_single_test(test_name, test_func)
            self.results.append(result)
            
        # Generate report
        report_file = self._generate_security_report()
        self._print_summary()
        
        return report_file
        
    def _run_single_test(self, test_name, test_func):
        """Run a single security test and capture results"""
        start_time = time.time()
        
        try:
            test_func()
            status = "✅ PASS"
            error = None
            print(f"   ✅ PASS")
        except Exception as e:
            status = "❌ FAIL"
            error = str(e)
            print(f"   ❌ FAIL: {error}")
            
        duration = time.time() - start_time
        print(f"   Duration: {duration:.2f}s")
        
        return {
            "test_name": test_name,
            "status": status,
            "error": error,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    def _generate_security_report(self):
        """Generate human-readable security report"""
        results_dir = Path(__file__).parent / "results" 
        results_dir.mkdir(exist_ok=True)
        
        report_file = results_dir / f"security_report_{self.timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"🔒 THUDBOT SECURITY TEST REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            
            passed = sum(1 for r in self.results if "PASS" in r["status"])
            failed = len(self.results) - passed
            
            f.write(f"SUMMARY: {passed} passed, {failed} failed\n\n")
            
            if failed > 0:
                f.write("🚨 SECURITY VULNERABILITIES DETECTED:\n")
                for result in self.results:
                    if "FAIL" in result["status"]:
                        f.write(f"- {result['test_name']}: {result['error']}\n")
                f.write("\n")
            
            f.write("DETAILED RESULTS:\n")
            f.write("-" * 30 + "\n")
            for result in self.results:
                f.write(f"{result['status']} {result['test_name']}\n")
                if result['error']:
                    f.write(f"   Error: {result['error']}\n")
                f.write(f"   Duration: {result['duration']:.2f}s\n")
                f.write(f"   Time: {result['timestamp']}\n\n")
                
        print(f"\n📄 Security report saved: {report_file}")
        return report_file
    
    def _print_summary(self):
        """Print summary to console"""
        print("\n" + "=" * 60)
        print("🔒 SECURITY TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if "PASS" in r["status"])
        failed = len(self.results) - passed
        total_duration = sum(r["duration"] for r in self.results)
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total Time: {total_duration:.2f}s")
        
        if failed > 0:
            print(f"\n🚨 {failed} SECURITY VULNERABILITIES DETECTED!")
            print("   Review the detailed report before deploying to production.")
        else:
            print(f"\n🎉 All security tests passed! Ready for production.")

def main():
    """Main entry point"""
    print("🔒 Thudbot Security Test Suite")
    print("Validating application security before production deployment")
    print()
    
    # Check environment
    env_setting = os.getenv("ENV", "dev")
    print(f"🔧 Environment: {env_setting}")
    
    if env_setting == "dev":
        print("ℹ️  Running in development mode - some tests will check dev-specific behavior")
    else:
        print("🏭 Running in production mode - testing production security settings")
    
    print()
    
    # Run tests
    runner = SecurityTestRunner()
    report_file = runner.run_all_tests()
    
    return report_file

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Security tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error running security tests: {e}")
        sys.exit(1)
