#!/usr/bin/env python3
"""
LangSmith API Key Security Checker

This script programmatically inspects LangSmith traces to detect any API key exposure.
It searches through trace data including inputs, outputs, metadata, and configurations
to ensure no sensitive information is being logged.

Usage:
    python check_langsmith_traces.py [--project PROJECT_NAME] [--limit N] [--api-key-pattern PATTERN]

Requirements:
    - LANGCHAIN_API_KEY environment variable must be set
    - langsmith Python package must be installed
"""

import os
import sys
import argparse
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add backend directory to path for package imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from thudbot_core.config import load_env  # Import robust .env loader
load_env()

try:
    from langsmith import Client
except ImportError:
    print("❌ Error: langsmith package not found. Install with: pip install langsmith")
    sys.exit(1)


class LangSmithAPIKeyChecker:
    """Checks LangSmith traces for potential API key exposure"""
    
    def __init__(self, project_name: str = "THUDBOT-DD", api_key_patterns: List[str] = None):
        self.project_name = project_name
        self.client = Client()
        
        # Default patterns for OpenAI API keys
        if api_key_patterns is None:
            self.api_key_patterns = [
                r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
                r'sk-proj-[a-zA-Z0-9]{64}',  # OpenAI project API key pattern
                r'OPENAI_API_KEY',  # Environment variable name
                r'openai_api_key',  # Config key name
                r'api_key',  # Generic API key field
            ]
        else:
            self.api_key_patterns = api_key_patterns
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.api_key_patterns]
    
    def search_in_data(self, data: Any, path: str = "root") -> List[Dict[str, str]]:
        """Recursively search for API key patterns in nested data structures"""
        findings = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}"
                
                # Check key names
                for pattern in self.compiled_patterns:
                    if pattern.search(str(key)):
                        findings.append({
                            "type": "key_name",
                            "path": current_path,
                            "pattern": pattern.pattern,
                            "value": str(key)[:50] + "..." if len(str(key)) > 50 else str(key)
                        })
                
                # Check values
                if isinstance(value, str):
                    for pattern in self.compiled_patterns:
                        if pattern.search(value):
                            findings.append({
                                "type": "value",
                                "path": current_path,
                                "pattern": pattern.pattern,
                                "value": value[:20] + "..." if len(value) > 20 else value
                            })
                
                # Recurse into nested structures
                findings.extend(self.search_in_data(value, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                findings.extend(self.search_in_data(item, current_path))
        
        elif isinstance(data, str):
            for pattern in self.compiled_patterns:
                if pattern.search(data):
                    findings.append({
                        "type": "string_value",
                        "path": path,
                        "pattern": pattern.pattern,
                        "value": data[:20] + "..." if len(data) > 20 else data
                    })
        
        return findings
    
    def check_trace(self, run) -> Dict[str, Any]:
        """Check a single trace/run for API key exposure"""
        findings = []
        
        # Check inputs
        if hasattr(run, 'inputs') and run.inputs:
            findings.extend(self.search_in_data(run.inputs, "inputs"))
        
        # Check outputs
        if hasattr(run, 'outputs') and run.outputs:
            findings.extend(self.search_in_data(run.outputs, "outputs"))
        
        # Check extra metadata
        if hasattr(run, 'extra') and run.extra:
            findings.extend(self.search_in_data(run.extra, "extra"))
        
        # Check serialized data
        if hasattr(run, 'serialized') and run.serialized:
            findings.extend(self.search_in_data(run.serialized, "serialized"))
        
        # Check any other attributes that might contain data
        for attr in ['tags', 'metadata']:
            if hasattr(run, attr):
                attr_value = getattr(run, attr)
                if attr_value:
                    findings.extend(self.search_in_data(attr_value, attr))
        
        return {
            "run_id": str(run.id) if hasattr(run, 'id') else "unknown",
            "run_name": getattr(run, 'name', 'unknown'),
            "run_type": getattr(run, 'run_type', 'unknown'),
            "start_time": getattr(run, 'start_time', None),
            "findings": findings
        }
    
    def check_recent_traces(self, limit: int = 50, hours_back: int = 24) -> Dict[str, Any]:
        """Check recent traces for API key exposure"""
        print(f"🔍 Checking last {limit} traces from project '{self.project_name}' (last {hours_back} hours)")
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        try:
            # List recent runs
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                limit=limit,
                start_time=start_time,
                end_time=end_time
            ))
            
            print(f"📊 Found {len(runs)} traces to analyze")
            
            if not runs:
                return {
                    "total_traces": 0,
                    "traces_with_issues": 0,
                    "total_findings": 0,
                    "results": [],
                    "summary": "No traces found in the specified time range"
                }
            
            # Check each trace
            results = []
            total_findings = 0
            
            for i, run in enumerate(runs, 1):
                print(f"  🔍 Checking trace {i}/{len(runs)}: {getattr(run, 'name', 'unknown')}", end="")
                
                result = self.check_trace(run)
                
                if result["findings"]:
                    print(f" ❌ ISSUES FOUND ({len(result['findings'])})")
                    total_findings += len(result["findings"])
                else:
                    print(" ✅")
                
                results.append(result)
            
            traces_with_issues = sum(1 for r in results if r["findings"])
            
            return {
                "total_traces": len(runs),
                "traces_with_issues": traces_with_issues,
                "total_findings": total_findings,
                "results": results,
                "patterns_checked": self.api_key_patterns,
                "summary": f"Checked {len(runs)} traces, found {total_findings} potential issues in {traces_with_issues} traces"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to check traces: {str(e)}",
                "total_traces": 0,
                "traces_with_issues": 0,
                "total_findings": 0,
                "results": []
            }
    
    def generate_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate a detailed security report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if results.get("error"):
            report = f"""
🚨 LANGSMITH API KEY SECURITY CHECK - ERROR
============================================================
Timestamp: {timestamp}
Project: {self.project_name}
Error: {results['error']}
"""
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(report)
            return report
        
        # Generate summary
        status = "🎉 SECURE" if results["total_findings"] == 0 else "🚨 SECURITY ISSUES DETECTED"
        
        report = f"""
🔒 LANGSMITH API KEY SECURITY CHECK
============================================================
Timestamp: {timestamp}
Project: {self.project_name}
Status: {status}

📊 SUMMARY:
- Total traces checked: {results['total_traces']}
- Traces with issues: {results['traces_with_issues']}
- Total potential exposures: {results['total_findings']}
- Patterns checked: {len(results.get('patterns_checked', []))}

🔍 PATTERNS SEARCHED:
{chr(10).join(f"  - {pattern}" for pattern in results.get('patterns_checked', []))}
"""
        
        if results["total_findings"] > 0:
            report += "\n🚨 DETAILED FINDINGS:\n"
            report += "=" * 60 + "\n"
            
            for result in results["results"]:
                if result["findings"]:
                    report += f"\n📍 TRACE: {result['run_name']} (ID: {result['run_id']})\n"
                    report += f"   Type: {result['run_type']}\n"
                    if result['start_time']:
                        report += f"   Time: {result['start_time']}\n"
                    
                    for finding in result["findings"]:
                        report += f"   ⚠️  {finding['type'].upper()}: {finding['path']}\n"
                        report += f"      Pattern: {finding['pattern']}\n"
                        report += f"      Value: {finding['value']}\n"
        else:
            report += "\n✅ NO SECURITY ISSUES FOUND!\n"
            report += "All traces appear to be free of API key exposure.\n"
        
        report += f"\n{results['summary']}\n"
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Check LangSmith traces for API key exposure")
    parser.add_argument("--project", default="THUDBOT-DD", help="LangSmith project name")
    parser.add_argument("--limit", type=int, default=50, help="Number of recent traces to check")
    parser.add_argument("--hours-back", type=int, default=24, help="Hours back to search")
    parser.add_argument("--output", help="Output file for detailed report")
    parser.add_argument("--api-key-pattern", action="append", help="Additional API key patterns to check")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Check for LangSmith API key
    if not os.getenv('LANGCHAIN_API_KEY'):
        print("❌ Error: LANGCHAIN_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize checker
    checker = LangSmithAPIKeyChecker(
        project_name=args.project,
        api_key_patterns=args.api_key_pattern
    )
    
    if not args.quiet:
        print(f"🔒 LangSmith API Key Security Checker")
        print(f"🎯 Target project: {args.project}")
        print(f"📊 Checking last {args.limit} traces ({args.hours_back} hours)")
        print("=" * 60)
    
    # Run the check
    results = checker.check_recent_traces(limit=args.limit, hours_back=args.hours_back)
    
    # Generate and display report
    output_file = args.output
    if not output_file and results["total_findings"] > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"tests/security/results/langsmith_security_check_{timestamp}.txt"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    report = checker.generate_report(results, output_file)
    
    if not args.quiet:
        print(report)
    
    # Exit with appropriate code
    if results.get("error"):
        sys.exit(2)
    elif results["total_findings"] > 0:
        if not args.quiet:
            print("🚨 SECURITY ISSUES DETECTED - Review the findings above!")
        sys.exit(1)
    else:
        if not args.quiet:
            print("🎉 All traces are secure - no API key exposure detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
