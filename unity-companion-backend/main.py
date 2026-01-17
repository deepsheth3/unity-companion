from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.rag import UnityRAG
from core.safety import SafetyChecker
from models.schemas import ChatRequest, ChatResponse

app = FastAPI(title="UNITY Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = UnityRAG()
safety = SafetyChecker()


@app.post('/api/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.messages[-1].content
    
    # Check if escalation needed
    escalate = safety.should_escalate(user_message)
    
    # Get RAG response
    response, confidence, sources = rag.query(
        user_message,
        chat_history=[{"role": m.role, "content": m.content} for m in request.messages[:-1]]
    )
    
    # Validate response
    response = safety.validate_response(response)
    
    return ChatResponse(
        response=response,
        confidence=confidence,
        should_escalate=escalate,
        sources=sources
    )


@app.get('/health')
async def health():
    return {'status': 'ok'}