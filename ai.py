# -*- coding: utf-8 -*-
import os
import google.generativeai as genai
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "phi3" # Updated to phi3 as per user request
        
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found. Will default to Ollama if available.")
        else:
            genai.configure(api_key=self.api_key)
            
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def set_api_key(self, key: str):
        """Sets the API key dynamically."""
        self.api_key = key
        genai.configure(api_key=self.api_key)

    def generate_response_ollama(self, prompt: str, context: str = "") -> str:
        """
        Generates a response using the local Ollama instance.
        """
        full_prompt = f"""
        You are the "Institutional Brain" for a school. 
        Answer the following question based strictly on the provided context if available.
        
        Context:
        {context}
        
        Question:
        {prompt}
        """
        
        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get('response', "⚠️ Ollama returned no response.")
        except requests.exceptions.ConnectionError:
            return "⚠️ Error: Could not connect to local Ollama instance. Is it running?"
        except Exception as e:
            return f"⚠️ Ollama Error: {str(e)}"

    def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Generates a response using Gemini, falling back to Ollama on error.
        """
        # 1. Try Gemini
        if self.api_key:
            try:
                full_prompt = f"""
                You are the "Institutional Brain" for a school. 
                Answer the following question based strictly on the provided context if available.
                If the context doesn't contain the answer, say so, but try to be helpful based on general educational knowledge if appropriate, 
                while clarifying it's general advice.
                
                Context:
                {context}
                
                Question:
                {prompt}
                """
                
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"Gemini Error: {e}. Falling back to Ollama...")
                # Fallthrough to Ollama
        
        # 2. Fallback to Ollama
        return self.generate_response_ollama(prompt, context)

# Singleton instance
ai_client = GeminiClient()
