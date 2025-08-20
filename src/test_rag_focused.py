#!/usr/bin/env python3
"""
Focused RAG testing script with configurable modes
- Test RAG-only without character processing
- Skip negative test cases  
- Focus on retrieval quality debugging
"""

import sys
import os
sys.path.append('src')

from agent import get_direct_hint
from app import run_hint_request

def test_rag_only():
    """Test RAG retrieval without character processing"""
    print("🧪 RAG-Only Testing (bypassing character processing)")
    print("=" * 60)
    
    test_cases = [
        "where is the bus token",
        "how do I find the token", 
        "I need a hint to find the bus token",
        "where is the token in the cup",
        "How do I get on the bus to Quantelope Lodge?",  # Exact CSV match
        "why can't I do anything in the fleebix flashback",
        "I'm stuck on this puzzle",
        "who is Zelda",
        "how do I save the game"
    ]
    
    results = []
    for query in test_cases:
        print(f"\n--- Query: '{query}' ---")
        try:
            rag_result = get_direct_hint(query)
            print(f"RAG: {rag_result}")
            
            # Simple success check
            success = "provided information doesn't contain enough details" not in rag_result.lower()
            status = "✅ Found info" if success else "❌ No info found"
            print(f"Status: {status}")
            
            results.append({
                'query': query,
                'rag_result': rag_result,
                'success': success
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'query': query,
                'rag_result': f"ERROR: {e}",
                'success': False
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RAG TEST SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    print("\n❌ Failed Queries:")
    for r in results:
        if not r['success']:
            print(f"  - '{r['query']}'")
    
    return results

def test_full_pipeline():
    """Test full pipeline including character processing"""
    print("\n🧪 Full Pipeline Testing (with character processing)")
    print("=" * 60)
    
    test_cases = [
        "where is the bus token",
        "I need a hint to find the bus token", 
        "why can't I do anything in the fleebix flashback",
        "who is Zelda"
    ]
    
    for query in test_cases:
        print(f"\n--- Query: '{query}' ---")
        try:
            full_result = run_hint_request(query)
            print(f"Final: {full_result[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main test runner with configurable modes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Focused RAG testing")
    parser.add_argument("--rag-only", action="store_true", 
                       help="Test RAG retrieval only (bypass character processing)")
    parser.add_argument("--full", action="store_true",
                       help="Test full pipeline including character processing") 
    parser.add_argument("--all", action="store_true",
                       help="Run all test modes")
    
    args = parser.parse_args()
    
    if args.all or args.rag_only:
        test_rag_only()
    
    if args.all or args.full:
        test_full_pipeline()
    
    if not any([args.rag_only, args.full, args.all]):
        # Default: RAG-only for quick debugging
        test_rag_only()

if __name__ == "__main__":
    main()
