#!/usr/bin/env python3
"""
Integration test suite for README to Word Converter

Tests cover:
- End-to-end conversion workflows
- Mermaid diagram integration
- File I/O operations
- Error recovery scenarios
- Performance benchmarks
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

from readme2word.converter import ReadmeToWordConverter

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))


class TestIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.converter = ReadmeToWordConverter()
        self.converter.set_debug_mode(False)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_readme_conversion(self):
        """Test complete README conversion with all features"""
        complex_readme = """# My Awesome Project

[![Build Status](https://travis-ci.org/user/project.svg?branch=master)](https://travis-ci.org/user/project)

## Overview

This project demonstrates **advanced features** including:
- Mermaid diagrams
- Tables with complex data
- Code blocks in multiple languages
- *Formatted text* and `inline code`

## Architecture

```mermaid
graph TB
    A[User Input] --> B[Markdown Parser]
    B --> C[Mermaid Processor]
    C --> D[HTML Generator]
    D --> E[Word Document]

    subgraph "Processing Pipeline"
        B
        C
        D
    end
```

## API Reference

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `convert()` | content, filename | path | Main conversion method |
| `set_debug_mode()` | enabled | None | Toggle debug output |
| `get_stats()` | None | dict | Get conversion statistics |

## Code Examples

### Python Implementation
```python
from readme2word.converter import ReadmeToWordConverter

converter = ReadmeToWordConverter()
result = converter.convert(content, "output")
print(f"Document saved to: {result}")
```

### JavaScript Usage
```javascript
const converter = new ReadmeConverter();
converter.convert(markdown)
    .then(result => console.log('Success:', result))
    .catch(error => console.error('Error:', error));
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant C as Converter
    participant M as Mermaid API

    U->>A: Upload README
    A->>C: Process content
    C->>M: Convert diagrams
    M-->>C: Return images
    C-->>A: Generate document
    A-->>U: Download link
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`

> **Note**: This is a blockquote with important information.

## Contributing

Please read our [contributing guidelines](CONTRIBUTING.md) before submitting PRs.

---

*Built with ❤️ by the development team*
"""

        # Test conversion
        start_time = time.time()
        output_path = self.converter.convert(
            complex_readme,
            "integration_test",
            include_toc=True,
            diagram_style="default",
        )
        conversion_time = time.time() - start_time

        # Verify output
        self.assertTrue(os.path.exists(output_path))
        # Should complete within 30 seconds
        self.assertLess(conversion_time, 30)

        # Check statistics
        stats = self.converter.get_conversion_stats()
        self.assertGreater(stats["headings"], 5)
        self.assertEqual(stats["tables"], 1)
        self.assertGreater(stats["code_blocks"], 1)
        self.assertEqual(stats["mermaid_diagrams"], 2)
        self.assertEqual(stats["images"], 2)  # Should have 2 Mermaid images

        # Verify file size (should be reasonable)
        file_size = os.path.getsize(output_path)
        self.assertGreater(file_size, 10000)  # At least 10KB
        self.assertLess(file_size, 5000000)  # Less than 5MB

    def test_mermaid_diagram_types(self):
        """Test various Mermaid diagram types"""
        diagram_tests = [
            (
                "flowchart",
                """
```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
```
""",
            ),
            (
                "sequence",
                """
```mermaid
sequenceDiagram
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>John: How about you John?
    Bob--x Alice: I am good thanks!
```
""",
            ),
            (
                "class",
                """
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog
```
""",
            ),
            (
                "state",
                """
```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```
""",
            ),
        ]

        for diagram_type, diagram_content in diagram_tests:
            with self.subTest(diagram_type=diagram_type):
                markdown_content = f"# {diagram_type.title()} Test\n\n{diagram_content}"

                output_path = self.converter.convert(
                    markdown_content, f"test_{diagram_type}", include_toc=False
                )

                self.assertTrue(os.path.exists(output_path))
                stats = self.converter.get_conversion_stats()
                self.assertEqual(stats["mermaid_diagrams"], 1)

    def test_large_document_performance(self):
        """Test performance with large documents"""
        # Generate large document
        large_content = "# Large Document Test\n\n"

        # Add many sections
        for i in range(50):
            large_content += f"""
## Section {i+1}

This is section {i+1} with some content. It includes:
- Multiple bullet points
- **Bold text** and *italic text*
- Some `inline code`

### Subsection {i+1}.1

More content here with a table:

| Column A | Column B | Column C |
|----------|----------|----------|
| Data {i} | Value {i} | Result {i} |

"""

        # Add a few Mermaid diagrams
        large_content += """
## Architecture Overview

```mermaid
graph LR
    A[Input] --> B[Processing]
    B --> C[Output]
```

## Process Flow

```mermaid
sequenceDiagram
    User->>System: Request
    System-->>User: Response
```
"""

        # Test conversion performance
        start_time = time.time()
        output_path = self.converter.convert(
            large_content, "large_document_test", include_toc=True
        )
        conversion_time = time.time() - start_time

        # Verify results
        self.assertTrue(os.path.exists(output_path))
        self.assertLess(conversion_time, 60)  # Should complete within 1 minute

        stats = self.converter.get_conversion_stats()
        self.assertGreater(stats["headings"], 100)  # Many headings
        self.assertGreater(stats["tables"], 40)  # Many tables
        self.assertEqual(stats["mermaid_diagrams"], 2)  # 2 diagrams

    def test_error_recovery(self):
        """Test error recovery scenarios"""
        # Test with invalid Mermaid syntax
        invalid_mermaid = """# Error Recovery Test

```mermaid
invalid syntax here
this should not work
```

But the conversion should continue and create a document.
"""

        output_path = self.converter.convert(
            invalid_mermaid, "error_recovery_test", include_toc=False
        )

        # Should still create document despite Mermaid error
        self.assertTrue(os.path.exists(output_path))

        stats = self.converter.get_conversion_stats()
        self.assertEqual(stats["mermaid_diagrams"], 0)  # Failed conversion

    def test_special_characters_handling(self):
        """Test handling of special characters and Unicode"""
        special_content = """# Special Characters Test 🚀

## Unicode Support

This document contains various special characters:
- Emojis: 🎉 🔥 ⭐ 🚀 💡
- Accented characters: café, naïve, résumé
- Mathematical symbols: α, β, γ, ∑, ∫, ∞
- Currency symbols: $, €, £, ¥, ₹

## Code with Special Characters

```python
def unicode_test():
    message = "Hello, 世界! 🌍"
    return f"Message: {message}"
```

## Table with Unicode

| Language | Greeting | Flag |
|----------|----------|------|
| English | Hello | 🇺🇸 |
| Spanish | Hola | 🇪🇸 |
| French | Bonjour | 🇫🇷 |
| Japanese | こんにちは | 🇯🇵 |
| Chinese | 你好 | 🇨🇳 |
"""

        output_path = self.converter.convert(
            special_content, "special_chars_test", include_toc=False
        )

        self.assertTrue(os.path.exists(output_path))

        stats = self.converter.get_conversion_stats()
        self.assertEqual(stats["headings"], 4)
        self.assertEqual(stats["tables"], 1)
        self.assertEqual(stats["code_blocks"], 1)


class TestFileOperations(unittest.TestCase):
    """Test file I/O operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.converter = ReadmeToWordConverter()
        self.converter.set_debug_mode(False)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_output_directory_creation(self):
        """Test that output directories are created properly"""
        # Test with nested directory structure
        nested_path = os.path.join(self.temp_dir, "nested", "deep", "path")

        # Change working directory temporarily
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)

            output_path = self.converter.convert(
                "# Test", "nested/deep/path/test_file", include_toc=False
            )

            # Check that file was created in correct location
            self.assertTrue(os.path.exists(output_path))

        finally:
            os.chdir(original_cwd)

    def test_filename_sanitization(self):
        """Test filename sanitization for various inputs"""
        test_cases = [
            ("normal_filename", "normal_filename.docx"),
            ("file with spaces", "file with spaces.docx"),
            (
                "file/with/slashes",
                "file/with/slashes.docx",
            ),  # Should handle path separators
        ]

        for input_name, expected_pattern in test_cases:
            with self.subTest(filename=input_name):
                output_path = self.converter.convert(
                    "# Test", input_name, include_toc=False
                )

                self.assertTrue(os.path.exists(output_path))
                self.assertTrue(output_path.endswith(".docx"))


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Integration Tests")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
    else:
        print(
            f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )

    return result.wasSuccessful()


if __name__ == "__main__":
    run_integration_tests()
