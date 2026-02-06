import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test."""
    # Store original activities
    original_activities = {
        key: {
            "description": val["description"],
            "schedule": val["schedule"],
            "max_participants": val["max_participants"],
            "participants": val["participants"].copy()
        }
        for key, val in activities.items()
    }
    
    yield
    
    # Restore original activities
    activities.clear()
    activities.update(original_activities)
