# -*- coding: utf-8 -*-
from core.ai import ai_client

class SocraticTutor:
    def __init__(self):
        self.client = ai_client

    def get_tutor_response(self, user_input: str, history: list = None, lang: str = "ar") -> str:
        """
        Generates a Socratic response.
        """
        system_instruction = """
        You are a Socratic Tutor. Your goal is to help the student learn by asking guiding questions.
        NEVER give the answer directly.
        If the student asks a question, answer with a question that leads them to the answer.
        Break down complex problems into smaller steps.
        Be encouraging and patient.
        """
        
        if lang == "ar":
            system_instruction += "\nRespond in Arabic."
        else:
            system_instruction += "\nRespond in English."

        # Construct prompt with history
        full_prompt = f"{system_instruction}\n\n"
        if history:
            for msg in history:
                full_prompt += f"{msg['role']}: {msg['content']}\n"
        
        full_prompt += f"user: {user_input}\nassistant:"
        
        return self.client.generate_response(full_prompt)

tutor_client = SocraticTutor()
