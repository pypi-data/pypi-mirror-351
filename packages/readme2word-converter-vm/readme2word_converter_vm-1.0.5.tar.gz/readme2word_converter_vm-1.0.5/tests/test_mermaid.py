#!/usr/bin/env python3
"""
Mermaid Diagram Test Suite

This script tests the Mermaid diagram conversion functionality:
- API connectivity to mermaid.ink
- Various diagram types (flowchart, sequence, class, state)
- Different themes (default, neutral, dark, forest)
- Error handling for invalid diagrams
- Image generation and validation
"""

import base64
import os
import sys
import time
from pathlib import Path

import requests

from readme2word.converter import ReadmeToWordConverter

# Add parent directory to path to import converter
sys.path.append(str(Path(__file__).parent.parent))


def test_mermaid_api_connectivity():
    """Test if Mermaid.ink API is accessible"""
    print("\n🌐 Testing Mermaid API connectivity...")

    # Simple test diagram
    test_diagram = "graph TD; A-->B"
    encoded = base64.urlsafe_b64encode(test_diagram.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{encoded}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print("   ✅ API connectivity successful")
            print(f"   📊 Response size: {len(response.content)} bytes")
            assert True  # Test passes
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            assert False, f"API returned status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        print(f"   ❌ API connectivity failed: {e}")
        assert False, f"API connectivity failed: {e}"


def test_diagram_types():
    """Test various Mermaid diagram types"""
    print("\n🎨 Testing different diagram types...")

    diagrams = {
        "Simple Flowchart": """
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
""",
        "Sequence Diagram": """
sequenceDiagram
    participant Alice
    participant Bob
    participant John

    Alice->>Bob: Hello Bob, how are you?
    Bob-->>John: How about you John?
    Bob--x Alice: I am good thanks!
    Bob-x John: I am good thanks!
    Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.

    Bob-->Alice: Checking with John...
    Alice->John: Yes... John, how are you?
""",
        "Class Diagram": """
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +String color
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
""",
        "State Diagram": """
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
""",
    }

    converter = ReadmeToWordConverter()
    converter.set_debug_mode(True)

    success_count = 0
    total_count = len(diagrams)

    for diagram_name, diagram_code in diagrams.items():
        print(f"\n   🔍 Testing {diagram_name}...")

        # Create test markdown with the diagram
        test_content = f"""# {diagram_name} Test

```mermaid
{diagram_code.strip()}
```

This document tests the {diagram_name.lower()} conversion.
"""

        try:
            start_time = time.time()
            output_path = converter.convert(
                test_content,
                f"test_{diagram_name.lower().replace(' ', '_')}",
                include_toc=False,
            )
            conversion_time = time.time() - start_time

            # Check if file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ {diagram_name}: SUCCESS")
                print(f"      📄 File: {output_path}")
                print(f"      📊 Size: {file_size:,} bytes")
                print(f"      ⏱️  Time: {conversion_time:.2f}s")

                # Check statistics
                stats = converter.get_conversion_stats()
                if stats["mermaid_diagrams"] > 0:
                    print(f"      🎯 Diagrams converted: {stats['mermaid_diagrams']}")
                    success_count += 1
                else:
                    print(f"      ⚠️  No diagrams were converted")
            else:
                print(f"   ❌ {diagram_name}: File not created")

        except Exception as e:
            print(f"   ❌ {diagram_name}: ERROR - {e}")

    # Assert that at least some diagrams were successful
    assert (
        success_count > 0
    ), f"No diagrams were successfully converted out of {total_count}"
    print(f"\n✅ Successfully converted {success_count}/{total_count} diagram types")


def test_theme_variations():
    """Test different Mermaid themes"""
    print("\n🎭 Testing theme variations...")

    themes = ["default", "neutral", "dark", "forest"]

    # Simple test diagram
    test_diagram = """
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
    C --> D{Success?}
    D -->|Yes| E[Complete]
    D -->|No| F[Error]
"""

    converter = ReadmeToWordConverter()
    success_count = 0
    total_count = len(themes)

    for theme in themes:
        print(f"\n   🎨 Testing {theme} theme...")

        test_content = f"""# Theme Test - {theme.title()}

```mermaid
{test_diagram.strip()}
```

Testing {theme} theme conversion.
"""

        try:
            start_time = time.time()
            output_path = converter.convert(
                test_content,
                f"test_theme_{theme}",
                include_toc=False,
                diagram_style=theme,
            )
            conversion_time = time.time() - start_time

            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ {theme.title()} theme: SUCCESS")
                print(f"      📄 File: {output_path}")
                print(f"      📊 Size: {file_size:,} bytes")
                print(f"      ⏱️  Time: {conversion_time:.2f}s")
                success_count += 1
            else:
                print(f"   ❌ {theme.title()} theme: File not created")

        except Exception as e:
            print(f"   ❌ {theme.title()} theme: ERROR - {e}")

    # Assert that at least some themes worked
    assert success_count > 0, f"No themes were successfully tested out of {total_count}"
    print(f"\n✅ Successfully tested {success_count}/{total_count} themes")


def test_error_handling():
    """Test error handling with invalid diagrams"""
    print("\n🚨 Testing error handling...")

    invalid_diagrams = {
        "Invalid Syntax": """
```mermaid
this is not valid mermaid syntax
random text here
```
""",
        "Empty Diagram": """
```mermaid

```
""",
        "Malformed Graph": """
```mermaid
graph TD
    A -->
    --> B
    C -->
```
""",
    }

    converter = ReadmeToWordConverter()
    success_count = 0
    total_count = len(invalid_diagrams)

    for test_name, invalid_content in invalid_diagrams.items():
        print(f"\n   🔍 Testing {test_name}...")

        test_content = f"""# Error Handling Test - {test_name}

{invalid_content}

This should handle the error gracefully.
"""

        try:
            output_path = converter.convert(
                test_content,
                f"test_error_{test_name.lower().replace(' ', '_')}",
                include_toc=False,
            )

            if os.path.exists(output_path):
                print(f"   ✅ {test_name}: Document created despite error")

                # Check that no diagrams were converted
                stats = converter.get_conversion_stats()
                if stats["mermaid_diagrams"] == 0:
                    print(f"   ✅ Error handled correctly (no diagrams converted)")
                    success_count += 1
                else:
                    print(
                        f"   ⚠️  Unexpected: {stats['mermaid_diagrams']} diagrams converted"
                    )
            else:
                print(f"   ❌ {test_name}: Document not created")

        except Exception as e:
            print(f"   ❌ {test_name}: Unexpected error - {e}")

    # Assert that error handling worked for at least some cases
    assert success_count > 0, f"Error handling failed for all {total_count} test cases"
    print(f"\n✅ Successfully handled errors in {success_count}/{total_count} cases")


def test_performance():
    """Test performance with multiple diagrams"""
    print("\n⚡ Testing performance with multiple diagrams...")

    # Create content with multiple diagrams
    multi_diagram_content = """# Performance Test Document

## Flowchart 1
```mermaid
graph TD
    A[Start] --> B[Process 1]
    B --> C[Process 2]
    C --> D[End]
```

## Sequence Diagram
```mermaid
sequenceDiagram
    User->>App: Request
    App->>API: Process
    API-->>App: Response
    App-->>User: Result
```

## Flowchart 2
```mermaid
graph LR
    X[Input] --> Y[Transform]
    Y --> Z[Output]
```

This document contains multiple diagrams to test performance.
"""

    converter = ReadmeToWordConverter()

    try:
        print("   🔍 Converting document with 3 diagrams...")
        start_time = time.time()

        output_path = converter.convert(
            multi_diagram_content, "test_performance_multi", include_toc=True
        )

        conversion_time = time.time() - start_time

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            stats = converter.get_conversion_stats()

            print(f"   ✅ Performance test: SUCCESS")
            print(f"      📄 File: {output_path}")
            print(f"      📊 Size: {file_size:,} bytes")
            print(f"      ⏱️  Time: {conversion_time:.2f}s")
            print(f"      🎯 Diagrams: {stats['mermaid_diagrams']}")
            print(f"      📈 Images: {stats['images']}")

            # Performance benchmarks
            if conversion_time < 30:
                print(f"      ✅ Performance: GOOD (< 30s)")
            elif conversion_time < 60:
                print(f"      ⚠️  Performance: ACCEPTABLE (< 60s)")
            else:
                print(f"      ❌ Performance: SLOW (> 60s)")

            # Assert performance is acceptable
            assert (
                conversion_time < 120
            ), f"Performance too slow: {conversion_time:.2f}s > 120s"
            assert os.path.exists(output_path), "Output file was not created"
            print(f"   ✅ Performance test passed")
        else:
            assert False, "Performance test: File not created"

    except Exception as e:
        assert False, f"Performance test: ERROR - {e}"


def run_mermaid_tests():
    """Run all Mermaid-related tests"""
    print("🧪 Mermaid Diagram Test Suite")
    print("=" * 50)

    test_results = {}

    # Test 1: API Connectivity
    try:
        test_mermaid_api_connectivity()
        test_results["api_connectivity"] = True
    except AssertionError as e:
        print(f"❌ API Connectivity failed: {e}")
        test_results["api_connectivity"] = False

    # Test 2: Diagram Types
    try:
        test_diagram_types()
        test_results["diagram_types"] = True
    except AssertionError as e:
        print(f"❌ Diagram Types failed: {e}")
        test_results["diagram_types"] = False

    # Test 3: Theme Variations
    try:
        test_theme_variations()
        test_results["themes"] = True
    except AssertionError as e:
        print(f"❌ Theme Variations failed: {e}")
        test_results["themes"] = False

    # Test 4: Error Handling
    try:
        test_error_handling()
        test_results["error_handling"] = True
    except AssertionError as e:
        print(f"❌ Error Handling failed: {e}")
        test_results["error_handling"] = False

    # Test 5: Performance
    try:
        test_performance()
        test_results["performance"] = True
    except AssertionError as e:
        print(f"❌ Performance failed: {e}")
        test_results["performance"] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 MERMAID TEST SUMMARY")
    print("=" * 50)

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)

    print(f"📈 Results: {passed_tests}/{total_tests} test categories passed")
    print()

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        formatted_name = test_name.replace("_", " ").title()
        print(f"   {status} {formatted_name}")

    print()

    if passed_tests == total_tests:
        print("🎉 ALL MERMAID TESTS PASSED! 🎉")
        print("Mermaid diagram conversion is working perfectly!")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")
        print("Please check the failed tests and fix any issues.")

    print("\n" + "=" * 50)

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_mermaid_tests()
    sys.exit(0 if success else 1)
