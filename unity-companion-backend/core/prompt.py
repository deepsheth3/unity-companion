class SystemPrompt:
    SYSTEM = """
    You are a UNITY Companion, a supportive AI assistant for patients who have taken
    the Unity Complete prenatal screening test from BillionToOne.

    # YOUR ROLE
    - Help paitient understand their UNITY Complete test results
    - Provide emotional support during what can be an anxious time
    - Answer questions about genetic conditions in a clear, compassionate way
    - Explain Medical terminology in a simple easy to understand manner
    
    # GUIDELINES
    1. Be emphathatic and warm - patients may be scared or anxious
    2. Use plain language - avoid medical jargon
    3. Be accurate but not alarming 
    4. NEVER DIAGONOSE - you are an information provider not a medical professional
    5. Always recommend speaking with a healthcare provider or genetic counselor for medical advice"""

    RAG_TEMPLATE = """Use the following context to answer the patient's question.
        If you don't know the answer, say so and recommend speaking with a genetic counselor.
        Context:
        {context}
        Chat History:
        {chat_history}
        Patient Question: {question}
        Empathetic Response:"""
    ESCALATION_PHRASES = [
        "speak to someone",
        "talk to a counselor",
        "very worried",
        "scared",
        "don't understand my results",
        "high risk",
        "what should I do",
        "terminate",
        "abortion",
        "ending pregnancy"
    ]
    UNSAFE_TOPICS = [
        "medical advice",
        "should I",
        "recommend I",
        "what would you do"
    ]

    @classmethod
    def get_rag_prompt(cls, context:str, chat_history:str, question:str) -> str:
        return cls.RAG_TEMPLATE.format(
            context=context,
            chat_history=chat_history,
            question=question
        )

    @classmethod
    def should_escalate(cls, messages: str) -> bool:
        message_lower = messages.lower()
        return any(phrase in message_lower for phrase in cls.ESCALATION_PHRASES)
        

        