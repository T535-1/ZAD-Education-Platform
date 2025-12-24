
import streamlit as st
import cv2
import numpy as np
import google.generativeai as genai
import os

class HandwritingGrader:
    """
    A Deep Learning class to grade handwritten answers from an image.
    It uses OpenCV for preprocessing and the Gemini Vision API for analysis.
    """
    def __init__(self):
        """
        Initializes the grader and configures the Gemini API.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocesses the input image to make it look like a high-contrast scan.
        
        Args:
            image_bytes (bytes): The raw bytes of the image from st.camera_input.
            
        Returns:
            np.ndarray: A processed image ready for analysis.
        """
        # Decode the image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to get a binary image
        # This is great for handling different lighting conditions
        processed_img = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        return processed_img

    def grade_handwriting(self, image_bytes: bytes, rubric: str):
        """
        Takes an image of handwriting, processes it, and sends it to Gemini for grading.
        
        Args:
            image_bytes (bytes): The raw image bytes.
            rubric (str): The grading criteria or model answer.
            
        Returns:
            dict: A dictionary containing the grade, corrections, and feedback.
        """
        try:
            # Preprocess the image
            processed_image = self._preprocess_image(image_bytes)
            
            # Convert processed image back to bytes for the API
            is_success, buffer = cv2.imencode(".jpg", processed_image)
            if not is_success:
                raise RuntimeError("Failed to encode processed image.")
            
            image_parts = [{"mime_type": "image/jpeg", "data": buffer.tobytes()}]
            
            # Construct the prompt for Gemini
            prompt = f"""
            You are an AI Vision Grader. Analyze the provided image of a handwritten answer.
            Compare it against the following rubric/model answer:
            ---
            RUBRIC: "{rubric}"
            ---
            Your task is to:
            1. Transcribe the handwritten text.
            2. Grade the answer based on the rubric (e.g., "8/10").
            3. Provide a list of corrections or suggestions for improvement.
            4. Generate a short, encouraging audio feedback summary (less than 15 words).
            
            Return the result as a JSON object with the keys: "transcription", "grade", "corrections", "feedback_summary".
            """
            
            # Call the Gemini API
            response = self.model.generate_content([prompt] + image_parts)
            
            # Extract and return the JSON content
            # A more robust solution would parse the response more carefully
            return response.text
            
        except Exception as e:
            st.error(f"An error occurred during grading: {e}")
            return {
                "transcription": "",
                "grade": "Error",
                "corrections": ["Could not process the image."],
                "feedback_summary": "An error occurred."
            }
