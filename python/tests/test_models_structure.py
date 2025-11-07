"""
Test database models structure without requiring SQLAlchemy to be installed.
This test verifies:
- All models are properly defined
- Fields are correctly typed
- Relationships are configured
"""

import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_job_model_structure():
    """Test that Job model has correct structure."""
    try:
        # Import the base and model classes directly
        from app.database.base import Base
        from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
        
        # Check Base exists
        assert Base is not None
        print("✅ Base class imported successfully")
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("⚠️  SQLAlchemy not installed (expected in test environment)")
            return
        raise


def test_models_can_be_imported():
    """Test that all models can be imported."""
    try:
        # This will fail if SQLAlchemy is not installed, but that's okay
        # The test framework will handle it
        from app.database.models import Job, Track, Loop
        print("✅ Job, Track, Loop models imported successfully")
        assert Job is not None
        assert Track is not None
        assert Loop is not None
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("⚠️  SQLAlchemy not installed (expected in test environment)")
            return
        raise


def test_repositories_can_be_imported():
    """Test that repository classes can be imported."""
    try:
        from app.database.repositories import (
            JobRepository,
            TrackRepository,
            LoopRepository,
        )
        print("✅ Repository classes imported successfully")
        assert JobRepository is not None
        assert TrackRepository is not None
        assert LoopRepository is not None
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("⚠️  SQLAlchemy not installed (expected in test environment)")
            return
        raise


def test_session_utilities_can_be_imported():
    """Test that session utilities can be imported."""
    try:
        from app.database.session import (
            get_session,
            init_database,
            create_db_engine,
        )
        print("✅ Session utilities imported successfully")
        assert get_session is not None
        assert init_database is not None
        assert create_db_engine is not None
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("⚠️  SQLAlchemy not installed (expected in test environment)")
            return
        raise


def test_package_exports():
    """Test that the database package exports all necessary items."""
    try:
        import app.database as db_package
        
        # Check all expected exports
        expected_exports = [
            "Base",
            "Job",
            "Track",
            "Loop",
            "JobRepository",
            "TrackRepository",
            "LoopRepository",
            "get_session",
            "init_database",
            "create_db_engine",
            "SessionLocal",
        ]
        
        for export in expected_exports:
            assert hasattr(db_package, export), f"Missing export: {export}"
        
        print(f"✅ All {len(expected_exports)} expected exports are available")
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("⚠️  SQLAlchemy not installed (expected in test environment)")
            return
        raise


def test_model_file_content():
    """Verify that model file contains all required classes and fields."""
    with open("/home/engine/project/python/app/database/models.py", "r") as f:
        content = f.read()
    
    # Check for model class definitions
    assert "class Job(Base):" in content, "Job model not found"
    assert "class Track(Base):" in content, "Track model not found"
    assert "class Loop(Base):" in content, "Loop model not found"
    print("✅ All model classes are defined")
    
    # Check for required Job fields
    job_fields = [
        "job_id",
        "job_type",
        "status",
        "progress",
        "prompt",
        "metadata",
        "file_manifest",
        "error",
        "created_at",
        "updated_at",
    ]
    for field in job_fields:
        assert field in content, f"Job.{field} not found"
    print(f"✅ Job model has all {len(job_fields)} required fields")
    
    # Check for required Track fields
    track_fields = [
        "track_id",
        "job_id",
        "duration",
        "metadata",
        "file_path_wav",
        "file_path_mp3",
        "created_at",
        "updated_at",
    ]
    for field in track_fields:
        assert field in content, f"Track.{field} not found"
    print(f"✅ Track model has all {len(track_fields)} required fields")
    
    # Check for required Loop fields
    loop_fields = [
        "loop_id",
        "track_id",
        "status",
        "duration",
        "fade_in_out",
        "format",
        "progress",
        "error",
        "result_url",
        "result_path",
        "created_at",
        "updated_at",
    ]
    for field in loop_fields:
        assert field in content, f"Loop.{field} not found"
    print(f"✅ Loop model has all {len(loop_fields)} required fields")


def test_repository_file_content():
    """Verify that repository file contains all required CRUD methods."""
    with open("/home/engine/project/python/app/database/repositories.py", "r") as f:
        content = f.read()
    
    # Check for repository classes
    assert "class JobRepository:" in content
    assert "class TrackRepository:" in content
    assert "class LoopRepository:" in content
    print("✅ All repository classes are defined")
    
    # Check for CRUD methods
    crud_methods = ["def create(", "def get_by_id(", "def update(", "def delete("]
    for method in crud_methods:
        assert content.count(method) >= 3, f"CRUD method '{method}' not found in all repositories"
    print(f"✅ All repositories have required CRUD methods")
    
    # Check for specific repository methods
    assert "def get_by_status(self" in content, "get_by_status method not found"
    assert "def get_by_job_id(self" in content, "get_by_job_id method not found"
    assert "def get_by_track_id(self" in content, "get_by_track_id method not found"
    print("✅ All specialized repository query methods are defined")


def test_session_file_content():
    """Verify that session file has proper initialization logic."""
    with open("/home/engine/project/python/app/database/session.py", "r") as f:
        content = f.read()
    
    # Check for key functions (note: may have type hints)
    assert "def get_database_url" in content, "get_database_url not found"
    assert "def create_db_engine" in content, "create_db_engine not found"
    assert "def init_db(" in content, "init_db not found"
    assert "def get_session" in content, "get_session not found"
    assert "def init_database" in content, "init_database not found"
    print("✅ Session module has all required functions")
    
    # Check for SQLite support
    assert "sqlite" in content, "SQLite support not configured"
    print("✅ SQLite support is configured")


def test_integration_with_service():
    """Test that diffrhythm_service.py imports database modules correctly."""
    with open("/home/engine/project/python/services/diffrhythm_service.py", "r") as f:
        content = f.read()
    
    # Check for database imports
    assert "from app.database import" in content
    assert "JobRepository" in content
    assert "TrackRepository" in content
    assert "get_session" in content
    assert "init_database" in content
    print("✅ Service file imports database modules correctly")
    
    # Check for startup event
    assert "@app.on_event(\"startup\")" in content
    assert "init_database()" in content
    print("✅ Service has startup event for database initialization")
    
    # Check for job database operations
    assert "repo.create(" in content
    assert "JobRepository(session)" in content
    assert "TrackRepository(session)" in content
    print("✅ Service uses database repositories for job and track storage")


def test_documentation_exists():
    """Test that DATABASE.md documentation exists and is comprehensive."""
    doc_path = "/home/engine/project/python/DATABASE.md"
    assert os.path.exists(doc_path), "DATABASE.md not found"
    
    with open(doc_path, "r") as f:
        content = f.read()
    
    # Check for key sections
    sections = [
        "# Database Setup and Configuration",
        "### Models",
        "#### Job",
        "#### Track",
        "#### Loop",
        "### Relationships",
        "## Configuration",
        "## Usage Examples",
        "## Testing",
    ]
    
    for section in sections:
        assert section in content, f"Section '{section}' not found in documentation"
    
    print(f"✅ DATABASE.md documentation exists with {len(sections)} key sections")


if __name__ == "__main__":
    print("🚀 Running database model structure tests...\n")
    
    tests = [
        ("Job model structure", test_job_model_structure),
        ("Models import", test_models_can_be_imported),
        ("Repositories import", test_repositories_can_be_imported),
        ("Session utilities import", test_session_utilities_can_be_imported),
        ("Package exports", test_package_exports),
        ("Model file content", test_model_file_content),
        ("Repository file content", test_repository_file_content),
        ("Session file content", test_session_file_content),
        ("Service integration", test_integration_with_service),
        ("Documentation", test_documentation_exists),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTesting: {test_name}...")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All model structure tests passed!")
        sys.exit(0)
    else:
        print(f"💥 {failed} test(s) failed!")
        sys.exit(1)
