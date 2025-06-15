import pytest
import os
import tempfile
import io
from src.app_production import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Set test configuration
    app.config['TESTING'] = True
    app.config['REDIS_HOST'] = 'localhost'
    app.config['REDIS_PORT'] = 6379
    app.config['REDIS_DB'] = 1  # Use different DB for tests
    app.config['SESSION_TTL'] = 300  # 5 minutes for tests
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    csv_content = """id,age,income,category,satisfaction,region
1,25,45000,A,4.2,North
2,30,52000,B,3.8,South
3,35,68000,A,4.5,East
4,28,48000,C,3.2,West
5,42,75000,B,4.1,North
"""
    return io.BytesIO(csv_content.encode('utf-8'))


@pytest.fixture
def invalid_csv_file():
    """Create an invalid CSV file for testing."""
    csv_content = "invalid,csv,content\nno,proper,headers"
    return io.BytesIO(csv_content.encode('utf-8'))


@pytest.fixture
def sample_analyzer_id():
    """Return a valid UUID for testing."""
    return "550e8400-e29b-41d4-a716-446655440000"
