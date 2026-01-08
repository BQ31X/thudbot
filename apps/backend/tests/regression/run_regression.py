#!/usr/bin/env python3
"""
Simple Raw Collector for Thudbot Regression Testing

This script runs test questions through the Thudbot system and captures
raw outputs from each node without interpretation. Human analysis required.
"""
# Use centralized path utilities
from tests.utils.paths import add_project_root_to_path, REGRESSION_ROOT, REGRESSION_RESULTS_ROOT
add_project_root_to_path()

import csv
import sys
import os
import time
from datetime import datetime
from pathlib import Path

from thudbot_core.config import load_env  # Import robust .env loader
load_env()

try:
    from thudbot_core.app import run_hint_request, create_thud_graph
    from thudbot_core.state import LangGraphState
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root with the venv activated")
    sys.exit(1)

class RawCollector:
    """Collects raw outputs from Thudbot nodes without interpretation"""
    
    def __init__(self, input_csv: str, run_label: str="regression"):
        self.input_csv = input_csv
        self.run_label = run_label
        self.results = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def run_collection(self):
        """Run all test questions and collect raw outputs"""
        start_time = time.time()
        print(f"🚀 Starting Raw Collection - {self.timestamp}")
        print("=" * 60)
        
        # Load test questions
        questions = self._load_questions()
        print(f"📋 Loaded {len(questions)} test questions")
        
        # Process each question
        for i, (question, expected_router, notes) in enumerate(questions, 1):
            print(f"\n🔍 {i}/{len(questions)}: {question[:50]}...")
            
            try:
                result = self._collect_raw_data(question, expected_router, notes)
                self.results.append(result)
                
                # Medium verbosity: Show key debugging info
                search_query = result['search_query']
                if search_query != question and search_query != "N/A":
                    print(f"   🔍 Search Query: '{search_query}' (≠ question)")
                else:
                    print(f"   🔍 Search Query: '{search_query}'")
                print(f"   ✅ Collected: Router={result['router']}, Verify={result['verify']}")
                
            except Exception as e:
                error_result = {
                    'question': question,
                    'expected_router': expected_router, 
                    'notes': notes,
                    'router': 'ERROR',
                    'hint': f'Error: {str(e)}',
                    'verify': 'ERROR',
                    'final': f'Error: {str(e)}',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'duration': 0
                }
                self.results.append(error_result)
                print(f"   ❌ Error: {str(e)}")
        
        # Calculate total duration
        total_duration = time.time() - start_time
        self.total_duration = total_duration
        
        # Save results
        self._save_csv()
        self._save_markdown()
        self._create_latest_symlink()
        
        print(f"\n🎉 Collection complete!")
        print(f"📊 Results: {len([r for r in self.results if r['router'] != 'ERROR'])} successful, {len([r for r in self.results if r['router'] == 'ERROR'])} errors")
        print(f"⏱️ Total duration: {total_duration:.1f}s")
        print(f"📄 Saved to: {REGRESSION_RESULTS_ROOT / f'{self.run_label}_{self.timestamp}.csv'}")
        print(f"📄 Saved to: {REGRESSION_RESULTS_ROOT / f'{self.run_label}_{self.timestamp}.md'}")
        
    def _load_questions(self):
        """Load questions from CSV file"""
        questions = []
        with open(self.input_csv, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append((row['question'], row['expected_router'], row['notes']))
        return questions
    
    def _collect_raw_data(self, question: str, expected_router: str, notes: str):
        """Collect raw data from a single question run"""
        start_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Capture debug output by redirecting stdout temporarily
        import sys
        from io import StringIO
        
        # Capture both the result and debug output
        old_stdout = sys.stdout
        debug_capture = StringIO()
        sys.stdout = debug_capture
        
        try:
            final_output = run_hint_request(question)
            debug_output = debug_capture.getvalue()
        finally:
            sys.stdout = old_stdout
        
        # Parse debug output for detailed routing information
        hint_level = self._extract_hint_level(debug_output, final_output)
        escalation_type = self._extract_escalation_type(debug_output)
        search_query = self._extract_search_query(debug_output)
        
        # Infer router decision from output patterns
        if any(phrase in final_output for phrase in ["Listen sweetie", "Sorry hon", "I appreciate the chat"]):
            router_result = "OFF_TOPIC"
            hint_text = "N/A"
            verify_result = "N/A"
        else:
            # Enhanced router result with escalation info
            if escalation_type:
                router_result = f"GAME_RELATED ({escalation_type}, L{hint_level})"
            else:
                router_result = f"GAME_RELATED (L{hint_level})"
            
            # Infer verification status for game-related queries
            if "more detail" in final_output.lower() or "more specific" in final_output.lower() or "Get a bit more specific" in final_output:
                verify_result = "INSUFFICIENT_CONTEXT"
            elif "🎯 Hint" in final_output:
                verify_result = "VERIFIED"
            elif "too specific" in final_output.lower():
                verify_result = "TOO_SPECIFIC"
            elif "hallucination" in final_output.lower() or "not enough information" in final_output.lower():
                verify_result = "HALLUCINATED"
            else:
                verify_result = "UNKNOWN"
                
            # Try to extract hint from formatted output
            if "🎯 Hint" in final_output:
                hint_start = final_output.find("🎯 Hint")
                hint_end = final_output.find("\n\n", hint_start) if final_output.find("\n\n", hint_start) > hint_start else len(final_output)
                hint_text = final_output[hint_start:hint_end]
                if len(hint_text) > 150:
                    hint_text = hint_text[:150] + "..."
            else:
                # For non-verified responses, capture first part of response as "hint attempt"
                hint_text = final_output[:100] + "..." if len(final_output) > 100 else final_output
        
        duration = time.time() - start_time
        
        return {
            'question': question,
            'expected_router': expected_router,
            'notes': notes,
            'router': router_result,
            'search_query': search_query,
            'hint': hint_text,
            'verify': verify_result,
            'final': final_output,
            'timestamp': timestamp,
            'duration': round(duration, 2)
        }
    
    def _extract_hint_level(self, debug_output: str, final_output: str) -> int:
        """Extract hint level from debug output or final output"""
        # Try debug output first
        import re
        level_match = re.search(r'continuing to hint flow \(level (\d+)\)', debug_output)
        if level_match:
            return int(level_match.group(1))
        
        # Fallback to final output
        level_match = re.search(r'🎯 Hint \(Level (\d+)\)', final_output)
        if level_match:
            return int(level_match.group(1))
        
        return 1  # Default
    
    def _extract_escalation_type(self, debug_output: str) -> str:
        """Extract escalation type from debug output"""
        if "keyword similarity" in debug_output:
            return "keyword escalation"
        elif "exact match fallback" in debug_output:
            return "exact escalation"
        elif "Vague escalation detected" in debug_output:
            return "vague escalation"
        return ""
    
    def _extract_search_query(self, debug_output: str) -> str:
        """Extract what query was sent to find_hint"""
        import re
        # Look for the FIND_HINT INPUT line
        match = re.search(r"🔍 FIND_HINT INPUT: '([^']+)'", debug_output)
        if match:
            query = match.group(1)
            return query[:50] + "..." if len(query) > 50 else query
        return "N/A"
    
    def _save_csv(self):
        """Save results as CSV"""
        output_file = REGRESSION_RESULTS_ROOT / f"{self.run_label}_{self.timestamp}.csv"
        
        with open(output_file, 'w', newline='') as f:
            if self.results:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
    
    def _save_markdown(self):
        """Save results as Markdown table"""
        output_file = REGRESSION_RESULTS_ROOT / f"{self.run_label}_{self.timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Thudbot Test Results ({self.run_label})\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Test Count:** {len(self.results)}\n\n")
            
            # Summary stats
            successful = len([r for r in self.results if r['router'] != 'ERROR'])
            errors = len([r for r in self.results if r['router'] == 'ERROR'])
            game_related = len([r for r in self.results if r['router'].startswith('GAME_RELATED')])
            off_topic = len([r for r in self.results if r['router'] == 'OFF_TOPIC'])
            
            # Timing analysis
            off_topic_times = [r['duration'] for r in self.results if r['router'] == 'OFF_TOPIC']
            game_related_times = [r['duration'] for r in self.results if r['router'].startswith('GAME_RELATED')]
            verified_times = [r['duration'] for r in self.results if r['router'].startswith('GAME_RELATED') and r['verify'] == 'VERIFIED']
            insufficient_context_times = [r['duration'] for r in self.results if r['router'].startswith('GAME_RELATED') and r['verify'] == 'INSUFFICIENT_CONTEXT']
            
            # Calculate averages with proper precision
            def calc_avg(times_list):
                if not times_list:
                    return "n/a"
                avg = sum(times_list) / len(times_list)
                # Use 2 decimals if we have enough precision, else 1
                if len(times_list) >= 3:
                    return f"{avg:.2f}s"
                else:
                    return f"{avg:.1f}s"
            
            avg_off_topic = calc_avg(off_topic_times)
            avg_game_related = calc_avg(game_related_times)
            avg_verified = calc_avg(verified_times)
            avg_insufficient = calc_avg(insufficient_context_times)
            
            f.write(f"## Summary\n\n")
            f.write(f"- ✅ Successful: {successful}\n")
            f.write(f"- ❌ Errors: {errors}\n")
            f.write(f"- 🎮 Game Related: {game_related}\n")
            f.write(f"- 🚫 Off Topic: {off_topic}\n\n")
            # Format total duration
            total_duration_str = f"{self.total_duration:.1f}s" if hasattr(self, 'total_duration') else "n/a"
            
            f.write(f"### Timing Analysis\n")
            f.write(f"- ⏱️ Total Test Duration: {total_duration_str}\n")
            f.write(f"- 🚫 Off Topic (avg): {avg_off_topic}\n")
            f.write(f"- 🎮 Game Related (avg): {avg_game_related}\n")
            f.write(f"- ✅ Verified (avg): {avg_verified}\n")
            f.write(f"- ⚠️ Insufficient Context (avg): {avg_insufficient}\n\n")
            
            # Results table
            f.write(f"## Detailed Results\n\n")
            f.write("| Question | Expected | Router | Search Query | Hint | Verify | Final | Time |\n")
            f.write("|----------|----------|--------|--------------|------|--------|-------|------|\n")
            
            for result in self.results:
                question = result['question'][:40] + "..." if len(result['question']) > 40 else result['question']
                search_query = result['search_query'][:30] + "..." if len(result['search_query']) > 30 else result['search_query']
                hint = result['hint'][:30] + "..." if len(result['hint']) > 30 else result['hint']
                final = result['final'][:50] + "..." if len(result['final']) > 50 else result['final']
                
                # Escape pipes for Markdown
                question = question.replace("|", "\\|")
                search_query = search_query.replace("|", "\\|")
                hint = hint.replace("|", "\\|")
                final = final.replace("|", "\\|")
                
                f.write(f"| {question} | {result['expected_router']} | {result['router']} | {search_query} | {hint} | {result['verify']} | {final} | {result['timestamp']} |\n")
    
    def _create_latest_symlink(self):
        """Create symlink to latest results"""
        csv_file = f"{self.run_label}_{self.timestamp}.csv"
        symlink_path = REGRESSION_RESULTS_ROOT / f"latest_{self.run_label}.csv"
        
        # Remove existing symlink if it exists
        if os.path.exists(symlink_path) or os.path.islink(symlink_path):
            os.remove(symlink_path)
            
        # Create new symlink
        os.symlink(csv_file, symlink_path)

def main():
    """Main entry point"""
    input_csv = REGRESSION_ROOT / "test_questions.csv"
    
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        print("Create test_questions.csv with columns: question,expected_router,notes")
        sys.exit(1)
    
    # Environment already loaded via load_env() at top of file
    
    collector = RawCollector(input_csv)
    collector.run_collection()

if __name__ == "__main__":
    main()
