#!/usr/bin/env python3
"""
Test suite for the ReadmeToWordConverter class

Tests cover:
- Basic markdown to Word conversion
- HTML processing
- Document styling
- Error handling
- Statistics tracking
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from docx import Document

from readme2word.converter import ReadmeToWordConverter

# Add parent directory to path to import converter
sys.path.append(str(Path(__file__).parent.parent))


class TestReadmeToWordConverter(unittest.TestCase):
    """Test cases for ReadmeToWordConverter class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.converter = ReadmeToWordConverter()
        self.converter.set_debug_mode(False)  # Disable debug output for tests

        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method"""
        # Clean up temporary files
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_basic_markdown_conversion(self):
        """Test basic markdown to Word conversion"""
        markdown_content = """# Test Document

This is a **bold** text and this is *italic* text.

## Section 2

Here's a list:
- Item 1
- Item 2
- Item 3

And a numbered list:
1. First item
2. Second item
3. Third item
"""

        output_path = self.converter.convert(
            markdown_content, "test_basic", include_toc=False
        )

        # Check that file was created
        self.assertTrue(os.path.exists(output_path))

        # Check statistics
        stats = self.converter.get_conversion_stats()
        self.assertEqual(stats["headings"], 2)
        self.assertEqual(stats["mermaid_diagrams"], 0)

    def test_table_conversion(self):
        """Test table conversion from markdown to Word"""
        markdown_content = """# Table Test

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data 1   | Value 1  |
| Row 2    | Data 2   | Value 2  |
| Row 3    | Data 3   | Value 3  |
"""

        output_path = self.converter.convert(
            markdown_content, "test_table", include_toc=False
        )

        # Check that file was created
        self.assertTrue(os.path.exists(output_path))

        # Check statistics
        stats = self.converter.get_conversion_stats()
        self.assertEqual(stats["tables"], 1)

    def test_code_block_conversion(self):
        """Test code block conversion"""
        markdown_content = """# Code Test

Here's some Python code:

```python
def hello_world():
    print("Hello, World!")
    return True
```

And some inline `code` here.
"""

        output_path = self.converter.convert(
            markdown_content, "test_code", include_toc=False
        )

        # Check that file was created
        self.assertTrue(os.path.exists(output_path))

        # Check statistics
        stats = self.converter.get_conversion_stats()
        self.assertEqual(stats["code_blocks"], 1)

    def test_title_extraction(self):
        """Test automatic title extraction"""
        markdown_content = """# My Amazing Project

This is the content of my project.
"""

        title = self.converter._extract_title(markdown_content)
        self.assertEqual(title, "My Amazing Project")

    def test_empty_content(self):
        """Test handling of empty content"""
        output_path = self.converter.convert("", "test_empty", include_toc=False)

        # Check that file was created even with empty content
        self.assertTrue(os.path.exists(output_path))

    def test_statistics_tracking(self):
        """Test that statistics are properly tracked"""
        markdown_content = """# Main Title

## Subtitle 1

### Subtitle 2

| Table | Header |
|-------|--------|
| Data  | Value  |

```python
print("code")
```

- List item 1
- List item 2
"""

        self.converter.convert(markdown_content, "test_stats", include_toc=False)
        stats = self.converter.get_conversion_stats()

        # Verify statistics
        self.assertEqual(stats["headings"], 3)
        self.assertEqual(stats["tables"], 1)
        self.assertEqual(stats["code_blocks"], 1)
        self.assertEqual(stats["mermaid_diagrams"], 0)

    def test_debug_mode_toggle(self):
        """Test debug mode functionality"""
        # Test enabling debug mode
        self.converter.set_debug_mode(True)
        self.assertTrue(self.converter.debug_mode)

        # Test disabling debug mode
        self.converter.set_debug_mode(False)
        self.assertFalse(self.converter.debug_mode)

    def test_document_styles_setup(self):
        """Test that document styles are properly set up"""
        from docx import Document

        doc = Document()

        # This should not raise an exception
        self.converter._setup_document_styles(doc)

        # Check that styles were added (basic check)
        style_names = [style.name for style in doc.styles]
        self.assertIn("Normal", style_names)


def run_converter_tests():
    """Run all converter tests"""
    print("🧪 Running Converter Tests")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReadmeToWordConverter)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All converter tests passed!")
    else:
        print(
            f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )

    return result.wasSuccessful()


if __name__ == "__main__":
    run_converter_tests()
