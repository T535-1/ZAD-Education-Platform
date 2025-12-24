# -*- coding: utf-8 -*-
"""
Educational Games Engine
========================
Generates AI-powered flashcards and quizzes using Gemini API.
"""

import os
import json
import re
import streamlit as st

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GamesEngine:
    """AI-powered educational games generator."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def generate_flashcards(self, topic: str, num_cards: int = 5, lang: str = "ar") -> list:
        """
        Generate flashcards for a given topic.
        
        Args:
            topic: The educational topic
            num_cards: Number of flashcards to generate
            lang: Language code ('ar' or 'en')
            
        Returns:
            List of flashcard dictionaries with 'term' and 'definition'
        """
        if not self.model:
            # Return demo flashcards if no API
            return self._get_demo_flashcards(topic, lang)
        
        try:
            if lang == "ar":
                prompt = f"""
                أنشئ {num_cards} بطاقات تعليمية (Flashcards) عن موضوع: {topic}
                
                أرجع النتيجة بصيغة JSON فقط بدون أي نص إضافي:
                [
                    {{"term": "المصطلح", "definition": "التعريف"}},
                    ...
                ]
                """
            else:
                prompt = f"""
                Create {num_cards} educational flashcards about: {topic}
                
                Return ONLY JSON format without any additional text:
                [
                    {{"term": "Term", "definition": "Definition"}},
                    ...
                ]
                """
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                cards = json.loads(json_match.group())
                return cards
            else:
                return self._get_demo_flashcards(topic, lang)
                
        except Exception as e:
            st.warning(f"AI Error: {e}. Using demo cards.")
            return self._get_demo_flashcards(topic, lang)
    
    def generate_quiz(self, topic: str, num_questions: int = 5, lang: str = "ar") -> list:
        """
        Generate a multiple-choice quiz for a given topic.
        
        Args:
            topic: The educational topic
            num_questions: Number of questions
            lang: Language code
            
        Returns:
            List of question dictionaries
        """
        if not self.model:
            return self._get_demo_quiz(topic, lang)
        
        try:
            if lang == "ar":
                prompt = f"""
                أنشئ اختبار قصير من {num_questions} أسئلة اختيار من متعدد عن: {topic}
                
                أرجع JSON فقط:
                [
                    {{
                        "question": "السؤال",
                        "options": ["خيار أ", "خيار ب", "خيار ج", "خيار د"],
                        "correct": 0
                    }}
                ]
                حيث correct هو رقم الإجابة الصحيحة (0-3)
                """
            else:
                prompt = f"""
                Create a {num_questions} question multiple-choice quiz about: {topic}
                
                Return ONLY JSON:
                [
                    {{
                        "question": "Question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct": 0
                    }}
                ]
                where correct is the index of the right answer (0-3)
                """
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_demo_quiz(topic, lang)
                
        except Exception:
            return self._get_demo_quiz(topic, lang)
    
    def _get_demo_flashcards(self, topic: str, lang: str) -> list:
        """Return demo flashcards when API is unavailable."""
        if lang == "ar":
            return [
                {"term": f"مفهوم 1 - {topic}", "definition": "هذا تعريف توضيحي للمفهوم الأول"},
                {"term": f"مفهوم 2 - {topic}", "definition": "هذا تعريف توضيحي للمفهوم الثاني"},
                {"term": f"مفهوم 3 - {topic}", "definition": "هذا تعريف توضيحي للمفهوم الثالث"},
            ]
        else:
            return [
                {"term": f"Concept 1 - {topic}", "definition": "This is a demo definition for concept 1"},
                {"term": f"Concept 2 - {topic}", "definition": "This is a demo definition for concept 2"},
                {"term": f"Concept 3 - {topic}", "definition": "This is a demo definition for concept 3"},
            ]
    
    def _get_demo_quiz(self, topic: str, lang: str) -> list:
        """Return demo quiz when API is unavailable."""
        if lang == "ar":
            return [
                {
                    "question": f"ما هو المفهوم الأساسي في {topic}؟",
                    "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
                    "correct": 0
                }
            ]
        else:
            return [
                {
                    "question": f"What is the main concept in {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct": 0
                }
            ]


# Singleton instance
games_engine = GamesEngine()
