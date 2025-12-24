# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Core Module
=====================================
Core functionality: auth, database, AI, i18n, etc.
"""

from core.database import get_db_session
from core.auth import login, logout, hash_password, verify_password, register_user
from core.i18n import get_text
from core.style import load_css

__all__ = [
    'get_db_session',
    'login',
    'logout', 
    'hash_password',
    'verify_password',
    'register_user',
    'get_text',
    'load_css'
]
