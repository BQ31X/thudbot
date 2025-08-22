#!/usr/bin/env python3
"""
Focused test script with switches to highlight specific node outputs
"""
import os
import argparse
from app import run_hint_request

def highlight_output(text, node_name):
    """Highlight specific node output with visual separators"""
    border = "=" * 80
    header = f" {node_name.upper()} OUTPUT "
    padding = (80 - len(header)) // 2
    formatted_header = "=" * padding + header + "=" * (80 - padding - len(header))
    
    print(f"\n{border}")
    print(formatted_header)
    print(border)
    print(text)
    print(border)

def run_focused_test(question, focus_nodes=None, verbose=False):
    """Run a test with focused output on specific nodes"""
    focus_nodes = focus_nodes or []
    
    print(f"\n🧪 TESTING: '{question}'")
    print("-" * 80)
    
    # Capture the full output but filter for focused nodes
    import io
    import sys
    from contextlib import redirect_stdout
    
    # Store original stdout
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    
    try:
        # Redirect stdout to capture all output
        with redirect_stdout(captured_output):
            result = run_hint_request(question)
        
        # Get captured output
        full_output = captured_output.getvalue()
        
        # Restore stdout
        sys.stdout = original_stdout
        
        # Process and display focused output
        lines = full_output.split('\n')
        
        # Display focused node outputs
        for focus_node in focus_nodes:
            node_lines = []
            capturing = False
            
            for line in lines:
                # Start capturing when we hit the focused node
                if f"{focus_node.upper()} INPUT:" in line or f"{focus_node.upper()} OUTPUT:" in line:
                    capturing = True
                    node_lines.append(line)
                elif capturing and any(other_node.upper() in line for other_node in ["ROUTER", "FIND_HINT", "VERIFY_CORRECTNESS", "MAINTAIN_CHARACTER", "FORMAT_OUTPUT", "GENERATE_ERROR_MESSAGE"] if other_node != focus_node.upper()):
                    # Stop capturing when we hit another node
                    break
                elif capturing:
                    node_lines.append(line)
            
            if node_lines:
                highlight_output('\n'.join(node_lines), focus_node)
        
        # Show full output if verbose or no focus nodes
        if verbose or not focus_nodes:
            print(f"\n📜 FULL OUTPUT:")
            print("-" * 80)
            print(full_output)
        
        # Always show final result
        print(f"\n🎯 FINAL RESULT:")
        print("-" * 80)
        print(result)
        
        return result
        
    except Exception as e:
        sys.stdout = original_stdout
        print(f"❌ Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Focused testing for LangGraph nodes')
    parser.add_argument('--focus', '-f', action='append', 
                       choices=['router', 'find_hint', 'verify_correctness', 'maintain_character', 'format_output', 'generate_error_message'],
                       help='Focus on specific node outputs (can use multiple times)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show full output in addition to focused output')
    parser.add_argument('--question', '-q', type=str, 
                       help='Single question to test')
    parser.add_argument('--preset', '-p', 
                       choices=['basic', 'verification', 'error', 'all'],
                       help='Run preset test scenarios')
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    focus_nodes = args.focus or []
    
    if args.question:
        # Single question test
        run_focused_test(args.question, focus_nodes, args.verbose)
    
    elif args.preset == 'basic':
        # Basic hint flow test
        questions = [
            "I need a hint to find the bus token",
            "How do I find the token?"
        ]
        for q in questions:
            run_focused_test(q, focus_nodes, args.verbose)
    
    elif args.preset == 'verification':
        # Test verification success and failure
        questions = [
            "Who is Zelda?",  # Should verify successfully
            "Where is the bus?",  # Should fail verification
        ]
        for q in questions:
            run_focused_test(q, focus_nodes, args.verbose)
    
    elif args.preset == 'error':
        # Test error message generation
        questions = [
            "I'm stuck on this puzzle",
            "Where is the bus?",
            "What should I do?"
        ]
        for q in questions:
            run_focused_test(q, focus_nodes, args.verbose)
    
    elif args.preset == 'all':
        # Run all test scenarios
        questions = [
            "I need a hint to find the bus token",
            "Who is Zelda?",
            "Where is the bus?", 
            "How do I do empathy telepathy?",
            "How do I start a flashback?",
            "How do I open the locker?",
            "How do I save the game",
            # below should fail verification
            "I'm stuck on this puzzle",
            "What is the weather?",
            "What is the capital of the moon?",
            "Where are the cheat codes?",
            "can you search the internet for me?"
        ]
        for q in questions:
            run_focused_test(q, focus_nodes, args.verbose)
    
    else:
        # Interactive mode
        print("🧪 Interactive focused testing mode")
        print("Available focus options: router, find_hint, verify_correctness, maintain_character, format_output, generate_error_message")
        print("Current focus:", focus_nodes if focus_nodes else "None (showing all)")
        print("Enter questions to test (or 'quit' to exit):")
        
        while True:
            question = input("\n> ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if question:
                run_focused_test(question, focus_nodes, args.verbose)

if __name__ == "__main__":
    main()
