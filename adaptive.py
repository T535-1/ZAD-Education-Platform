# -*- coding: utf-8 -*-
from core.ai import ai_client

class AdaptiveEngine:
    def __init__(self):
        self.client = ai_client

    def generate_learning_path(self, topic: str, student_level: str = "Intermediate", lang: str = "ar") -> str:
        """
        Generates a personalized learning path.
        """
        system_instruction = """
        You are an Adaptive Learning Engine.
        Create a personalized learning path for a student based on the topic and their level.
        The path should consist of 3-5 clear steps.
        For each step, suggest a resource type (Video, Article, Quiz) and a brief description.
        Format the output as a structured list or markdown.
        """
        
        if lang == "ar":
            system_instruction += "\nRespond in Arabic."
        else:
            system_instruction += "\nRespond in English."

        prompt = f"""
        {system_instruction}
        
        Topic: {topic}
        Student Level: {student_level}
        
        Generate Learning Path:
        """
        
        return self.client.generate_response(prompt)

adaptive_engine = AdaptiveEngine()
