# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Database Models | منصة زاد - نماذج قاعدة البيانات
==========================================================================
SQLAlchemy ORM models for Multi-Tenant SaaS LMS.

Tables:
- School: مدرسة - Multi-tenant isolation entity
- User: مستخدم - Roles: super_admin, school_admin, teacher, student
- Grade: درجة - Student grades/scores
- Resource: مورد - PDF Library resources (uploaded by teachers)
- OnlineSession: جلسة أونلاين - Zoom/online classes
"""

import datetime
import enum
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Enums for backward compatibility
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"


class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

# =============================================================================
# DATABASE SETUP
# =============================================================================

DATABASE_URL = "sqlite:///zad_edu.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session():
    """Get a new database session."""
    return SessionLocal()


# =============================================================================
# MODEL DEFINITIONS
# =============================================================================

class School(Base):
    """المدرسة - School entity for multi-tenant isolation"""
    __tablename__ = 'schools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    subscription_plan = Column(String(50), default='free')  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="school", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="school", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="school", cascade="all, delete-orphan")
    online_sessions = relationship("OnlineSession", back_populates="school", cascade="all, delete-orphan")


class User(Base):
    """المستخدم - User entity with roles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='student')  # super_admin, school_admin, teacher, student
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Key (nullable for super_admin)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="users")
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="teacher", cascade="all, delete-orphan")
    online_sessions = relationship("OnlineSession", back_populates="teacher", cascade="all, delete-orphan")


class Grade(Base):
    """الدرجة - Grade/Score record"""
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)
    max_score = Column(Integer, default=100)
    subject = Column(String(100), nullable=False)
    feedback = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys (Multi-Tenancy: school_id is REQUIRED)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="grades")
    school = relationship("School", back_populates="grades")


class Resource(Base):
    """
    المورد - PDF/Document Library Resource
    Uploaded by teachers for students to access.
    Multi-tenancy: Each resource belongs to a school.
    """
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Local file path or URL to PDF/document
    url = Column(String(500), nullable=True)        # External URL (alternative to file_path)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=True)  # e.g., "Grade 5", "10th", "University"
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys (Multi-Tenancy)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    teacher = relationship("User", back_populates="resources")
    school = relationship("School", back_populates="resources")


class OnlineSession(Base):
    """
    جلسة أونلاين - Online/Zoom Class Session
    Scheduled by teachers for students to join.
    Multi-tenancy: Each session belongs to a school.
    """
    __tablename__ = 'online_sessions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    zoom_link = Column(String(500), nullable=False)  # Zoom/Meet/Teams link
    scheduled_time = Column(DateTime, nullable=False)
    subject = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys (Multi-Tenancy)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    teacher = relationship("User", back_populates="online_sessions")
    school = relationship("School", back_populates="online_sessions")


class ParentChild(Base):
    """
    علاقة ولي الأمر بالطفل - Parent-Child Relationship
    Links parents to their children for proper access control.
    CRITICAL: Without this, parents could see other children's grades.
    """
    __tablename__ = 'parent_children'
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    child_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    parent = relationship("User", foreign_keys=[parent_id], backref="children_links")
    child = relationship("User", foreign_keys=[child_id], backref="parent_links")


class Subscription(Base):
    """
    اشتراك - Subscription for school billing
    Tracks subscription status for each school.
    """
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    plan = Column(String(50), default='free')  # free, pro, enterprise
    is_active = Column(Boolean, default=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    school = relationship("School", backref="subscriptions")


class Classroom(Base):
    """الفصل الدراسي - Classroom for organizing students"""
    __tablename__ = 'classrooms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    school = relationship("School", backref="classrooms")


class Enrollment(Base):
    """تسجيل الطالب - Student enrollment in classroom"""
    __tablename__ = 'enrollments'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)


class Assignment(Base):
    """المهمة - Assignment/Homework"""
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Submission(Base):
    """تسليم المهمة - Assignment submission"""
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)


class Attendance(Base):
    """الحضور - Student attendance"""
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(20), default='present')  # present, absent, late, excused
    notes = Column(Text, nullable=True)


class AuditLog(Base):
    """سجل النشاط - Audit log for tracking actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class Notification(Base):
    """الإشعار - User notification"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50), default='info')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Document(Base):
    """المستند - Document for RAG/AI tutor"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class QualityKPI(Base):
    """
    مؤشرات الجودة - Quality Key Performance Indicators
    Tracks education quality metrics and benchmarks for each school.
    Supports both global standards and custom school-defined KPIs.
    """
    __tablename__ = 'quality_kpis'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # e.g., "Student-Teacher Ratio"
    metric_type = Column(String(50), default='School_Custom')  # 'Global_Standard', 'School_Custom'
    current_value = Column(Float, nullable=False, default=0)
    target_value = Column(Float, nullable=False, default=100)
    unit = Column(String(20), default='%')  # '%', 'Ratio', 'Score', 'Count'
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # 'Academic', 'Infrastructure', 'Digital'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign Key (Multi-Tenancy)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    
    # Relationships
    school = relationship("School", backref="quality_kpis")


# =============================================================================
# TABLE CREATION
# =============================================================================

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created.")


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == "__main__":
    init_db()
    print("✅ Models loaded successfully.")
