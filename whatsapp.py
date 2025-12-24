# -*- coding: utf-8 -*-
"""
WhatsApp Client
===============
Sends messages via Twilio WhatsApp API or provides demo mode.
"""

import os
import streamlit as st

# Try to import Twilio
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# Try to import Gemini for AI drafts
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class WhatsAppClient:
    """WhatsApp messaging client using Twilio."""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        
        # Initialize Twilio client if credentials available
        if self.account_sid and self.auth_token and TWILIO_AVAILABLE:
            self.client = Client(self.account_sid, self.auth_token)
            self.demo_mode = False
        else:
            self.client = None
            self.demo_mode = True
        
        # Initialize Gemini for AI drafts
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.ai_model = None
    
    def send_message(self, to_phone: str, message: str) -> dict:
        """
        Send a WhatsApp message.
        
        Args:
            to_phone: Recipient phone number (e.g., +966...)
            message: Message content
            
        Returns:
            dict with status and details
        """
        # Normalize phone number
        if not to_phone.startswith("+"):
            to_phone = "+" + to_phone
        
        to_whatsapp = f"whatsapp:{to_phone}"
        
        if self.demo_mode:
            return {
                "status": "success",
                "msg": "🔧 وضع تجريبي - الرسالة لم ترسل فعلياً. أضف مفاتيح Twilio للإرسال الحقيقي.",
                "sid": "DEMO_MSG_12345"
            }
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_whatsapp
            )
            return {
                "status": "success",
                "sid": msg.sid,
                "msg": "تم إرسال الرسالة بنجاح!"
            }
        except Exception as e:
            return {
                "status": "error",
                "msg": str(e)
            }
    
    def draft_message(self, topic: str, lang: str = "ar") -> str:
        """
        Generate an AI-drafted message based on topic.
        
        Args:
            topic: The topic/purpose of the message
            lang: Language code
            
        Returns:
            AI-generated message draft
        """
        if not self.ai_model:
            return self._get_demo_draft(topic, lang)
        
        try:
            if lang == "ar":
                prompt = f"""
                اكتب رسالة واتساب قصيرة ومهذبة لولي أمر طالب عن:
                {topic}
                
                الرسالة يجب أن تكون:
                - مختصرة (2-3 جمل)
                - مهنية ولطيفة
                - تتضمن تحية وختام
                """
            else:
                prompt = f"""
                Write a short, polite WhatsApp message to a parent about:
                {topic}
                
                The message should be:
                - Brief (2-3 sentences)
                - Professional and friendly
                - Include greeting and closing
                """
            
            response = self.ai_model.generate_content(prompt)
            return response.text
            
        except Exception:
            return self._get_demo_draft(topic, lang)
    
    def _get_demo_draft(self, topic: str, lang: str) -> str:
        """Return demo draft when AI is unavailable."""
        if lang == "ar":
            return f"""السلام عليكم ورحمة الله وبركاته،

نود إعلامكم بخصوص: {topic}

شاكرين تعاونكم،
إدارة المدرسة"""
        else:
            return f"""Dear Parent,

We would like to inform you about: {topic}

Thank you for your cooperation,
School Administration"""
    
    def get_message_templates(self, lang: str = "ar") -> list:
        """Get pre-built message templates."""
        if lang == "ar":
            return [
                {"name": "تذكير بالاجتماع", "template": "تذكير: اجتماع أولياء الأمور يوم {date} الساعة {time}"},
                {"name": "غياب الطالب", "template": "نود إعلامكم بغياب {student} اليوم. نرجو التواصل معنا."},
                {"name": "تهنئة", "template": "مبارك! حصل {student} على درجة ممتازة في {subject}!"},
                {"name": "تذكير بالواجب", "template": "تذكير: موعد تسليم واجب {subject} هو {date}."}
            ]
        else:
            return [
                {"name": "Meeting Reminder", "template": "Reminder: Parent meeting on {date} at {time}"},
                {"name": "Absence Notice", "template": "We inform you that {student} was absent today. Please contact us."},
                {"name": "Congratulations", "template": "Congratulations! {student} achieved an excellent grade in {subject}!"},
                {"name": "Assignment Reminder", "template": "Reminder: {subject} assignment is due on {date}."}
            ]


# Singleton instance
wa_client = WhatsAppClient()
