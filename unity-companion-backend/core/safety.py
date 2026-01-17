from typing import List
from .prompt import SystemPrompt


class SafetyChecker:
    """Safety guardrails for UNITY Companion responses."""
    
    ESCALATION_RESPONSE = (
        "I understand this may be a difficult time. I strongly recommend "
        "speaking with one of our licensed genetic counselors who can provide "
        "personalized guidance.\n\n"
        "📞 Schedule: unityscreen.com/schedule-a-consult\n"
        "📧 Email: support@unityscreen.com\n"
        "☎️ Call: 650-460-2551"
    )
    
    UNSAFE_RESPONSE = (
        "I'm not able to provide specific medical advice. For personalized "
        "guidance about your situation, please speak with your healthcare "
        "provider or a genetic counselor."
    )
    
    BLOCKED_PHRASES = [
        "you should terminate",
        "you should abort",
        "i recommend you",
        "you must",
        "definitely will have",
        "your baby will have",
        "guaranteed",
        "100%"
    ]
    
    def should_escalate(self, message: str) -> bool:
        """Check if message should be escalated to human counselor."""
        return SystemPrompt.should_escalate(message)
    
    def validate_response(self, response: str) -> str:
        """Validate and sanitize AI response for safety."""
        response_lower = response.lower()
        
        # Check for blocked phrases
        for phrase in self.BLOCKED_PHRASES:
            if phrase in response_lower:
                return self._sanitize_response(response, phrase)
        
        # Ensure disclaimer is present for medical topics
        if self._contains_medical_content(response):
            if "genetic counselor" not in response_lower:
                response += (
                    "\n\n*For personalized medical advice, please consult "
                    "with a genetic counselor.*"
                )
        
        return response
    
    def _sanitize_response(self, response: str, blocked_phrase: str) -> str:
        """Remove or replace blocked content."""
        # Log the issue (in production, send to monitoring)
        print(f"Blocked phrase detected: {blocked_phrase}")
        
        return (
            "I want to help, but I need to be careful not to overstep. "
            "A genetic counselor can provide the specific guidance you need. "
            "Would you like help scheduling a consultation?"
        )
    
    def _contains_medical_content(self, response: str) -> bool:
        """Check if response contains medical content."""
        medical_keywords = [
            "risk", "diagnosis", "condition", "syndrome",
            "disease", "treatment", "therapy", "test result"
        ]
        response_lower = response.lower()
        return any(kw in response_lower for kw in medical_keywords)
    
    def get_escalation_response(self) -> str:
        """Get standard escalation response."""
        return self.ESCALATION_RESPONSE