# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Error Handler & Auto-Fixer | مصلح الأخطاء
=================================================================
Comprehensive error handling, logging, and auto-fix capabilities.

Features:
1. Global Exception Handler
2. Database Self-Repair
3. Session State Recovery
4. Diagnostic Tools
"""

import streamlit as st
import traceback
import logging
import datetime
import os

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/zad_platform.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ZAD")


# =============================================================================
# DECORATOR: SAFE EXECUTION
# =============================================================================

def safe_execute(func):
    """
    Decorator that wraps functions with error handling.
    Catches exceptions, logs them, and shows user-friendly messages.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            # Log the error
            logger.error(f"Error in {func.__name__}: {error_msg}")
            logger.debug(error_trace)
            
            # Show user-friendly message
            st.error(f"⚠️ An error occurred: {error_msg}")
            
            with st.expander("🔍 Error Details (for developers)"):
                st.code(error_trace)
            
            # Try auto-fix
            fix_applied = _attempt_auto_fix(error_msg, func.__name__)
            if fix_applied:
                st.info("🔧 Auto-fix applied! Please refresh the page.")
            
            return None
    
    return wrapper


# =============================================================================
# AUTO-FIX ENGINE
# =============================================================================

def _attempt_auto_fix(error_msg: str, context: str) -> bool:
    """
    Attempt to automatically fix common errors.
    Returns True if a fix was applied.
    """
    
    fixes_applied = []
    
    # Fix 1: Missing database tables
    if "no such table" in error_msg.lower():
        try:
            from models import init_db
            init_db()
            fixes_applied.append("Created missing database tables")
            logger.info("Auto-fix: Created missing database tables")
        except Exception as e:
            logger.error(f"Auto-fix failed: {e}")
    
    # Fix 2: Session state corruption
    if "session_state" in error_msg.lower() or "'NoneType'" in error_msg:
        _repair_session_state()
        fixes_applied.append("Repaired session state")
        logger.info("Auto-fix: Repaired session state")
    
    # Fix 3: Missing werkzeug
    if "werkzeug" in error_msg.lower():
        st.warning("⚠️ Missing 'werkzeug' package. Run: `pip install werkzeug`")
    
    # Fix 4: Missing pandas
    if "pandas" in error_msg.lower():
        st.warning("⚠️ Missing 'pandas' package. Run: `pip install pandas`")
    
    # Fix 5: Database locked
    if "database is locked" in error_msg.lower():
        st.warning("⚠️ Database is locked. Close other connections and try again.")
    
    return len(fixes_applied) > 0


def _repair_session_state():
    """Reset corrupted session state to safe defaults."""
    
    defaults = {
        'logged_in': False,
        'user_id': None,
        'role': None,
        'school_id': None,
        'language': 'ar',
        'is_impersonating': False,
        'db_initialized': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# DIAGNOSTIC TOOLS
# =============================================================================

def run_diagnostics() -> dict:
    """
    Run comprehensive platform diagnostics.
    Returns a dict with status of each component.
    """
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "checks": []
    }
    
    # Check 1: Database Connection
    try:
        from models import get_db_session, School, User
        session = get_db_session()
        session.execute("SELECT 1")
        session.close()
        results["checks"].append({
            "name": "Database Connection",
            "status": "✅ OK",
            "details": "SQLite connected successfully"
        })
    except Exception as e:
        results["checks"].append({
            "name": "Database Connection",
            "status": "❌ FAILED",
            "details": str(e)
        })
    
    # Check 2: Tables Exist
    try:
        from models import get_db_session, School, User, Grade
        session = get_db_session()
        school_count = session.query(School).count()
        user_count = session.query(User).count()
        session.close()
        results["checks"].append({
            "name": "Database Tables",
            "status": "✅ OK",
            "details": f"{school_count} schools, {user_count} users"
        })
    except Exception as e:
        results["checks"].append({
            "name": "Database Tables",
            "status": "❌ FAILED",
            "details": str(e)
        })
    
    # Check 3: Required Modules
    required_modules = ['streamlit', 'sqlalchemy', 'werkzeug', 'pandas']
    for module in required_modules:
        try:
            __import__(module)
            results["checks"].append({
                "name": f"Module: {module}",
                "status": "✅ OK",
                "details": "Installed"
            })
        except ImportError:
            results["checks"].append({
                "name": f"Module: {module}",
                "status": "❌ MISSING",
                "details": f"Run: pip install {module}"
            })
    
    # Check 4: Session State
    required_keys = ['logged_in', 'language']
    missing_keys = [k for k in required_keys if k not in st.session_state]
    if missing_keys:
        results["checks"].append({
            "name": "Session State",
            "status": "⚠️ WARNING",
            "details": f"Missing keys: {missing_keys}"
        })
    else:
        results["checks"].append({
            "name": "Session State",
            "status": "✅ OK",
            "details": "All required keys present"
        })
    
    # Check 5: Super Admin Exists
    try:
        from models import get_db_session, User
        session = get_db_session()
        admin = session.query(User).filter(User.email == "admin@zad.edu").first()
        session.close()
        if admin:
            results["checks"].append({
                "name": "Super Admin",
                "status": "✅ OK",
                "details": "admin@zad.edu exists"
            })
        else:
            results["checks"].append({
                "name": "Super Admin",
                "status": "⚠️ MISSING",
                "details": "Default admin not found"
            })
    except Exception as e:
        results["checks"].append({
            "name": "Super Admin",
            "status": "❌ FAILED",
            "details": str(e)
        })
    
    return results


def show_diagnostics_ui():
    """Display diagnostics UI in Streamlit."""
    
    st.subheader("🔧 Platform Diagnostics | تشخيص المنصة")
    
    if st.button("🔍 Run Full Diagnostic", use_container_width=True):
        with st.spinner("Running diagnostics..."):
            results = run_diagnostics()
        
        st.markdown(f"**Scan Time:** {results['timestamp']}")
        st.markdown("---")
        
        passed = 0
        failed = 0
        warnings = 0
        
        for check in results["checks"]:
            if "✅" in check["status"]:
                passed += 1
                st.success(f"{check['status']} **{check['name']}** - {check['details']}")
            elif "❌" in check["status"]:
                failed += 1
                st.error(f"{check['status']} **{check['name']}** - {check['details']}")
            else:
                warnings += 1
                st.warning(f"{check['status']} **{check['name']}** - {check['details']}")
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Passed", passed)
        col2.metric("⚠️ Warnings", warnings)
        col3.metric("❌ Failed", failed)
        
        if failed > 0:
            if st.button("🔧 Attempt Auto-Fix", type="primary"):
                _run_auto_fix_all()
                st.rerun()


def _run_auto_fix_all():
    """Run all auto-fix procedures."""
    
    st.info("🔧 Running auto-fix procedures...")
    
    # Fix 1: Initialize database
    try:
        from models import init_db
        init_db()
        st.success("✅ Database tables verified/created")
    except Exception as e:
        st.error(f"❌ Database fix failed: {e}")
    
    # Fix 2: Create super admin
    try:
        from models import get_db_session, User
        from werkzeug.security import generate_password_hash
        
        session = get_db_session()
        admin = session.query(User).filter(User.email == "admin@zad.edu").first()
        if not admin:
            admin = User(
                email="admin@zad.edu",
                full_name="Super Admin",
                hashed_password=generate_password_hash("admin123"),
                role="super_admin",
                is_active=True
            )
            session.add(admin)
            session.commit()
            st.success("✅ Super admin created")
        session.close()
    except Exception as e:
        st.error(f"❌ Admin creation failed: {e}")
    
    # Fix 3: Repair session state
    _repair_session_state()
    st.success("✅ Session state repaired")


# =============================================================================
# ERROR PAGE COMPONENT
# =============================================================================

def show_error_page(error_msg: str, error_trace: str = None):
    """Display a user-friendly error page."""
    
    st.error("# ⚠️ حدث خطأ | An Error Occurred")
    
    st.markdown(f"""
    **رسالة الخطأ | Error Message:**
    ```
    {error_msg}
    ```
    """)
    
    if error_trace:
        with st.expander("🔍 Technical Details"):
            st.code(error_trace)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Page", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🔧 Run Diagnostics", use_container_width=True):
            show_diagnostics_ui()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'safe_execute',
    'run_diagnostics',
    'show_diagnostics_ui',
    'show_error_page',
    'logger'
]
