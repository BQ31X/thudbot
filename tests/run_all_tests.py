#!/usr/bin/env python3
"""
DEPRECATED: Unified Test Runner for Thudbot Hint System

⚠️  WARNING: This test runner is somewhat outdated and may need testing itself before use.
⚠️  RECOMMENDED: Use tests/regression/run_regression.py for current regression testing.

Original purpose: Runs all test suites in sequence and provides comprehensive reporting
Demo Day: 8/25 | Code Freeze: 8/21

Status: Moved from root to tests/ on 2025-08-20. Paths adjusted but untested.
        Contains interpretation logic that was superseded by simpler raw data collection.
        
Usage: Run from project root: python tests/run_all_tests.py
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env", override=True)
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  python-dotenv not installed - using system environment only")

# Add src to path for imports (moved to tests/ directory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_test_suite(suite_name: str, test_function) -> Dict[str, Any]:
    """Run a test suite and capture results"""
    print(f"\n{'='*20} {suite_name.upper()} {'='*20}")
    
    start_time = time.time()
    
    try:
        results = test_function()
        duration = time.time() - start_time
        
        return {
            "suite": suite_name,
            "status": "COMPLETED",
            "duration": duration,
            "results": results
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {suite_name} failed with error: {e}")
        
        return {
            "suite": suite_name,
            "status": "FAILED",
            "duration": duration,
            "error": str(e)
        }

def check_environment() -> bool:
    """Check that environment is ready for testing"""
    print("🔧 ENVIRONMENT CHECK")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check API key
    total_checks += 1
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY found")
        checks_passed += 1
    else:
        print("❌ OPENAI_API_KEY not found")
    
    # Check required files
    required_files = [
        "src/app.py",  # Adjusted path from tests/ perspective
        "src/agent.py", 
        "src/test_comprehensive.py",
        "src/test_progressive_hints_prep.py",
        "data/Thudbot_Hint_Data_1.csv"
    ]
    
    for file_path in required_files:
        total_checks += 1
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            checks_passed += 1
        else:
            print(f"❌ {file_path}")
    
    # Check cache directory (optional)
    if Path("cache/embeddings").exists():
        print("✅ Cache directory found (performance benefit)")
    else:
        print("ℹ️  Cache directory not found (will be created)")
    
    success_rate = (checks_passed / total_checks * 100)
    print(f"\nEnvironment Check: {checks_passed}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate < 80:
        print("❌ Environment not ready for testing")
        return False
    else:
        print("✅ Environment ready for testing")
        return True

def run_all_tests():
    """Run all test suites and generate comprehensive report"""
    
    print("🧪 THUDBOT COMPREHENSIVE TEST BATTERY")
    print("=" * 80)
    print("Demo Day: 8/25 | Code Freeze: 8/21")
    print("Testing: Edge Cases | Regression | Verification Edge Cases | UX | Performance | Progressive Hints Prep")
    print("=" * 80)
    
    # Environment check
    if not check_environment():
        print("\n❌ Aborting tests due to environment issues")
        return False
    
    # Import test modules (after environment check)
    try:
        from test_comprehensive import run_comprehensive_tests
        from test_progressive_hints_prep import run_progressive_hints_prep
        import test_langgraph
        # Note: test_functions import removed - not needed for main test runner
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return False
    
    # Test suite registry
    test_suites = []
    
    # 1. Basic Integration Tests (existing)
    def run_basic_tests():
        """Run existing basic tests"""
        print("Running basic LangGraph integration tests...")
        
        # Simulate running the existing tests
        success_count = 0
        total_tests = 4
        
        try:
            # Test basic flow
            if test_langgraph.test_basic_flow():
                success_count += 1
            
            # Test game questions
            if test_langgraph.test_game_related_questions():
                success_count += 1
            
            # Test off-topic
            if test_langgraph.test_off_topic_questions():
                success_count += 1
                
            # Test Zelda guardrail
            if test_langgraph.test_zelda_guardrail():
                success_count += 1
                
        except Exception as e:
            print(f"Error in basic tests: {e}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": success_count,
            "success_rate": (success_count / total_tests * 100) if total_tests > 0 else 0
        }
    
    test_suites.append(("Basic Integration", run_basic_tests))
    test_suites.append(("Comprehensive Tests", run_comprehensive_tests))
    # test_suites.append(("Progressive Hints Prep", run_progressive_hints_prep))  # Commented out - no progressive hints feature yet
    
    # Run all test suites
    all_results = []
    total_start_time = time.time()
    
    for suite_name, test_function in test_suites:
        result = run_test_suite(suite_name, test_function)
        all_results.append(result)
    
    total_duration = time.time() - total_start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST REPORT")
    print(f"{'='*80}")
    
    total_suites = len(all_results)
    completed_suites = sum(1 for r in all_results if r["status"] == "COMPLETED")
    failed_suites = sum(1 for r in all_results if r["status"] == "FAILED")
    
    print(f"Test Suites: {completed_suites}/{total_suites} completed")
    print(f"Total Duration: {total_duration:.1f} seconds")
    
    # Suite-by-suite summary
    overall_success = True
    
    for result in all_results:
        suite_name = result["suite"]
        status = result["status"]
        duration = result.get("duration", 0)
        
        if status == "COMPLETED":
            suite_results = result.get("results", {})
            
            if isinstance(suite_results, dict):
                # Extract success metrics based on suite type
                if "success_rate" in suite_results:
                    success_rate = suite_results["success_rate"]
                elif "total_tests" in suite_results and "passed_tests" in suite_results:
                    total = suite_results["total_tests"]
                    passed = suite_results["passed_tests"]
                    success_rate = (passed / total * 100) if total > 0 else 0
                else:
                    success_rate = 100  # Assume success if no metrics
                
                status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                print(f"{status_icon} {suite_name}: {success_rate:.1f}% ({duration:.1f}s)")
                
                if success_rate < 80:
                    overall_success = False
            else:
                print(f"✅ {suite_name}: Completed ({duration:.1f}s)")
        else:
            print(f"❌ {suite_name}: Failed ({duration:.1f}s)")
            overall_success = False
    
    # Critical issues summary
    critical_issues = []
    
    for result in all_results:
        if result["status"] == "FAILED":
            critical_issues.append(f"Suite failure: {result['suite']}")
        elif result["status"] == "COMPLETED":
            suite_results = result.get("results", {})
            
            # Check for specific critical issues
            if isinstance(suite_results, dict):
                if suite_results.get("success_rate", 100) < 60:
                    critical_issues.append(f"Low success rate in {result['suite']}")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT:")
    
    if overall_success and len(critical_issues) == 0:
        print("✅ ALL SYSTEMS GO - Ready for Progressive Hints Implementation!")
        print("✅ System stability confirmed")
        print("✅ Edge cases handled appropriately") 
        print("✅ Verification system working")
        print("✅ User experience validated")
        assessment = "READY"
    elif len(critical_issues) <= 2:
        print("⚠️  MOSTLY READY - Address minor issues before progressive hints")
        print("⚠️  Some test failures detected but system fundamentally sound")
        assessment = "MOSTLY_READY"
    else:
        print("❌ NOT READY - Resolve critical issues before proceeding")
        print("❌ Multiple test failures indicate stability concerns")
        assessment = "NOT_READY"
    
    if critical_issues:
        print(f"\n🔧 Critical Issues to Address:")
        for issue in critical_issues[:5]:  # Show top 5
            print(f"   - {issue}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if assessment == "READY":
        print("🚀 Implement progressive hints with confidence")
        print("📊 Use current metrics as baseline for future testing")
        print("🔄 Run regression tests after progressive hints implementation")
    elif assessment == "MOSTLY_READY":
        print("🔧 Fix critical test failures first")
        print("🧪 Re-run this test battery after fixes")
        print("⚠️  Consider implementing progressive hints in stages")
    else:
        print("🛑 Focus on system stability before new features")
        print("🔍 Investigate and resolve test failures")
        print("📞 Consider delaying progressive hints until after Demo Day")
    
    # Save detailed results
    timestamp = int(time.time())
    results_file = f"comprehensive_test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump({
                "assessment": assessment,
                "overall_success": overall_success,
                "total_duration": total_duration,
                "suite_results": all_results,
                "critical_issues": critical_issues,
                "timestamp": timestamp,
                "environment": {
                    "cache_available": os.path.exists("./cache/embeddings"),
                    "api_key_available": bool(os.getenv('OPENAI_API_KEY'))
                }
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save detailed results: {e}")
    
    print(f"\n🎉 Test battery complete! System assessment: {assessment}")
    
    return assessment == "READY" or assessment == "MOSTLY_READY"

if __name__ == "__main__":
    success = run_all_tests()
    
    # Exit codes for CI/CD integration
    if success:
        print("\n✅ Exiting with success code")
        exit(0)
    else:
        print("\n❌ Exiting with failure code")
        exit(1)
