from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(Enum):
    LOW = 'low',
    MEDIUM = 'medium',
    HIGH = 'high'

class Message(BaseModel):
    role: str
    content:str

class ChatRequest(BaseModel):
    messages: List[Message]

class Source(BaseModel):
    title: str
    content: str
    relevance_score: float

class ChatResponse(BaseModel):
    response: str
    confidence: float = Field(ge=0.0, le=1.0)
    should_escalate: bool = False
    sources: List[str] = []
    detected_intent: Optional[str] = None

class Condition(BaseModel):
    name: str
    description: str
    inheritance: str
    frequency: str
    key_facts: List[str]
    risk_level: Optional[RiskLevel] = None
