# -*- coding: utf-8 -*-
"""
Configuration Management for ZAD Education Platform | منصة زاد التعليمية
Centralized settings for production deployment

SECURITY NOTE: All sensitive values MUST be loaded from environment variables.
Never commit actual secrets to version control.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized Configuration Class
    All settings are loaded from environment variables with sensible defaults
    """

    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    APP_NAME = "ZAD Education Platform - School Cloud"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development/staging/production
    
    # Production flag for security enforcement
    IS_PRODUCTION = ENVIRONMENT == "production"

    # ========================================================================
    # PATHS
    # ========================================================================
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    VECTOR_STORES_DIR = DATA_DIR / "vector_stores"
    LOGS_DIR = BASE_DIR / "logs"

    # Create directories if they don't exist
    for directory in [DATA_DIR, UPLOADS_DIR, VECTOR_STORES_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # DATABASE SETTINGS
    # ========================================================================
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'zad_edu.db'}"
    )

    # For production PostgreSQL:
    # DATABASE_URL = "postgresql://user:password@localhost/zad_edu_db"

    # ========================================================================
    # AI/LLM SETTINGS
    # ========================================================================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

    # Model configurations
    GEMINI_FLASH_MODEL = "gemini-1.5-flash"  # Fast, cost-effective
    GEMINI_PRO_MODEL = "gemini-1.5-pro"      # More capable, reasoning
    EMBEDDING_MODEL = "models/embedding-001"

    # Default model (can be overridden per use case)
    DEFAULT_MODEL = GEMINI_FLASH_MODEL

    # AI Usage Limits (Free Tier)
    FREE_TIER_AI_REQUESTS_PER_MONTH = 100
    PRO_TIER_AI_REQUESTS_PER_MONTH = -1  # Unlimited

    # ========================================================================
    # SUBSCRIPTION TIERS
    # ========================================================================
    SUBSCRIPTION_LIMITS = {
        "Free": {
            "max_users": 50,
            "max_ai_requests": 100,
            "max_storage_mb": 100,
            "features": ["basic_ai_tutor", "assignments", "attendance"]
        },
        "Pro": {
            "max_users": 500,
            "max_ai_requests": -1,  # Unlimited
            "max_storage_mb": 5000,  # 5GB
            "features": ["advanced_ai_tutor", "quiz_generator", "lesson_planner", "analytics", "api_access"]
        },
        "Enterprise": {
            "max_users": -1,  # Unlimited
            "max_ai_requests": -1,
            "max_storage_mb": -1,
            "features": ["all_pro_features", "custom_branding", "dedicated_support", "sso"]
        }
    }

    # ========================================================================
    # SECURITY SETTINGS
    # ========================================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-to-a-random-secret")
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT_MINUTES = 60

    # ========================================================================
    # FILE UPLOAD SETTINGS
    # ========================================================================
    ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".docx", ".txt"]
    MAX_UPLOAD_SIZE_MB = 10
    MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ========================================================================
    # RAG SETTINGS
    # ========================================================================
    RAG_CHUNK_SIZE = 1000
    RAG_CHUNK_OVERLAP = 200
    RAG_TOP_K_RESULTS = 4  # Number of relevant chunks to retrieve
    RAG_SIMILARITY_THRESHOLD = 0.7

    # ========================================================================
    # UI/UX SETTINGS
    # ========================================================================
    DEFAULT_LANGUAGE = "ar"  # Arabic
    SUPPORTED_LANGUAGES = ["ar", "en"]
    RTL_LANGUAGES = ["ar"]

    # Mobile breakpoints (in pixels)
    MOBILE_BREAKPOINT = 768
    TABLET_BREAKPOINT = 1024

    # ========================================================================
    # EMAIL SETTINGS (Optional - for notifications)
    # ========================================================================
    SMTP_SERVER = os.getenv("SMTP_SERVER", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@zad-edu.ai")

    # ========================================================================
    # THIRD-PARTY INTEGRATIONS
    # ========================================================================
    # Twilio (WhatsApp/SMS)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # OpenAI (Fallback/Additional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # ========================================================================
    # LOGGING
    # ========================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "zad_edu.log"

    # ========================================================================
    # PERFORMANCE SETTINGS
    # ========================================================================
    # Streamlit caching
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 300  # 5 minutes

    # Database connection pooling
    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 10

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate critical configuration settings.
        
        Performs stricter validation in production environment.

        Returns:
            (is_valid: bool, errors: list[str])
        """
        errors = []
        warnings = []

        # Check critical API keys
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set in environment variables")

        # Production-specific security checks
        if cls.IS_PRODUCTION:
            # SECRET_KEY must be changed
            if cls.SECRET_KEY == "change-this-in-production-to-a-random-secret":
                errors.append("🔴 CRITICAL: SECRET_KEY must be changed in production!")
            
            # SECRET_KEY should be long enough
            if len(cls.SECRET_KEY) < 32:
                errors.append("🔴 CRITICAL: SECRET_KEY should be at least 32 characters")
            
            # SQLite not recommended for production
            if cls.DATABASE_URL.startswith("sqlite"):
                warnings.append("⚠️ SQLite is not recommended for production. Use PostgreSQL.")
            
            # Debug should be off
            if cls.DEBUG:
                errors.append("🔴 CRITICAL: DEBUG must be False in production!")

        # Print warnings (non-blocking)
        for warning in warnings:
            print(f"   {warning}")

        return len(errors) == 0, errors

    @classmethod
    def get_model_for_task(cls, task: str) -> str:
        """
        Get the appropriate Gemini model for a specific task

        Args:
            task: Task type (chat/quiz/lesson_plan/analysis)

        Returns:
            Model name to use
        """
        task_model_mapping = {
            "chat": cls.GEMINI_FLASH_MODEL,  # Fast responses for chat
            "quiz": cls.GEMINI_FLASH_MODEL,
            "lesson_plan": cls.GEMINI_PRO_MODEL,  # More complex reasoning
            "analysis": cls.GEMINI_PRO_MODEL,
            "default": cls.DEFAULT_MODEL
        }

        return task_model_mapping.get(task, task_model_mapping["default"])

    @classmethod
    def is_feature_enabled(cls, tier: str, feature: str) -> bool:
        """
        Check if a feature is enabled for a subscription tier

        Args:
            tier: Subscription tier (Free/Pro/Enterprise)
            feature: Feature name

        Returns:
            True if feature is enabled
        """
        if tier not in cls.SUBSCRIPTION_LIMITS:
            return False

        tier_features = cls.SUBSCRIPTION_LIMITS[tier]["features"]
        return feature in tier_features or "all_pro_features" in tier_features


# Global config instance
config = Config()


# Validation check on import
is_valid, errors = config.validate()
if not is_valid:
    print("⚠️  Configuration Warnings:")
    for error in errors:
        print(f"   - {error}")
