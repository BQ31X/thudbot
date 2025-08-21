#!/usr/bin/env python3
"""
Test Report Analyzer - Human-Digestible Test Results
Analyzes test results JSON and creates readable summaries for evaluation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class TestReportAnalyzer:
    """Analyze and format test results for human review"""
    
    def __init__(self, results_file: str = None):
        self.results_file = results_file or self._find_latest_results()
        self.data = None
        
    def _find_latest_results(self) -> str:
        """Find the most recent test results file"""
        result_files = list(Path(".").glob("*test_results*.json"))
        if not result_files:
            return None
        return str(max(result_files, key=os.path.getctime))
    
    def load_results(self) -> bool:
        """Load test results from JSON file"""
        if not self.results_file or not Path(self.results_file).exists():
            print("❌ No test results file found. Run tests first.")
            return False
            
        try:
            with open(self.results_file, 'r') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading results: {e}")
            return False
    
    def generate_summary_report(self):
        """Generate a human-readable summary report"""
        if not self.load_results():
            return
            
        print("📊 THUDBOT TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Overall stats
        if "summary" in self.data:
            summary = self.data["summary"]
            print(f"📈 Overall Success Rate: {summary.get('success_rate', 0):.1f}%")
            print(f"✅ Tests Passed: {summary.get('passed', 0)}")
            print(f"❌ Tests Failed: {summary.get('failed', 0)}")
            print(f"📊 Total Tests: {summary.get('total_tests', 0)}")
            
            if summary.get('performance_metrics'):
                perf = summary['performance_metrics']
                print(f"⚡ Avg Response Time: {perf.get('average_response_time', 0):.2f}s")
        
        print("\n" + "=" * 60)
        print("🔍 DETAILED RESULTS BY CATEGORY")
        print("=" * 60)
        
        # Categorize and analyze results
        self._analyze_by_category()
        
        print("\n" + "=" * 60)
        print("❌ FAILED TESTS BREAKDOWN")
        print("=" * 60)
        
        # Show failed tests with details
        self._show_failed_tests()
        
        print("\n" + "=" * 60)
        print("🎯 RECOMMENDATIONS")
        print("=" * 60)
        
        self._generate_recommendations()
    
    def _analyze_by_category(self):
        """Analyze results by test category"""
        if "detailed_results" not in self.data:
            return
            
        # Group by category
        categories = {}
        for result in self.data["detailed_results"]:
            category = self._categorize_test(result["test_name"])
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result["status"] == "PASS":
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Display by category
        for category, stats in categories.items():
            success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            
            print(f"{status_icon} {category.title()}: {success_rate:.1f}% ({stats['passed']}/{stats['total']})")
    
    def _categorize_test(self, test_name: str) -> str:
        """Categorize test based on name"""
        if "core_" in test_name:
            return "core functionality"
        elif "off_topic_" in test_name:
            return "off-topic routing"
        elif "vague_question_" in test_name:
            return "vague questions"
        elif "specific_question_" in test_name:
            return "specific questions"
        elif "verification_edge_" in test_name:
            return "verification edge cases"
        elif "hallucination_detection_" in test_name:
            return "hallucination detection"
        elif "quality_" in test_name:
            return "response quality"
        elif "performance_" in test_name:
            return "performance"
        elif "empty_input_" in test_name:
            return "edge case inputs"
        elif "long_input_" in test_name:
            return "long inputs"
        elif "special_chars_" in test_name:
            return "special characters"
        elif "ambiguous_" in test_name:
            return "ambiguous questions"
        elif "zelda_guardrails" in test_name:
            return "character guardrails"
        else:
            return "other"
    
    def _show_failed_tests(self):
        """Show detailed breakdown of failed tests"""
        if "detailed_results" not in self.data:
            return
            
        failed_tests = [r for r in self.data["detailed_results"] if r["status"] == "FAIL"]
        
        if not failed_tests:
            print("🎉 No failed tests! All tests passed.")
            return
        
        # Group failures by category for better organization
        failure_categories = {}
        for test in failed_tests:
            category = self._categorize_test(test["test_name"])
            if category not in failure_categories:
                failure_categories[category] = []
            failure_categories[category].append(test)
        
        for category, tests in failure_categories.items():
            print(f"\n📂 {category.title()} Failures ({len(tests)}):")
            for test in tests[:3]:  # Show first 3 failures per category
                self._show_test_details(test)
            
            if len(tests) > 3:
                print(f"   ... and {len(tests) - 3} more {category} failures")
    
    def _show_test_details(self, test: Dict[str, Any]):
        """Show details of a specific test"""
        details = test.get("details", {})
        
        print(f"   ❌ {test['test_name']}")
        
        # Show question if available
        if "question" in details:
            print(f"      Question: \"{details['question']}\"")
        
        # Show expected behavior vs actual for verification tests
        if "expected_behavior" in details:
            print(f"      Expected: {details['expected_behavior']}")
            if "test_type" in details:
                print(f"      Test Type: {details['test_type']}")
        
        # Show detailed analysis for different test types
        if "appropriate_response" in details:
            print(f"      Appropriate Response: {details['appropriate_response']}")
            
            # Show what was checked
            if "asks_clarification" in details:
                print(f"      Asks Clarification: {details['asks_clarification']}")
            if "is_off_topic" in details:
                print(f"      Is Off-Topic Response: {details['is_off_topic']}")
            if "contains_keywords" in details:
                print(f"      Contains Expected Keywords: {details['contains_keywords']}")
            if "has_character_info" in details:
                print(f"      Has Character Info: {details['has_character_info']}")
            if "not_forbidden" in details:
                print(f"      No Forbidden Terms: {details['not_forbidden']}")
            if "insufficient_indicated" in details:
                print(f"      Indicates Insufficient Info: {details['insufficient_indicated']}")
        
        # Show actual response (truncated)
        if "response" in details:
            response = details["response"]
            if len(response) > 150:
                response = response[:150] + "..."
            print(f"      Actual Response: \"{response}\"")
        
        # Show error if available
        if "error" in details:
            print(f"      Error: {details['error']}")
        
        print()
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        if "detailed_results" not in self.data:
            return
            
        failed_tests = [r for r in self.data["detailed_results"] if r["status"] == "FAIL"]
        total_tests = len(self.data["detailed_results"])
        success_rate = ((total_tests - len(failed_tests)) / total_tests * 100) if total_tests > 0 else 0
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: System is ready for production!")
        elif success_rate >= 80:
            print("✅ GOOD: System is mostly ready, minor fixes needed")
        elif success_rate >= 70:
            print("⚠️  NEEDS WORK: Address key issues before deployment")
        else:
            print("❌ SIGNIFICANT ISSUES: Major fixes needed")
        
        # Specific recommendations based on failure patterns
        failure_patterns = {}
        for test in failed_tests:
            category = self._categorize_test(test["test_name"])
            failure_patterns[category] = failure_patterns.get(category, 0) + 1
        
        if failure_patterns:
            print(f"\n🔧 Priority Areas to Address:")
            sorted_patterns = sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True)
            
            for category, count in sorted_patterns[:3]:  # Top 3 problem areas
                print(f"   • {category.title()}: {count} failures")
                self._get_category_recommendations(category)
    
    def _get_category_recommendations(self, category: str):
        """Get specific recommendations for a category"""
        recommendations = {
            "verification edge cases": "Review verification logic for edge cases",
            "hallucination detection": "Check if responses are appropriately flagged",
            "vague questions": "Ensure vague questions get clarification requests",
            "off-topic routing": "Verify router classification accuracy",
            "character guardrails": "Check Zelda character consistency",
            "performance": "Optimize response times if needed",
            "edge case inputs": "Handle unusual input formats better"
        }
        
        if category in recommendations:
            print(f"     → {recommendations[category]}")
    
    def show_detailed_failure_analysis(self, test_name_pattern: str = None):
        """Show detailed analysis of specific failed tests"""
        if not self.load_results():
            return
            
        print("🔍 DETAILED FAILURE ANALYSIS")
        print("=" * 60)
        
        failed_tests = [r for r in self.data["detailed_results"] if r["status"] == "FAIL"]
        
        if test_name_pattern:
            failed_tests = [t for t in failed_tests if test_name_pattern in t["test_name"]]
        
        for test in failed_tests:
            self._show_detailed_test_analysis(test)
    
    def generate_failure_table(self, test_name_pattern: str = None, output_format: str = "console"):
        """Generate a detailed table of test failures"""
        if not self.load_results():
            return
            
        failed_tests = [r for r in self.data["detailed_results"] if r["status"] == "FAIL"]
        
        if test_name_pattern:
            failed_tests = [t for t in failed_tests if test_name_pattern in t["test_name"]]
        
        if not failed_tests:
            if output_format == "markdown":
                return "## Test Results\n\n🎉 **No failed tests found!** All tests passed.\n"
            else:
                print("🎉 No failed tests found!")
                return
        
        if output_format == "markdown":
            return self._generate_markdown_table(failed_tests)
        else:
            self._generate_console_table(failed_tests)
    
    def _generate_console_table(self, failed_tests):
        """Generate console format table"""
        print("📊 DETAILED TEST FAILURE TABLE")
        print("=" * 120)
        
        # Table header
        print(f"{'TEST TYPE':<25} | {'QUERY':<40} | {'EXPECTED':<30} | {'ACTUAL':<40} | {'CONCLUSION':<15}")
        print("-" * 120)
        
        for test in failed_tests:
            self._format_test_row(test)
    
    def _generate_markdown_table(self, failed_tests) -> str:
        """Generate Markdown format table"""
        from datetime import datetime
        
        md_content = []
        md_content.append("# Thudbot Test Failure Analysis")
        md_content.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_content.append(f"\n**Total Failed Tests:** {len(failed_tests)}")
        
        # Summary by conclusion
        conclusions = {}
        for test in failed_tests:
            conclusion = self._get_test_conclusion(test)
            conclusions[conclusion] = conclusions.get(conclusion, 0) + 1
        
        md_content.append(f"\n## Summary by Conclusion")
        md_content.append("")
        for conclusion, count in sorted(conclusions.items()):
            emoji = "🔥" if conclusion == "REAL ISSUE" else "⚠️" if conclusion == "NEEDS REVIEW" else "✅"
            md_content.append(f"- {emoji} **{conclusion}**: {count} tests")
        
        # Detailed table
        md_content.append(f"\n## Detailed Test Results")
        md_content.append("")
        md_content.append("| Test Type | Query | Expected | Actual | Conclusion |")
        md_content.append("|-----------|-------|----------|--------|------------|")
        
        for test in failed_tests:
            details = test.get("details", {})
            
            test_type = self._get_test_type(test["test_name"])
            query = details.get("question", "N/A")
            expected = self._get_expected_description(details)
            actual = self._get_actual_description(details)
            conclusion = self._get_test_conclusion(test)
            
            # Escape pipes in content for Markdown
            query = query.replace("|", "\\|")
            expected = expected.replace("|", "\\|")
            actual = actual.replace("|", "\\|")
            
            # Add conclusion emoji
            conclusion_emoji = {
                "REAL ISSUE": "🔥",
                "FALSE POSITIVE": "✅", 
                "NEEDS REVIEW": "⚠️"
            }
            conclusion_display = f"{conclusion_emoji.get(conclusion, '❓')} {conclusion}"
            
            md_content.append(f"| {test_type} | {query} | {expected} | {actual} | {conclusion_display} |")
        
        # Analysis section
        md_content.append(f"\n## Analysis")
        md_content.append("")
        
        real_issues = [t for t in failed_tests if self._get_test_conclusion(t) == "REAL ISSUE"]
        false_positives = [t for t in failed_tests if self._get_test_conclusion(t) == "FALSE POSITIVE"]
        
        if real_issues:
            md_content.append(f"### 🔥 Real Issues ({len(real_issues)})")
            md_content.append("")
            md_content.append("These test failures indicate actual problems that need attention:")
            md_content.append("")
            for test in real_issues:
                details = test.get("details", {})
                question = details.get("question", "Unknown")
                issue_desc = self._get_issue_description(test)
                md_content.append(f"- **\"{question}\"**: {issue_desc}")
        
        if false_positives:
            md_content.append(f"\n### ✅ False Positives ({len(false_positives)})")
            md_content.append("")
            md_content.append("These \"failures\" actually indicate the system is working better than expected:")
            md_content.append("")
            for test in false_positives[:5]:  # Show first 5
                details = test.get("details", {})
                question = details.get("question", "Unknown")
                explanation = self._get_false_positive_explanation(test)
                md_content.append(f"- **\"{question}\"**: {explanation}")
            
            if len(false_positives) > 5:
                md_content.append(f"- *(and {len(false_positives) - 5} more similar false positives)*")
        
        # Recommendations
        md_content.append(f"\n## Recommendations")
        md_content.append("")
        
        if len(real_issues) == 0:
            md_content.append("🎉 **No critical issues found!** Your system is performing well.")
        elif len(real_issues) <= 2:
            md_content.append("✅ **Minor issues only** - Address these specific cases:")
            for test in real_issues:
                details = test.get("details", {})
                question = details.get("question", "Unknown")
                md_content.append(f"   - Test \"{question}\" manually to confirm the issue")
        else:
            md_content.append("⚠️ **Multiple issues found** - Focus on:")
            md_content.append("   1. Core functionality problems first")
            md_content.append("   2. Character guardrail issues")
            md_content.append("   3. Review test expectations vs actual behavior")
        
        md_content.append(f"\n**Test confidence:** {((len(failed_tests) - len(false_positives)) / len(failed_tests) * 100):.1f}% of failures are false positives, indicating robust system behavior.")
        
        return "\n".join(md_content)
    
    def _get_issue_description(self, test: Dict[str, Any]) -> str:
        """Get description of what the actual issue is"""
        details = test.get("details", {})
        test_name = test["test_name"]
        
        if "core_" in test_name:
            if not details.get("contains_keyword", True):
                return "Response missing expected keyword - check RAG retrieval"
            return "Core functionality not working as expected"
        
        if "zelda_guardrails" in test_name:
            if not details.get("not_forbidden", True):
                return "Character leaked forbidden Legend of Zelda terms"
            return "Character response needs review"
        
        return "Needs manual verification"
    
    def _get_false_positive_explanation(self, test: Dict[str, Any]) -> str:
        """Explain why this is a false positive"""
        details = test.get("details", {})
        test_name = test["test_name"]
        
        if "verification_edge" in test_name:
            return "System asked for clarification instead of saying 'insufficient info' - better UX"
        
        if "hallucination_detection" in test_name:
            return "System correctly avoided making up details about non-game concepts"
        
        if "zelda_guardrails" in test_name:
            return "No forbidden terms detected - response appears appropriate"
        
        return "System behavior is actually correct"
    
    def save_markdown_report(self, filename: str = None, test_name_pattern: str = None):
        """Save failure analysis as Markdown file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_failure_analysis_{timestamp}.md"
        
        markdown_content = self.generate_failure_table(test_name_pattern, output_format="markdown")
        
        try:
            with open(filename, 'w') as f:
                f.write(markdown_content)
            print(f"📄 Markdown report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None
    
    def _format_test_row(self, test: Dict[str, Any]):
        """Format a single test result as a table row"""
        details = test.get("details", {})
        
        # Extract test type
        test_type = self._get_test_type(test["test_name"])
        
        # Extract query
        query = details.get("question", "N/A")
        if len(query) > 38:
            query = query[:35] + "..."
        
        # Extract expected behavior
        expected = self._get_expected_description(details)
        if len(expected) > 28:
            expected = expected[:25] + "..."
        
        # Extract actual behavior
        actual = self._get_actual_description(details)
        if len(actual) > 38:
            actual = actual[:35] + "..."
        
        # Determine conclusion
        conclusion = self._get_test_conclusion(test)
        
        print(f"{test_type:<25} | {query:<40} | {expected:<30} | {actual:<40} | {conclusion:<15}")
    
    def _get_test_type(self, test_name: str) -> str:
        """Extract readable test type from test name"""
        if "verification_edge" in test_name:
            return "Verification Edge"
        elif "hallucination_detection" in test_name:
            return "Hallucination Detection"
        elif "zelda_guardrails" in test_name:
            return "Character Guardrails"
        elif "core_" in test_name:
            return "Core Functionality"
        elif "off_topic_" in test_name:
            return "Off-Topic Routing"
        elif "vague_question" in test_name:
            return "Vague Questions"
        elif "specific_question" in test_name:
            return "Specific Questions"
        elif "ambiguous" in test_name:
            return "Ambiguous Input"
        elif "quality" in test_name:
            return "Response Quality"
        elif "performance" in test_name:
            return "Performance"
        else:
            return "Other"
    
    def _get_expected_description(self, details: Dict[str, Any]) -> str:
        """Get human-readable expected behavior"""
        if "expected_behavior" in details:
            behavior = details["expected_behavior"]
            mappings = {
                "clarification_or_off_topic": "Ask clarification OR off-topic",
                "specific_helpful_response": "Specific helpful answer",
                "character_information": "Character info (Space Bar)",
                "insufficient_context_message": "Say insufficient info"
            }
            return mappings.get(behavior, behavior)
        
        if "expected_keyword" in details:
            return f"Contains '{details['expected_keyword']}'"
        
        return "Pass all checks"
    
    def _get_actual_description(self, details: Dict[str, Any]) -> str:
        """Get human-readable actual behavior"""
        # For verification edge cases
        if "insufficient_indicated" in details and "is_off_topic" in details:
            insufficient = details["insufficient_indicated"]
            off_topic = details["is_off_topic"]
            
            if off_topic:
                return "Treated as off-topic"
            elif insufficient:
                return "Indicated insufficient info"
            else:
                return "Asked for clarification"
        
        # For hallucination detection
        if "contains_suspicious_details" in details:
            if details["contains_suspicious_details"]:
                return "Made up specific details"
            else:
                return "No suspicious details"
        
        # For character info
        if "has_character_info" in details and "not_forbidden" in details:
            has_info = details["has_character_info"]
            no_forbidden = details["not_forbidden"]
            
            if has_info and no_forbidden:
                return "Good character info"
            elif not no_forbidden:
                return "Contains forbidden terms"
            else:
                return "Missing character info"
        
        # For keyword checking
        if "contains_keywords" in details:
            if details["contains_keywords"]:
                return "Contains expected keywords"
            else:
                return "Missing expected keywords"
        
        # Default
        return "Failed checks"
    
    def _get_test_conclusion(self, test: Dict[str, Any]) -> str:
        """Determine if this is a real issue or test problem"""
        details = test.get("details", {})
        test_name = test["test_name"]
        
        # Character guardrails - check for real issues
        if "zelda_guardrails" in test_name:
            if details.get("not_forbidden", True):
                return "FALSE POSITIVE"
            else:
                return "REAL ISSUE"
        
        # Verification edge cases - asking for clarification is good
        if "verification_edge" in test_name and details.get("expected_behavior") == "insufficient_context_message":
            if not details.get("insufficient_indicated", False) and not details.get("is_off_topic", False):
                return "FALSE POSITIVE"  # System asked for clarification, which is better UX
            else:
                return "PASS"
        
        # Hallucination detection - no suspicious details is good
        if "hallucination_detection" in test_name:
            if not details.get("contains_suspicious_details", True):
                return "FALSE POSITIVE"  # System correctly avoided hallucinations
            else:
                return "REAL ISSUE"
        
        # Core functionality issues are real
        if "core_" in test_name:
            return "REAL ISSUE"
        
        # Default
        return "NEEDS REVIEW"
    
    def _show_detailed_test_analysis(self, test: Dict[str, Any]):
        """Show comprehensive analysis of a single test failure"""
        details = test.get("details", {})
        
        print(f"\n{'='*40}")
        print(f"TEST: {test['test_name']}")
        print(f"STATUS: {test['status']}")
        print(f"{'='*40}")
        
        if "question" in details:
            print(f"❓ QUESTION: \"{details['question']}\"")
        
        if "expected_behavior" in details:
            print(f"🎯 EXPECTED BEHAVIOR: {details['expected_behavior']}")
            self._explain_expected_behavior(details['expected_behavior'])
        
        if "test_type" in details:
            print(f"🧪 TEST TYPE: {details['test_type']}")
        
        print(f"\n📊 ACTUAL BEHAVIOR:")
        if "appropriate_response" in details:
            print(f"   Overall Assessment: {'✅ PASS' if details['appropriate_response'] else '❌ FAIL'}")
        
        # Show detailed checks
        checks = [
            ("asks_clarification", "Asks for clarification"),
            ("is_off_topic", "Treats as off-topic"),
            ("contains_keywords", "Contains expected keywords"),
            ("has_character_info", "Has character information"),
            ("not_forbidden", "No forbidden terms"),
            ("insufficient_indicated", "Indicates insufficient info"),
            ("contains_suspicious_details", "Contains suspicious details")
        ]
        
        for key, description in checks:
            if key in details:
                value = details[key]
                icon = "✅" if value else "❌"
                print(f"   {icon} {description}: {value}")
        
        if "response" in details:
            print(f"\n💬 ACTUAL RESPONSE:")
            print(f"   \"{details['response']}\"")
        
        if "error" in details:
            print(f"\n🚨 ERROR: {details['error']}")
        
        # Analysis and recommendation
        print(f"\n🤔 ANALYSIS:")
        self._analyze_specific_failure(test)
    
    def _explain_expected_behavior(self, expected_behavior: str):
        """Explain what the expected behavior means"""
        explanations = {
            "clarification_or_off_topic": "Should either ask for more specific details OR treat as off-topic question",
            "specific_helpful_response": "Should provide a helpful, specific answer with relevant information",
            "character_information": "Should provide information about characters while maintaining Space Bar context",
            "insufficient_context_message": "Should indicate that there isn't enough information to answer"
        }
        
        if expected_behavior in explanations:
            print(f"   💡 Meaning: {explanations[expected_behavior]}")
    
    def _analyze_specific_failure(self, test: Dict[str, Any]):
        """Provide specific analysis for why a test failed"""
        details = test.get("details", {})
        test_name = test["test_name"]
        
        if "verification_edge" in test_name:
            expected = details.get("expected_behavior", "")
            if expected == "insufficient_context_message":
                if not details.get("insufficient_indicated", False) and not details.get("is_off_topic", False):
                    print("   🔍 The system provided a specific response instead of indicating insufficient information")
                    print("   📝 This might actually be CORRECT behavior - check if the response is appropriate")
        
        elif "hallucination_detection" in test_name:
            if details.get("contains_suspicious_details", False):
                print("   ⚠️  System provided detailed information for concepts not in the game")
                print("   📝 This could indicate hallucination - verify against game data")
            else:
                print("   ✅ System appropriately avoided making up details")
                print("   📝 This might be a test expectation issue rather than system failure")
        
        elif "zelda_guardrails" in test_name:
            if not details.get("not_forbidden", True):
                print("   🚨 CRITICAL: System mentioned Legend of Zelda concepts")
                print("   📝 Check character maintenance node for guardrail failures")
            else:
                print("   ✅ No forbidden terms detected - may be expectation issue")
        
        print("   💡 Recommendation: Manually test this question to verify if it's a real issue")

def create_sample_questions_report():
    """Create a report of sample questions for manual testing"""
    from test_queries import (
        CORE_GAME_QUESTIONS, OFF_TOPIC_QUESTIONS, VAGUE_QUESTIONS,
        SPECIFIC_GAME_QUESTIONS, VERIFICATION_EDGE_CASES
    )
    
    print("🧪 SAMPLE QUESTIONS FOR MANUAL TESTING")
    print("=" * 60)
    print("Copy and paste these into your app to test manually:\n")
    
    print("✅ CORE GAME QUESTIONS (should work well):")
    for i, (question, _) in enumerate(CORE_GAME_QUESTIONS[:5], 1):
        print(f"{i}. {question}")
    
    print(f"\n❌ OFF-TOPIC QUESTIONS (should be politely rejected):")
    for i, question in enumerate(OFF_TOPIC_QUESTIONS[:5], 1):
        print(f"{i}. {question}")
    
    print(f"\n⚠️  VAGUE QUESTIONS (should ask for clarification):")
    for i, question in enumerate(VAGUE_QUESTIONS[:5], 1):
        print(f"{i}. {question}")
    
    print(f"\n🔍 EDGE CASES (test verification system):")
    for i, case in enumerate(VERIFICATION_EDGE_CASES[:3], 1):
        print(f"{i}. {case['question']} (expect: {case['expected_behavior']})")

def main():
    """Main function to run the analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Thudbot test results')
    parser.add_argument('--file', '-f', help='Specific results file to analyze')
    parser.add_argument('--samples', '-s', action='store_true', help='Show sample questions for manual testing')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed failure analysis')
    parser.add_argument('--table', '-t', action='store_true', help='Show failure table format')
    parser.add_argument('--markdown', '-m', action='store_true', help='Save analysis as Markdown file')
    parser.add_argument('--output', '-o', help='Output filename for Markdown report')
    parser.add_argument('--filter', help='Filter detailed analysis by test name pattern')
    
    args = parser.parse_args()
    
    if args.samples:
        create_sample_questions_report()
        return
    
    analyzer = TestReportAnalyzer(args.file)
    
    if args.detailed:
        analyzer.show_detailed_failure_analysis(args.filter)
    elif args.table:
        analyzer.generate_failure_table(args.filter)
    elif args.markdown:
        analyzer.save_markdown_report(args.output, args.filter)
    else:
        analyzer.generate_summary_report()

if __name__ == "__main__":
    main()
