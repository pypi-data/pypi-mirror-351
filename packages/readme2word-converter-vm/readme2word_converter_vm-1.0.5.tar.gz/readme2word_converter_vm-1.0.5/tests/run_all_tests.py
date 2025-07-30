#!/usr/bin/env python3
"""
Comprehensive test runner for README to Word Converter

This script runs all test suites and provides detailed reporting:
- Unit tests for converter functionality
- UI component tests
- Integration tests
- Mermaid diagram tests
- Performance benchmarks
"""

import importlib.util
import sys
import time
import unittest
from pathlib import Path

from tests.test_converter import run_converter_tests
from tests.test_integration import run_integration_tests
from tests.test_mermaid import run_mermaid_tests
from tests.test_ui import run_ui_tests

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import test modules


class TestRunner:
    """Comprehensive test runner with reporting"""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.total_time = 0

    def print_header(self):
        """Print test suite header"""
        print("🧪 README to Word Converter - Test Suite")
        print("=" * 60)
        print("Running comprehensive tests for all components...")
        print()

    def print_separator(self):
        """Print section separator"""
        print("\n" + "─" * 60 + "\n")

    def run_test_suite(self, name, test_function):
        """Run a test suite and record results"""
        print(f"🔍 Starting {name}...")
        start_time = time.time()

        try:
            success = test_function()
            duration = time.time() - start_time

            self.results[name] = {
                "success": success,
                "duration": duration,
                "error": None,
            }

            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {name} completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            self.results[name] = {
                "success": False,
                "duration": duration,
                "error": str(e),
            }
            print(f"❌ ERROR - {name} failed with error: {e}")

        self.print_separator()

    def run_all_tests(self):
        """Run all test suites"""
        self.start_time = time.time()
        self.print_header()

        # Define test suites
        test_suites = [
            ("Mermaid Diagram Tests", run_mermaid_tests),
            ("Converter Unit Tests", run_converter_tests),
            ("UI Component Tests", run_ui_tests),
            ("Integration Tests", run_integration_tests),
        ]

        # Run each test suite
        for name, test_function in test_suites:
            self.run_test_suite(name, test_function)

        self.total_time = time.time() - self.start_time

    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"📈 Overall Results:")
        print(f"   Total Test Suites: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⏱️  Total Time: {self.total_time:.2f}s")
        print()

        # Detailed results
        print("📋 Detailed Results:")
        for name, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result["duration"]
            print(f"   {status} {name:<25} ({duration:.2f}s)")

            if result["error"]:
                print(f"      Error: {result['error']}")

        print()

        # Performance analysis
        print("⚡ Performance Analysis:")
        sorted_results = sorted(
            self.results.items(), key=lambda x: x[1]["duration"], reverse=True
        )

        for name, result in sorted_results:
            duration = result["duration"]
            percentage = (duration / self.total_time) * 100
            print(f"   {name:<25} {duration:>6.2f}s ({percentage:>5.1f}%)")

        print()

        # Final status
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! 🎉")
            print("The README to Word Converter is working perfectly!")
        else:
            print(f"⚠️  {failed_tests} TEST SUITE(S) FAILED")
            print("Please review the failed tests and fix any issues.")

        print("\n" + "=" * 60)

        return failed_tests == 0


def run_quick_tests():
    """Run a quick subset of tests for development"""
    print("🚀 Quick Test Mode")
    print("=" * 40)

    # Run only essential tests
    quick_suites = [
        ("Mermaid Tests", run_mermaid_tests),
        ("Converter Tests", run_converter_tests),
    ]

    all_passed = True
    total_time = time.time()

    for name, test_function in quick_suites:
        print(f"\n🔍 Running {name}...")
        start = time.time()

        try:
            success = test_function()
            duration = time.time() - start
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status} - {duration:.2f}s")

            if not success:
                all_passed = False

        except Exception as e:
            print(f"❌ ERROR - {e}")
            all_passed = False

    total_duration = time.time() - total_time
    print(f"\n⏱️  Quick tests completed in {total_duration:.2f}s")

    if all_passed:
        print("✅ All quick tests passed!")
    else:
        print("❌ Some quick tests failed!")

    return all_passed


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies...")

    required_modules = ["streamlit", "docx", "markdown", "bs4", "requests", "PIL"]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (missing)")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Please install missing dependencies with:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are available!")
        return True


def main():
    """Main test runner function"""
    import argparse

    parser = argparse.ArgumentParser(description="README to Word Converter Test Suite")
    parser.add_argument(
        "--quick", action="store_true", help="Run only quick essential tests"
    )
    parser.add_argument(
        "--check-deps", action="store_true", help="Check dependencies only"
    )

    args = parser.parse_args()

    if args.check_deps:
        success = check_dependencies()
        sys.exit(0 if success else 1)

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Cannot run tests due to missing dependencies!")
        sys.exit(1)

    print()  # Add spacing

    if args.quick:
        success = run_quick_tests()
    else:
        runner = TestRunner()
        runner.run_all_tests()
        success = runner.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
