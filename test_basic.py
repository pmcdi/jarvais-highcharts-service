#!/usr/bin/env python3
"""
Basic syntax and import test for the application.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that we can import the main modules."""
    try:
        # Test basic Python syntax
        print("Testing basic Python syntax...")
        from src.app_production import validate_analyzer_id, allowed_file
        print("✓ Basic imports work")
        
        # Test validation functions
        print("Testing validation functions...")
        assert validate_analyzer_id("550e8400-e29b-41d4-a716-446655440000") == True
        assert validate_analyzer_id("invalid") == False
        assert allowed_file("test.csv") == True
        assert allowed_file("test.txt") == False
        print("✓ Validation functions work")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_docker_compose_structure():
    """Test docker-compose.yaml structure."""
    try:
        import yaml
        print("Testing docker-compose.yaml structure...")
        
        with open('docker-compose.yaml', 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Check required services
        assert 'services' in compose_data
        assert 'jarvais-api' in compose_data['services']
        assert 'redis' in compose_data['services']
        
        # Check API service configuration
        api_service = compose_data['services']['jarvais-api']
        assert 'ports' in api_service
        assert 'environment' in api_service
        assert 'depends_on' in api_service
        assert 'redis' in api_service['depends_on']
        
        # Check Redis service
        redis_service = compose_data['services']['redis']
        assert 'image' in redis_service
        assert 'redis' in redis_service['image']
        
        print("✓ Docker Compose structure is valid")
        return True
    except Exception as e:
        print(f"✗ Docker Compose test failed: {e}")
        return False

def test_dockerfile():
    """Test Dockerfile structure."""
    try:
        print("Testing Dockerfile structure...")
        
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        # Check required instructions
        assert 'FROM python:' in dockerfile_content
        assert 'WORKDIR /app' in dockerfile_content
        assert 'COPY requirements.txt' in dockerfile_content
        assert 'EXPOSE 5000' in dockerfile_content
        
        print("✓ Dockerfile structure is valid")
        return True
    except Exception as e:
        print(f"✗ Dockerfile test failed: {e}")
        return False

def test_requirements():
    """Test requirements.txt structure."""
    try:
        print("Testing requirements.txt...")
        
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check required packages
        required_packages = ['flask', 'pandas', 'redis', 'flask-cors']
        for package in required_packages:
            assert package in requirements.lower(), f"Missing package: {package}"
        
        print("✓ Requirements.txt is valid")
        return True
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Starting basic tests...")
    
    tests = [
        test_imports,
        test_docker_compose_structure,
        test_dockerfile,
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All basic tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
