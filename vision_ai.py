"""
ZAD Education Platform - Vision AI Service | منصة زاد - خدمة الذكاء الاصطناعي للرؤية
===================================================================================
AI-powered image analysis for grading student work.
Supports OpenAI GPT-4 Vision, Google Gemini Vision, with mock fallback.
"""

import os
import base64
from typing import Optional, Tuple
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()


class VisionAI:
    """
    Vision AI service for analyzing student work images.
    
    Supports multiple providers with automatic fallback:
    1. OpenAI GPT-4 Vision
    2. Google Gemini Vision
    3. Mock mode (for testing)
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
        
        # Initialize clients
        self._openai_client = None
        self._gemini_model = None
        
        if not self.use_mock:
            self._init_clients()
    
    def _init_clients(self):
        """Initialize AI clients based on available API keys."""
        # Try OpenAI
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                print("⚠️ OpenAI library not installed. Run: pip install openai")
            except Exception as e:
                print(f"⚠️ OpenAI initialization error: {e}")
        
        # Try Google Gemini
        if self.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_api_key)
                self._gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
            except ImportError:
                print("⚠️ Google Generative AI library not installed. Run: pip install google-generativeai")
            except Exception as e:
                print(f"⚠️ Gemini initialization error: {e}")
    
    def analyze_image(
        self,
        image_data: bytes,
        subject: str = "General",
        max_score: int = 100
    ) -> dict:
        """
        Analyze a student work image and provide grading feedback.
        
        Args:
            image_data: Image bytes
            subject: Subject/topic of the assignment
            max_score: Maximum possible score
            
        Returns:
            dict: {
                'score': float,
                'max_score': int,
                'feedback': str,
                'provider': str  # 'openai', 'gemini', or 'mock'
            }
        """
        if self.use_mock:
            return self._mock_analysis(subject, max_score)
        
        # Try OpenAI first
        if self._openai_client:
            try:
                return self._analyze_with_openai(image_data, subject, max_score)
            except Exception as e:
                print(f"⚠️ OpenAI error, falling back to Gemini: {e}")
        
        # Fallback to Gemini
        if self._gemini_model:
            try:
                return self._analyze_with_gemini(image_data, subject, max_score)
            except Exception as e:
                print(f"⚠️ Gemini error, falling back to mock: {e}")
        
        # Final fallback to mock
        return self._mock_analysis(subject, max_score)
    
    def _analyze_with_openai(
        self,
        image_data: bytes,
        subject: str,
        max_score: int
    ) -> dict:
        """Analyze using OpenAI GPT-4 Vision."""
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        prompt = self._get_grading_prompt(subject, max_score)
        
        response = self._openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        result = self._parse_ai_response(response.choices[0].message.content, max_score)
        result['provider'] = 'openai'
        return result
    
    def _analyze_with_gemini(
        self,
        image_data: bytes,
        subject: str,
        max_score: int
    ) -> dict:
        """Analyze using Google Gemini Vision."""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        prompt = self._get_grading_prompt(subject, max_score)
        
        response = self._gemini_model.generate_content([prompt, image])
        
        result = self._parse_ai_response(response.text, max_score)
        result['provider'] = 'gemini'
        return result
    
    def _get_grading_prompt(self, subject: str, max_score: int) -> str:
        """Generate the grading prompt."""
        return f"""You are an expert teacher grading student work in {subject}.

Analyze this student's work and provide:
1. A numerical score out of {max_score}
2. Detailed feedback in both Arabic and English

Consider:
- Correctness of answers
- Organization and presentation
- Effort and completeness
- Handwriting clarity (if applicable)

Format your response as:
SCORE: [number]
FEEDBACK:
[Your detailed feedback here, in Arabic first then English]

Be encouraging while being accurate in your assessment."""
    
    def _parse_ai_response(self, response_text: str, max_score: int) -> dict:
        """Parse AI response to extract score and feedback."""
        import re
        
        # Try to extract score
        score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            score = min(score, max_score)  # Cap at max_score
        else:
            # Default if score not found
            score = max_score * 0.75
        
        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.+)', response_text, re.IGNORECASE | re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        else:
            feedback = response_text
        
        return {
            'score': score,
            'max_score': max_score,
            'feedback': feedback
        }
    
    def _mock_analysis(self, subject: str, max_score: int) -> dict:
        """Provide mock analysis for testing."""
        import random
        import time
        
        # Simulate processing time
        time.sleep(1.5)
        
        score = random.randint(int(max_score * 0.6), int(max_score * 0.98))
        
        feedbacks = [
            f"عمل ممتاز في {subject}! الإجابات واضحة ومنظمة.\n\nExcellent work in {subject}! Answers are clear and well-organized.",
            f"جهد جيد جداً في {subject}. بعض الأخطاء البسيطة لكن الفهم العام ممتاز.\n\nVery good effort in {subject}. Minor errors but overall understanding is excellent.",
            f"عمل مقبول في {subject}. يحتاج لمزيد من المراجعة.\n\nSatisfactory work in {subject}. Needs more review.",
            f"إجابات جيدة في {subject}. استمر في التحسن!\n\nGood answers in {subject}. Keep improving!",
        ]
        
        return {
            'score': score,
            'max_score': max_score,
            'feedback': random.choice(feedbacks),
            'provider': 'mock'
        }


# Singleton instance
vision_ai = VisionAI()
