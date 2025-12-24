"""
ZAD Education Platform - Audit Logging | منصة زاد - سجل النشاطات
================================================================
Audit logging utility for tracking user actions and system events.
"""

import datetime
import json
from typing import Optional, Any
from core.database import get_db_session
from models import AuditLog


# =============================================================================
# ACTION CONSTANTS
# =============================================================================

class AuditActions:
    """Constants for audit log actions."""
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    REGISTER = "REGISTER"
    
    # Password Management
    PASSWORD_RESET = "PASSWORD_RESET"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    
    # Impersonation
    IMPERSONATE_START = "IMPERSONATE_START"
    IMPERSONATE_END = "IMPERSONATE_END"
    
    # User Management
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    
    # School Management
    SCHOOL_CREATE = "SCHOOL_CREATE"
    SCHOOL_UPDATE = "SCHOOL_UPDATE"
    
    # Grading
    GRADE_CREATE = "GRADE_CREATE"
    GRADE_UPDATE = "GRADE_UPDATE"
    
    # Import/Export
    BULK_IMPORT = "BULK_IMPORT"
    DATA_EXPORT = "DATA_EXPORT"


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def log_action(
    action: str,
    user_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[Any] = None,
    ip_address: Optional[str] = None
) -> bool:
    """
    Log an action to the audit log.
    
    Args:
        action: Action type from AuditActions
        user_id: ID of the user performing the action
        target_type: Type of the target (user, school, grade, etc.)
        target_id: ID of the target
        details: Additional details (dict will be JSON serialized)
        ip_address: IP address of the user
        
    Returns:
        bool: True if logged successfully, False otherwise
    """
    session = get_db_session()
    
    try:
        # Convert dict details to JSON string
        if isinstance(details, dict):
            details = json.dumps(details, ensure_ascii=False)
        
        audit_log = AuditLog(
            timestamp=datetime.datetime.utcnow(),
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address
        )
        
        session.add(audit_log)
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"❌ Audit log error: {e}")
        return False
    
    finally:
        session.close()


def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list:
    """
    Retrieve audit logs with optional filtering.
    
    Args:
        user_id: Filter by user ID
        action: Filter by action type
        limit: Maximum number of logs to return
        offset: Offset for pagination
        
    Returns:
        list: List of AuditLog objects
    """
    session = get_db_session()
    
    try:
        query = session.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        return logs
    
    finally:
        session.close()


def get_recent_activity(user_id: int, limit: int = 10) -> list:
    """
    Get recent activity for a specific user.
    
    Args:
        user_id: User ID
        limit: Number of recent activities
        
    Returns:
        list: Recent activities
    """
    return get_audit_logs(user_id=user_id, limit=limit)


def format_audit_log_for_display(log: AuditLog) -> dict:
    """
    Format an audit log entry for display.
    
    Args:
        log: AuditLog object
        
    Returns:
        dict: Formatted log entry
    """
    action_labels = {
        AuditActions.LOGIN: ("🔐", "Login | تسجيل دخول"),
        AuditActions.LOGOUT: ("🚪", "Logout | تسجيل خروج"),
        AuditActions.LOGIN_FAILED: ("❌", "Failed Login | فشل تسجيل الدخول"),
        AuditActions.PASSWORD_RESET: ("🔑", "Password Reset | إعادة تعيين كلمة المرور"),
        AuditActions.IMPERSONATE_START: ("🎭", "Started Impersonation | بدء الانتحال"),
        AuditActions.IMPERSONATE_END: ("↩️", "Ended Impersonation | إنهاء الانتحال"),
        AuditActions.USER_CREATE: ("👤+", "User Created | إنشاء مستخدم"),
        AuditActions.SCHOOL_CREATE: ("🏫+", "School Created | إنشاء مدرسة"),
        AuditActions.GRADE_CREATE: ("📝+", "Grade Created | إنشاء درجة"),
        AuditActions.BULK_IMPORT: ("📥", "Bulk Import | استيراد جماعي"),
    }
    
    icon, label = action_labels.get(log.action, ("📌", log.action))
    
    return {
        "icon": icon,
        "label": label,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": log.user_id,
        "target": f"{log.target_type or ''} #{log.target_id or ''}".strip(),
        "details": log.details
    }
