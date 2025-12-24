# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Database Connection | منصة زاد - اتصال قاعدة البيانات
===============================================================================
Database setup, session management, and initialization.
"""

from werkzeug.security import generate_password_hash
from models import Base, engine, SessionLocal, get_db_session, User, School, init_db as create_tables


def init_db():
    """Initialize database and create tables."""
    print("🔧 Initializing database...")
    create_tables()


def create_default_super_admin():
    """Create default super admin user if not exists."""
    session = get_db_session()
    
    try:
        existing = session.query(User).filter(User.email == "admin@zad.edu").first()
        
        if not existing:
            super_admin = User(
                email="admin@zad.edu",
                full_name="ZAD Super Admin",
                hashed_password=generate_password_hash("admin123"),
                role="super_admin",
                school_id=None
            )
            session.add(super_admin)
            session.commit()
            print("✅ Default super admin created: admin@zad.edu / admin123")
        else:
            print("ℹ️ Super admin already exists.")
    
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating super admin: {e}")
    
    finally:
        session.close()


# Re-export for convenience
__all__ = ['init_db', 'get_db_session', 'create_default_super_admin']