#!/usr/bin/env python3
"""
Centralized Test Queries for Thudbot Hint System
All test question lists in one place for easy maintenance and expansion
"""

# Core game functionality tests - questions that should work well
CORE_GAME_QUESTIONS = [
    ("How do I find the bus token?", "bus token"),
    ("Who is Zelda?", "assistant"),
    ("How do I save the game?", "save"),
    ("Where is the Thirsty Tentacle?", "bar"),
    ("How do I interact with objects?", "click"),
    ("How do I open the locker?", "locker"),
    ("How do I do empathy telepathy?", "empathy"),
    ("How do I start a flashback?", "flashback"),
]

# Off-topic questions that should get polite rejections
OFF_TOPIC_QUESTIONS = [
    "What's the weather like?",
    "Tell me a joke",
    "How do I play Minecraft?",
    "What's 2+2?",
    "Hello, how are you?",
    "What time is it?",
    "How do I cook pasta?",
]

# Vague questions that should get clarification requests or off-topic responses
VAGUE_QUESTIONS = [
    "I'm stuck on this puzzle",
    "Help me with this",
    "What should I do?",
    "How do I solve a puzzle?",
    "I need help",
    "I don't know what to do",
    "This is confusing",
    "I'm lost",
]

# Specific questions with expected keywords for validation
SPECIFIC_GAME_QUESTIONS = [
    ("How do I find the bus token?", ["token", "bus"]),
    ("How do I open the locker?", ["locker", "open"]),
    ("How do I save the game?", ["save", "game"]),
    ("Where is the Thirsty Tentacle?", ["tentacle", "bar"]),
    ("How do I interact with objects?", ["click", "interact"]),
    ("Who is Alias Node?", ["alias", "detective"]),
]

# Edge case questions for verification system testing
VERIFICATION_EDGE_CASES = [
    # TOO_SPECIFIC cases - vague questions that should get clarification
    {
        "question": "I'm stuck on this puzzle",
        "expected_behavior": "clarification_or_off_topic",
        "test_type": "TOO_SPECIFIC"
    },
    {
        "question": "Help me with this",
        "expected_behavior": "clarification_or_off_topic", 
        "test_type": "TOO_SPECIFIC"
    },
    {
        "question": "What should I do next?",
        "expected_behavior": "clarification_or_off_topic",
        "test_type": "TOO_SPECIFIC"
    },
    # VERIFIED cases - specific questions with good context
    {
        "question": "How do I find the bus token?",
        "expected_behavior": "specific_helpful_response",
        "test_type": "VERIFIED"
    },
    {
        "question": "Who is Zelda?",
        "expected_behavior": "character_information",
        "test_type": "VERIFIED"
    },
    {
        "question": "How do I save the game?",
        "expected_behavior": "specific_helpful_response",
        "test_type": "VERIFIED"
    },
    # INSUFFICIENT_CONTEXT cases - specific questions without enough data
    {
        "question": "How do I solve the quantum flux capacitor puzzle?",
        "expected_behavior": "insufficient_context_message",
        "test_type": "INSUFFICIENT_CONTEXT"
    },
    {
        "question": "Where is the ultra-rare alien artifact?",
        "expected_behavior": "insufficient_context_message", 
        "test_type": "INSUFFICIENT_CONTEXT"
    },
    {
        "question": "How do I activate the hyperdrive?",
        "expected_behavior": "insufficient_context_message",
        "test_type": "INSUFFICIENT_CONTEXT"
    },
]

# Questions that might lead to hallucinations if not properly controlled
HALLUCINATION_RISK_QUESTIONS = [
    "What happens when you use the hyperdrive?",  # Sci-fi term not in Space Bar
    "How do I defeat the final boss?",  # Gaming concept, wrong game type
    "Where is the secret treasure room?",  # Generic adventure game concept
    "How do I cast spells?",  # Fantasy concept, not sci-fi
    "What are the cheat codes?",  # Modern gaming concept
    "How do I level up my character?",  # RPG concept
    "Where can I buy weapons?",  # Combat game concept
]

# User experience and quality testing questions
UX_TEST_QUESTIONS = [
    "How do I find the bus token?",
    "Who is Zelda?",
    "How do I save the game?",
    "What's the weather?",  # off-topic for comparison
    "How do I interact with objects?",
]

# Performance testing questions (mix of game and off-topic)
PERFORMANCE_TEST_QUESTIONS = [
    "How do I find the bus token?",  # Game question (full pipeline)
    "Who is Zelda?",  # Game question (character info)
    "What's the weather?",  # Off-topic (should be faster)
]

# Progressive hints preparation questions
PROGRESSIVE_HINTS_QUESTIONS = {
    "repeat_detection_variants": [
        "How do I find the bus token?",
        "How do I find the bus token?",  # Exact repeat
        "how do i find the bus token?",  # Case variation
        "How do I find the bus token??", # Punctuation variation
        "How can I find the bus token?", # Minor wording change
    ],
    
    "multi_level_potential": [
        "How do I find the bus token?",
        "How do I save the game?",
        "Who is Zelda?",
        "How do I interact with objects?",
        "How do I open the locker?",
    ],
    
    "escalation_readiness": [
        "How do I find the bus token?",
        "How do I save the game?",
        "How do I interact with objects?",
        "Who is Zelda?",
    ]
}

# Edge case input testing
EDGE_CASE_INPUTS = {
    "empty_inputs": [
        "",
        " ",
        "\n",
        "\t",
        "   \n\t   "
    ],
    
    "long_inputs": [
        "How do I find the token? " * 100,  # Repetitive long input
        "A" * 1000,  # Single character repeated
        "How do I find the bus token in the space bar game that has aliens and puzzles? " * 50,  # Realistic but very long
    ],
    
    "special_characters": [
        "How do I find the tökën?",  # Unicode
        "Where is the bus? 🚌",  # Emoji
        "How do I save the game?!@#$%^&*()",  # Special characters
        "Where's the \"bus token\" in 'The Space Bar'?",  # Quotes
        "<script>alert('test')</script> Where is the token?",  # HTML/XSS attempt
        "SELECT * FROM hints WHERE question='token'",  # SQL injection attempt
    ],
    
    "ambiguous_pronouns": [
        "How do I use it?",
        "Where is it located?",
        "Can you help me with this?",
        "What does it do?",
        "How do I fix this thing?",
        "Why won't this work?"
    ]
}

# Test configuration
TEST_CONFIG = {
    "max_test_duration": 30.0,  # Maximum seconds per test
    "response_length_min": 10,   # Minimum expected response length
    "response_length_max": 500,  # Maximum reasonable response length
    "quality_threshold": 80,     # Minimum success rate for quality tests
    "performance_threshold": 15.0,  # Maximum acceptable response time (seconds)
}

# Helper functions for test data access
def get_all_game_questions():
    """Get all questions that should be routed to game hints"""
    questions = []
    questions.extend([q[0] for q in CORE_GAME_QUESTIONS])
    questions.extend([q[0] for q in SPECIFIC_GAME_QUESTIONS])
    questions.extend([case["question"] for case in VERIFICATION_EDGE_CASES if case["test_type"] == "VERIFIED"])
    return list(set(questions))  # Remove duplicates

def get_all_off_topic_questions():
    """Get all questions that should be routed as off-topic"""
    questions = []
    questions.extend(OFF_TOPIC_QUESTIONS)
    questions.extend(VAGUE_QUESTIONS)
    questions.extend(HALLUCINATION_RISK_QUESTIONS)
    return list(set(questions))  # Remove duplicates

def get_test_questions_by_category(category):
    """Get test questions by category name"""
    categories = {
        "core": CORE_GAME_QUESTIONS,
        "off_topic": OFF_TOPIC_QUESTIONS,
        "vague": VAGUE_QUESTIONS,
        "specific": SPECIFIC_GAME_QUESTIONS,
        "verification_edge": VERIFICATION_EDGE_CASES,
        "hallucination": HALLUCINATION_RISK_QUESTIONS,
        "ux": UX_TEST_QUESTIONS,
        "performance": PERFORMANCE_TEST_QUESTIONS,
        "progressive_hints": PROGRESSIVE_HINTS_QUESTIONS,
        "edge_cases": EDGE_CASE_INPUTS,
    }
    return categories.get(category, [])

def get_test_config():
    """Get test configuration parameters"""
    return TEST_CONFIG.copy()

# Statistics
def get_test_statistics():
    """Get statistics about test questions"""
    stats = {
        "core_questions": len(CORE_GAME_QUESTIONS),
        "off_topic_questions": len(OFF_TOPIC_QUESTIONS),
        "vague_questions": len(VAGUE_QUESTIONS),
        "specific_questions": len(SPECIFIC_GAME_QUESTIONS),
        "verification_edge_cases": len(VERIFICATION_EDGE_CASES),
        "hallucination_risk": len(HALLUCINATION_RISK_QUESTIONS),
        "ux_questions": len(UX_TEST_QUESTIONS),
        "performance_questions": len(PERFORMANCE_TEST_QUESTIONS),
        "total_unique_game_questions": len(get_all_game_questions()),
        "total_unique_off_topic_questions": len(get_all_off_topic_questions()),
    }
    
    # Calculate totals
    stats["total_questions"] = sum(stats.values()) - stats["total_unique_game_questions"] - stats["total_unique_off_topic_questions"]
    
    return stats

if __name__ == "__main__":
    # Print statistics when run directly
    print("📊 THUDBOT TEST QUERIES STATISTICS")
    print("=" * 50)
    
    stats = get_test_statistics()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"✅ Good coverage across test categories")
    print(f"✅ Total question count appropriate for comprehensive testing")
    print(f"ℹ️  You can add more questions to any category as needed")
    print(f"ℹ️  Edit this file to expand test coverage")
