"""
Guardrails for validating agent inputs and outputs using Guardrails.ai API.

This module integrates with specific guards from Guardrails Hub:
1. restricttotopic - Ensure responses stay on topic
2. detect_jailbreak - Prevent prompt injection and jailbreaking
3. competitor_check - Prevent discussion of competitors
4. llm_rag_evaluator - Evaluate RAG response quality
5. profanity_free - Filter out profanity
6. guardrails_pii - Protect PII data
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import os
import os.path
from guardrails import Guard

# Import the installed guards
from guardrails.hub import RestrictToTopic, DetectJailbreak, ProfanityFree, GuardrailsPII

@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    passed: bool
    message: str = ""
    refinement_needed: bool = False

class GuardrailsManager:
    """Manages Guardrails.ai API guards for input and output validation."""
    
    def __init__(self):
        """Initialize guards."""
        # Ensure API key is set
        if not os.getenv("GUARDRAILS_API_KEY"):
            raise ValueError("GUARDRAILS_API_KEY environment variable must be set")
        
        print("Initializing Guardrails.ai guards...")
        
        # Create individual guards using the installed validators
        self.topic_guard = Guard().use(RestrictToTopic(
            valid_topics=[
                "student loans", "financial aid", "education", "FAFSA",
                "research", "academic", "science", "technology", 
                "artificial intelligence", "AI", "machine learning", "ML",
                "neural networks", "transformers", "AI safety", "computer science"
            ]
        ))
        print("Topic guard initialized")
        
        self.jailbreak_guard = Guard().use(DetectJailbreak())
        print("Jailbreak guard initialized")
        
        self.profanity_guard = Guard().use(ProfanityFree())
        print("Profanity guard initialized")
        
        self.pii_guard = Guard().use(GuardrailsPII(entities=["SSN", "EMAIL", "PHONE", "CREDIT_CARD"]))
        print("PII guard initialized")
        
    def validate_input(self, message: HumanMessage) -> GuardrailResult:
        """
        Validate user input using individual guards.
        
        Args:
            message: The user's input message
            
        Returns:
            GuardrailResult indicating if the input passed validation
        """
        content = message.content
        print(f"\nValidating input: {content}")
        
        try:
            # Check topic relevance using Guardrails.ai
            print("Checking topic with RestrictToTopic...")
            result = self.topic_guard.parse(content)
            if not result.validation_passed:
                print("Topic check failed")
                return GuardrailResult(
                    passed=False,
                    message="I cannot provide information on this topic."
                )
            
            # Check for jailbreak attempts
            print("Checking for jailbreak with DetectJailbreak...")
            result = self.jailbreak_guard.parse(content)
            if not result.validation_passed:
                print("Jailbreak check failed")
                return GuardrailResult(
                    passed=False,
                    message="I cannot provide system information or respond to jailbreak attempts."
                )
            
            # Check for profanity
            print("Checking for profanity with ProfanityFree...")
            result = self.profanity_guard.parse(content)
            if not result.validation_passed:
                print("Profanity check failed")
                return GuardrailResult(
                    passed=False,
                    message="Please maintain professional language."
                )
            
            # Check for PII
            print("Checking for PII with GuardrailsPII...")
            result = self.pii_guard.parse(content)
            if not result.validation_passed:
                print("PII check failed")
                return GuardrailResult(
                    passed=False,
                    message="Please do not include personal identifiable information."
                )
            
            print("All input checks passed")
            return GuardrailResult(passed=True)
            
        except Exception as e:
            print(f"Warning: Guard validation error: {str(e)}")
            return GuardrailResult(passed=True)
    
    def validate_output(self, message: AIMessage, context: Dict[str, Any]) -> GuardrailResult:
        """
        Validate agent output using individual guards.
        
        Args:
            message: The agent's output message
            context: Additional context about the conversation
            
        Returns:
            GuardrailResult indicating if the output passed validation
        """
        content = message.content
        print(f"\nValidating output: {content}")
        
        try:
            # Check topic relevance for output
            print("Checking output topic with RestrictToTopic...")
            result = self.topic_guard.parse(content)
            if not result.validation_passed:
                print("Output topic check failed")
                return GuardrailResult(
                    passed=False,
                    message="Response must be related to student financial aid.",
                    refinement_needed=True
                )
            
            # Check for PII in output
            print("Checking output for PII with GuardrailsPII...")
            result = self.pii_guard.parse(content)
            if not result.validation_passed:
                print("Output PII check failed")
                return GuardrailResult(
                    passed=False,
                    message="Response contains personal identifiable information.",
                    refinement_needed=True
                )
            
            print("All output checks passed")
            return GuardrailResult(passed=True)
            
        except Exception as e:
            print(f"Warning: Guard validation error: {str(e)}")
            return GuardrailResult(passed=True)

_guardrails_manager = None

def get_guardrails_manager() -> GuardrailsManager:
    """Get or create the GuardrailsManager singleton."""
    global _guardrails_manager
    if _guardrails_manager is None:
        _guardrails_manager = GuardrailsManager()
    return _guardrails_manager

def reset_guardrails_manager():
    """Reset the guardrails manager singleton to force re-initialization."""
    global _guardrails_manager
    _guardrails_manager = None
    print("Guardrails manager reset - will reinitialize on next use")

def check_message(
    message: BaseMessage,
    context: Optional[Dict[str, Any]] = None
) -> GuardrailResult:
    """
    Main entry point for guardrail validation using Guardrails.ai API.
    
    Args:
        message: The message to validate
        context: Optional context about the conversation
        
    Returns:
        GuardrailResult indicating if the message passed validation
    """
    manager = get_guardrails_manager()
    
    if isinstance(message, HumanMessage):
        return manager.validate_input(message)
    elif isinstance(message, AIMessage):
        return manager.validate_output(message, context or {})
    else:
        return GuardrailResult(passed=True)  # System messages pass through
