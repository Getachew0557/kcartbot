#!/usr/bin/env python3
"""Test runner for KcartBot."""

import subprocess
import sys
import os

def run_tests():
    """Run all tests."""
    print("🧪 Running KcartBot Test Suite")
    print("=" * 50)
    
    # Change to project root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--cov=src",
            "--cov-report=term-missing"
        ], check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest pytest-cov")
        return False

def run_linting():
    """Run code linting."""
    print("\n🔍 Running Code Linting")
    print("=" * 30)
    
    try:
        # Run flake8
        subprocess.run([sys.executable, "-m", "flake8", "src/", "tests/"], check=True)
        print("✅ Flake8 passed!")
        
        # Run black check
        subprocess.run([sys.executable, "-m", "black", "--check", "src/", "tests/"], check=True)
        print("✅ Black formatting check passed!")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Linting failed!")
        return False
    except FileNotFoundError:
        print("❌ Linting tools not found. Please install with: pip install flake8 black")
        return False

if __name__ == "__main__":
    print("🚀 KcartBot CI/CD Test Runner")
    print("=" * 50)
    
    # Run tests
    tests_passed = run_tests()
    
    # Run linting
    linting_passed = run_linting()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 20)
    print(f"Tests: {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"Linting: {'✅ PASSED' if linting_passed else '❌ FAILED'}")
    
    if tests_passed and linting_passed:
        print("\n🎉 All checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n⚠️  Some checks failed. Please fix the issues.")
        sys.exit(1)
