#!/usr/bin/env python3
"""
Test configuration for README to Word Converter

This file provides shared fixtures and configuration for pytest
if users prefer to use pytest instead of unittest.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

from readme2word.converter import ReadmeToWordConverter

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


@pytest.fixture
def converter():
    """Provide a fresh converter instance for each test"""
    converter = ReadmeToWordConverter()
    converter.set_debug_mode(False)  # Disable debug for tests
    return converter


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that gets cleaned up after tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_markdown():
    """Provide sample markdown content for testing"""
    return """# Test Document

This is a **test document** with various elements:

## Features
- Lists
- *Italic text*
- `Code snippets`

## Table Example

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Value 1  |
| Data 2   | Value 2  |

## Code Block

```python
def hello():
    print("Hello, World!")
```

## Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B[End]
```
"""


@pytest.fixture
def mermaid_diagrams():
    """Provide various Mermaid diagram examples"""
    return {
        "flowchart": """
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[Alternative]
    C --> E[End]
    D --> E
""",
        "sequence": """
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello!
    B-->>A: Hi there!
""",
        "class": """
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog
""",
    }


# Test markers for categorizing tests
pytest_markers = [
    "unit: Unit tests for individual components",
    "integration: Integration tests for complete workflows",
    "mermaid: Tests specifically for Mermaid diagram functionality",
    "ui: Tests for user interface components",
    "performance: Performance and benchmark tests",
    "slow: Tests that take longer to run",
]


def pytest_configure(config):
    """Configure pytest with custom markers"""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file names
        if "test_mermaid" in item.nodeid:
            item.add_marker(pytest.mark.mermaid)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        elif "test_ui" in item.nodeid:
            item.add_marker(pytest.mark.ui)
        elif "test_converter" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Mark performance tests
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
