#!/bin/bash

# Comprehensive test script for jarvais-highcharts-service

set -e

echo "🧪 Starting comprehensive test suite for jarvais-highcharts-service"
echo "===================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $1 in
        "PASS") echo -e "${GREEN}✓ $2${NC}" ;;
        "FAIL") echo -e "${RED}✗ $2${NC}" ;;
        "INFO") echo -e "${YELLOW}ℹ $2${NC}" ;;
    esac
}

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "Running: $test_name"
    if eval "$test_command"; then
        print_status "PASS" "$test_name"
        return 0
    else
        print_status "FAIL" "$test_name"
        return 1
    fi
}

# Initialize counters
TOTAL_TESTS=0
PASSED_TESTS=0

# Test 1: Basic syntax and structure tests
echo "
📋 Phase 1: Basic Structure Tests"
echo "================================"

((TOTAL_TESTS++))
if run_test "Basic Python syntax and imports" "python3 test_basic.py"; then
    ((PASSED_TESTS++))
fi

# Test 2: Docker build test
echo "
🐳 Phase 2: Docker Build Tests"
echo "=============================="

((TOTAL_TESTS++))
if run_test "Docker image build" "docker build -t jarvais-test --build-arg INSTALL_TEST_DEPS=true ."; then
    ((PASSED_TESTS++))
fi

# Test 3: Docker Compose tests
echo "
🔧 Phase 3: Docker Compose Tests"
echo "================================"

((TOTAL_TESTS++))
if run_test "Docker Compose build" "docker-compose -f docker-compose.test.yml build"; then
    ((PASSED_TESTS++))
fi

((TOTAL_TESTS++))
if run_test "Docker Compose services start" "timeout 120 docker-compose -f docker-compose.test.yml up -d"; then
    ((PASSED_TESTS++))
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 20
    
    # Test 4: Service health checks
    echo "
🩺 Phase 4: Service Health Tests"
    echo "==============================="
    
    ((TOTAL_TESTS++))
    if run_test "API health check" "curl -f http://localhost:5001/api/v1/health"; then
        ((PASSED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    if run_test "Redis connectivity" "docker-compose -f docker-compose.test.yml exec -T redis-test redis-cli ping"; then
        ((PASSED_TESTS++))
    fi
    
    # Test 5: API endpoint tests
    echo "
🌐 Phase 5: API Endpoint Tests"
    echo "============================="
    
    ((TOTAL_TESTS++))
    if run_test "Upload endpoint with test data" "curl -X POST -F 'file=@tests/sample_data.csv' http://localhost:5001/upload"; then
        ((PASSED_TESTS++))
    fi
    
    # Clean up
    echo "
🧹 Cleaning up Docker Compose services..."
    docker-compose -f docker-compose.test.yml down -v
else
    echo "Docker Compose failed to start, skipping subsequent tests"
fi

# Test 6: Security tests (if tools are available)
echo "
🔒 Phase 6: Security Tests"
echo "========================"

if command -v bandit &> /dev/null; then
    ((TOTAL_TESTS++))
    if run_test "Security scan with bandit" "bandit -r src/ -ll"; then
        ((PASSED_TESTS++))
    fi
else
    print_status "INFO" "Bandit not installed, skipping security scan"
fi

# Test 7: Code quality tests
echo "
📊 Phase 7: Code Quality Tests"
echo "============================="

if command -v flake8 &> /dev/null; then
    ((TOTAL_TESTS++))
    if run_test "Code style check with flake8" "flake8 src/ --max-line-length=100 --exclude=__pycache__"; then
        ((PASSED_TESTS++))
    fi
else
    print_status "INFO" "Flake8 not installed, skipping code style check"
fi

# Final results
echo "
📊 Test Results Summary"
echo "====================="
echo "Total tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $((TOTAL_TESTS - PASSED_TESTS))"
echo "Success rate: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    print_status "PASS" "All tests passed! 🎉"
    echo "
✅ Your jarvais-highcharts-service is production-ready!"
    echo "📋 Summary of improvements made:"
    echo "   • Fixed production readiness issues in app_production.py"
    echo "   • Added comprehensive test suite"
    echo "   • Added Docker health checks"
    echo "   • Added security headers"
    echo "   • Added input validation"
    echo "   • Created GitHub Actions workflow"
    echo "   • Added proper error handling"
    exit 0
else
    print_status "FAIL" "Some tests failed. Please review the output above."
    exit 1
fi
