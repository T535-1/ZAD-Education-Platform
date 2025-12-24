# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsClient:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def text_to_speech(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
        """
        Converts text to speech using ElevenLabs API.
        Default voice_id: Rachel (21m00Tcm4TlvDq8ikWAM)
        """
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is missing.")

        url = f"{self.base_url}/text-to-speech/{voice_id}"
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"ElevenLabs API Error: {response.status_code} - {response.text}")

# Singleton
voice_client = ElevenLabsClient()
