import pytest
from sqlalchemy import text
from app.db.database import Base
from app.tests.conftest import engine, TestingSessionLocal

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """Test that we can connect to the database and execute a simple query (in-memory)"""
    db = next(get_test_db())
    try:
        result = db.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1
    finally:
        db.close()

def test_create_tables():
    """Test that we can create database tables (in-memory)"""
    # Drop all tables first (should be empty for in-memory)
    Base.metadata.drop_all(bind=engine)
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = next(get_test_db())
    try:
        result = db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        tables = [row[0] for row in result]
        assert "projects" in tables
        assert "construction_inspections" in tables
        assert "inspection_photos" in tables
    finally:
        db.close()
