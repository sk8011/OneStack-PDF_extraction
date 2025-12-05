"""
Quick Test Script
Tests basic functionality without running the full server
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError:
        print("✗ FastAPI - Run: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn")
    except ImportError:
        print("✗ Uvicorn - Run: pip install uvicorn")
        return False
    
    try:
        import pdfplumber
        print("✓ pdfplumber")
    except ImportError:
        print("✗ pdfplumber - Run: pip install pdfplumber")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy")
    except ImportError:
        print("✗ SQLAlchemy - Run: pip install sqlalchemy")
        return False
    
    try:
        import pandas
        print("✓ Pandas")
    except ImportError:
        print("✗ Pandas - Run: pip install pandas")
        return False
    
    return True


def test_modules():
    """Test if local modules can be imported"""
    print("\nTesting local modules...")
    
    try:
        import config
        print("✓ config.py")
    except ImportError as e:
        print(f"✗ config.py - {e}")
        return False
    
    try:
        import pdf_extractor
        print("✓ pdf_extractor.py")
    except ImportError as e:
        print(f"✗ pdf_extractor.py - {e}")
        return False
    
    try:
        import database
        print("✓ database.py")
    except ImportError as e:
        print(f"✗ database.py - {e}")
        return False
    
    return True


def test_database():
    """Test database creation"""
    print("\nTesting database...")
    
    try:
        from database import DynamicDatabaseManager
        
        db = DynamicDatabaseManager()
        
        # Test table creation
        sample_data = {
            "name": "Test",
            "amount": 100.50,
            "quantity": 5
        }
        
        db.create_or_update_table("test_table", sample_data)
        print("✓ Database table creation works")
        
        # Test data insertion
        db.insert_data("test_table", [sample_data])
        print("✓ Data insertion works")
        
        # Test data retrieval
        data = db.get_all_data("test_table")
        if len(data) > 0:
            print("✓ Data retrieval works")
        
        return True
    
    except Exception as e:
        print(f"✗ Database test failed - {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("PDF Extraction System - Quick Test")
    print("=" * 50)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
        print("\n⚠️  Some packages are missing. Install them with:")
        print("   pip install -r requirements.txt")
    
    if not test_modules():
        all_passed = False
    
    if all_passed:
        if not test_database():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Ready to run.")
        print("\nStart the server with:")
        print("   python main.py")
        print("\nThen open: http://localhost:8000")
    else:
        print("❌ Some tests failed. Fix the issues above.")
    print("=" * 50)
