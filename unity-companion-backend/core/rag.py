import json
import os 
from typing import List, Tuple, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from .prompt import SystemPrompt

load_dotenv()

class UnityRAG:
    def __init__(self):
        self.conditions = self._load_conditions()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def _load_conditions(self):
        knowledge_path = os.path.join(
            os.path.dirname(__file__),
            '../knowledge/conditions.json'
        )
        with open(knowledge_path, 'r') as f:
            data = json.load(f)
        return data

    def _retrival(self, query:str) -> dict:
        query = query.lower()
        relevant_conditions = []
        sources = []

        for condition in self.conditions['conditions']:
            if any(kw in query for kw in condition['keywords']):
                relevant_conditions.append(condition)
                sources.append(condition['name'])
        
        result_context = ""
        if "low risk" in query:
            result_context = f"Low Risk Result: {self.conditions['result_types']['low_risk']}"
        elif "high risk" in query:
            result_context = f"High Risk Result: {self.conditions['result_types']['high_risk']}"
        elif "carrier" in query:
            result_context = f"Carrier Status: {self.conditions['result_types']['carrier_positive']}"
    
        context_part = []
        for cond in relevant_conditions:
            context_part.append(
                f"**{cond['name']}**/n"
                f"Description: {cond['description']}"
                f"Inheritance: {cond['inheritance']}"
                f"Frequency: {cond['frequency']}"
                f"Key Facts: {cond['key_facts']}"
            )

        if result_context:
            context_part.append(result_context)

        context = "\n\n".join(context_part) if context_part else "No relevant information found"
        return context, sources

    def _format_chat_history(self, history: List[dict]) -> str:
        """ Format chat history for RAG prompt """
        if not history:
            return "No chat history available"

        formatted = []
        for msg in history[-4:]:
            role = "Patient" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    def query(self, questions: str, chat_history: List[dict]= None) -> Tuple[str, float, List[str]]:
        context, sources = self._retrival(questions)
        
        history_str = self._format_chat_history(chat_history or [])
        prompt = SystemPrompt.get_rag_prompt(
            context=context,
            chat_history=history_str,
            question=questions
        )
        if self.model:
            try:
                full_prompt = f"{SystemPrompt.SYSTEM}\n\n{prompt}"
                response = self.model.generate_content(full_prompt)
                answer = response.text
                confidence = 0.85 if sources else 0.5

            except Exception as e:
                print(f"Gemini error: {e}")
                answer = self._fallback_response(questions)
                confidence = 0.4
        else:
            answer = self._fallback_response(questions)
            confidence = 0.4
        return answer, confidence, sources

    def _fallback_response(self, question: str) -> str:
        """Fallback when API is unavailable."""
        q = question.lower()
        
        if "low risk" in q:
            return ("A 'low risk' result means the chance of your baby having "
                    "that condition is significantly reduced. This is reassuring news! "
                    "Continue your routine prenatal care.")
        
        if "high risk" in q:
            return ("A 'high risk' result indicates an increased chance, but it is "
                    "NOT a diagnosis. I recommend speaking with a genetic counselor "
                    "to discuss confirmatory testing options.")
        
        if any(kw in q for kw in ["counselor", "talk", "speak", "help"]):
            return ("I recommend scheduling a consultation with a genetic counselor. "
                    "You can reach them at unityscreen.com/schedule-a-consult "
                    "or call 650-460-2551.")
        
        return ("I'm here to help you understand your UNITY Complete results. "
                "Feel free to ask about specific conditions, what your results mean, "
                "or how to connect with a genetic counselor.")