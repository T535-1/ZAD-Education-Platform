# -*- coding: utf-8 -*-
from core.ai import ai_client
from PIL import Image
import io

class VisionGrader:
    def __init__(self):
        self.client = ai_client

    def grade_submission(self, image_bytes: bytes, rubric: str, lang: str = "ar") -> str:
        """
        Analyzes an image and grades it based on the rubric.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return f"Error processing image: {e}"

        system_instruction = """
        You are an expert AI Teacher and Grader.
        Analyze the provided image of student work.
        Grade it strictly based on the provided rubric.
        Provide a detailed breakdown of the score, feedback, and corrections for any mistakes.
        """
        
        if lang == "ar":
            system_instruction += "\nRespond in Arabic."
        else:
            system_instruction += "\nRespond in English."

        prompt = f"""
        {system_instruction}
        
        Rubric/Instructions:
        {rubric}
        
        Please provide the grading report now.
        """
        
        # Gemini 1.5 Pro supports image + text prompts
        try:
            response = self.client.model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"AI Vision Error: {str(e)}"

vision_grader = VisionGrader()
