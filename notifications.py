"""
ZAD Education Platform - Notifications Service | منصة زاد - خدمة الإشعارات
==========================================================================
Notification management for user alerts and system messages.
"""

from typing import List, Optional
from core.database import get_db_session
from models import Notification, User


# =============================================================================
# NOTIFICATION TYPES
# =============================================================================

class NotificationTypes:
    """Constants for notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    GRADE = "grade"
    MESSAGE = "message"
    SYSTEM = "system"


# =============================================================================
# NOTIFICATION FUNCTIONS
# =============================================================================

def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = NotificationTypes.INFO
) -> bool:
    """
    Create a new notification for a user.
    
    Args:
        user_id: Target user ID
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        
    Returns:
        bool: True if created successfully
    """
    session = get_db_session()
    
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            is_read=False
        )
        
        session.add(notification)
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"❌ Notification error: {e}")
        return False
    
    finally:
        session.close()


def get_user_notifications(
    user_id: int,
    unread_only: bool = False,
    limit: int = 50
) -> List[Notification]:
    """
    Get notifications for a user.
    
    Args:
        user_id: User ID
        unread_only: If True, only return unread notifications
        limit: Maximum number of notifications
        
    Returns:
        List of Notification objects
    """
    session = get_db_session()
    
    try:
        query = session.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        return notifications
    
    finally:
        session.close()


def get_unread_count(user_id: int) -> int:
    """
    Get count of unread notifications for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        int: Number of unread notifications
    """
    session = get_db_session()
    
    try:
        count = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        return count
    
    finally:
        session.close()


def mark_as_read(notification_id: int) -> bool:
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        bool: True if successful
    """
    session = get_db_session()
    
    try:
        notification = session.query(Notification).get(notification_id)
        
        if notification:
            notification.is_read = True
            session.commit()
            return True
        
        return False
    
    finally:
        session.close()


def mark_all_as_read(user_id: int) -> int:
    """
    Mark all notifications as read for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        int: Number of notifications marked as read
    """
    session = get_db_session()
    
    try:
        count = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        session.commit()
        return count
    
    finally:
        session.close()


def delete_notification(notification_id: int) -> bool:
    """
    Delete a notification.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        bool: True if deleted successfully
    """
    session = get_db_session()
    
    try:
        notification = session.query(Notification).get(notification_id)
        
        if notification:
            session.delete(notification)
            session.commit()
            return True
        
        return False
    
    finally:
        session.close()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def notify_grade_added(student_id: int, subject: str, score: float, max_score: int):
    """
    Send notification when a new grade is added.
    
    Args:
        student_id: Student user ID
        subject: Subject name
        score: Score received
        max_score: Maximum possible score
    """
    percentage = (score / max_score) * 100
    
    title = f"📝 درجة جديدة | New Grade"
    message = f"تم إضافة درجة جديدة في {subject}: {score}/{max_score} ({percentage:.0f}%)"
    
    create_notification(
        user_id=student_id,
        title=title,
        message=message,
        notification_type=NotificationTypes.GRADE
    )


def notify_password_reset(user_id: int):
    """
    Send notification when password is reset by admin.
    
    Args:
        user_id: User ID
    """
    create_notification(
        user_id=user_id,
        title="🔑 Password Reset | إعادة تعيين كلمة المرور",
        message="تم إعادة تعيين كلمة المرور الخاصة بك بواسطة المسؤول. يرجى تسجيل الدخول بكلمة المرور الجديدة.",
        notification_type=NotificationTypes.WARNING
    )
