"""Marker-based test runner for different test categories."""

import subprocess
import sys


def run_unit_tests():
    """Run only unit tests (fast, no external dependencies)."""
    print("Running UNIT tests...")
    result = subprocess.run(
        ["pytest", "-m", "unit", "-v"],
        cwd="backend",
    )
    return result.returncode


def run_integration_tests():
    """Run integration tests (may require services)."""
    print("Running INTEGRATION tests...")
    result = subprocess.run(
        ["pytest", "-m", "integration", "-v"],
        cwd="backend",
    )
    return result.returncode


def run_security_tests():
    """Run security-focused tests."""
    print("Running SECURITY tests...")
    result = subprocess.run(
        ["pytest", "-m", "security or auth", "-v"],
        cwd="backend",
    )
    return result.returncode


def run_fast_tests():
    """Run all tests except slow ones."""
    print("Running FAST tests (excluding slow)...")
    result = subprocess.run(
        ["pytest", "-m", "not slow", "-v"],
        cwd="backend",
    )
    return result.returncode


def run_all_tests():
    """Run all tests with coverage."""
    print("Running ALL tests with coverage...")
    result = subprocess.run(
        ["pytest", "-v", "--cov=app", "--cov-report=html"],
        cwd="backend",
    )
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py [unit|integration|security|fast|all]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "unit":
        exit_code = run_unit_tests()
    elif command == "integration":
        exit_code = run_integration_tests()
    elif command == "security":
        exit_code = run_security_tests()
    elif command == "fast":
        exit_code = run_fast_tests()
    elif command == "all":
        exit_code = run_all_tests()
    else:
        print(f"Unknown command: {command}")
        exit_code = 1

    sys.exit(exit_code)
