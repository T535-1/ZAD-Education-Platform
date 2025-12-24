# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Authentication Module | منصة زاد - وحدة المصادقة
=====================================
Secure authentication with bcrypt password hashing and rate limiting.

SECURITY FEATURES:
- bcrypt password hashing with automatic salting
- Session-based rate limiting for brute-force protection
- Timing-safe password verification
"""

import time
import streamlit as st
from models import User, get_db_session
import bcrypt


# ========================================================================
# RATE LIMITING CONFIGURATION
# ========================================================================
MAX_LOGIN_ATTEMPTS = 5          # Maximum failed attempts before lockout
LOCKOUT_DURATION_SECONDS = 60   # Lockout duration in seconds


# ========================================================================
# PASSWORD HASHING (BCRYPT)
# ========================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with automatic salting.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Bcrypt hashed password (includes salt)
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')  # Store as string in database


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a password against a stored bcrypt hash.
    
    Args:
        stored_password: Bcrypt hashed password from database (string)
        provided_password: Plain text password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Convert strings to bytes for bcrypt
        stored_bytes = stored_password.encode('utf-8')
        provided_bytes = provided_password.encode('utf-8')
        return bcrypt.checkpw(provided_bytes, stored_bytes)
    except (ValueError, TypeError) as e:
        # Invalid hash format
        print(f"Password verification error: {e}")
        return False


# ========================================================================
# RATE LIMITING HELPERS
# ========================================================================

def _init_rate_limit_state():
    """Initialize rate limiting session state if not present."""
    if '_login_attempts' not in st.session_state:
        st.session_state['_login_attempts'] = 0
    if '_lockout_until' not in st.session_state:
        st.session_state['_lockout_until'] = 0


def _is_locked_out() -> bool:
    """Check if user is currently locked out."""
    _init_rate_limit_state()
    if st.session_state['_lockout_until'] > time.time():
        return True
    return False


def _get_lockout_remaining() -> int:
    """Get remaining lockout time in seconds."""
    _init_rate_limit_state()
    remaining = st.session_state['_lockout_until'] - time.time()
    return max(0, int(remaining))


def _record_failed_attempt():
    """Record a failed login attempt and trigger lockout if needed."""
    _init_rate_limit_state()
    st.session_state['_login_attempts'] += 1
    
    if st.session_state['_login_attempts'] >= MAX_LOGIN_ATTEMPTS:
        st.session_state['_lockout_until'] = time.time() + LOCKOUT_DURATION_SECONDS
        st.session_state['_login_attempts'] = 0


def _reset_rate_limit():
    """Reset rate limiting after successful login."""
    st.session_state['_login_attempts'] = 0
    st.session_state['_lockout_until'] = 0


# ========================================================================
# AUTHENTICATION FUNCTIONS
# ========================================================================

def login(username: str, password: str) -> bool:
    """
    Authenticates a user with rate limiting protection.
    """
    # --- RATE LIMITING CHECK ---
    if _is_locked_out():
        remaining = _get_lockout_remaining()
        st.error(
            f"🔒 تم قفل تسجيل الدخول مؤقتاً. حاول بعد {remaining} ثانية.\n\n"
            f"🔒 Login locked. Try again in {remaining} seconds."
        )
        return False
    
    # --- DATABASE QUERY ---
    session = get_db_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        
        # --- PASSWORD VERIFICATION ---
        if user and verify_password(user.hashed_password, password):
            # SUCCESS
            _reset_rate_limit()
            
            st.session_state['logged_in'] = True
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = user.id
            st.session_state['username'] = user.username
            st.session_state['user_role'] = user.role
            st.session_state['school_id'] = user.school_id
            return True
    finally:
        session.close()
    
    # --- FAILED LOGIN ---
    _record_failed_attempt()
    remaining_attempts = MAX_LOGIN_ATTEMPTS - st.session_state.get('_login_attempts', 0)
    
    if remaining_attempts > 0:
        st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة. المحاولات المتبقية: {remaining_attempts}")
    
    return False


def logout():
    """Logs out the user by clearing the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def register_user(username: str, password: str, role: str, school_id: int) -> tuple:
    """Registers a new user with secure password hashing."""
    session = get_db_session()
    
    try:
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists."
        
        hashed_password = hash_password(password)
        new_user = User(
            username=username, 
            hashed_password=hashed_password, 
            role=role, 
            school_id=school_id
        )
        session.add(new_user)
        session.commit()
        return True, "User registered successfully."
    except Exception as e:
        session.rollback()
        return False, f"Registration error: {str(e)}"
    finally:
        session.close()
