import pytest
from sqlalchemy import text
from app.db.database import get_db, Base, engine

def test_database_connection():
    """Test that we can connect to the database and execute a simple query"""
    # Get a database session
    db = next(get_db())
    
    try:
        # Execute a simple query
        result = db.execute(text("SELECT 1"))
        value = result.scalar()
        
        # Check that the query returned the expected result
        assert value == 1
    finally:
        db.close()

def test_create_tables():
    """Test that we can create database tables"""
    # Drop all tables first
    Base.metadata.drop_all(bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get a database session
    db = next(get_db())
    
    try:
        # Check that tables exist by querying information schema
        # This is SQLite specific
        result = db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        tables = [row[0] for row in result]
        
        # Check that our main tables exist
        assert "projects" in tables
        assert "construction_inspections" in tables
        assert "inspection_photos" in tables
    finally:
        db.close()
