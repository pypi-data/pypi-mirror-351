#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pytest",
#     "pytest-cov",
# ]
# ///

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add the parent directory to sys.path so we can import mhtml_converter
sys.path.insert(0, str(Path(__file__).parent.parent))

from mhtml_converter import convert_mhtml
from mhtml_converter.converter import _detect_binary


class TestMHTMLConverter:
    """Test the MHTML converter functionality."""
    
    def test_binary_detection(self):
        """Test that the correct binary is detected for the current platform."""
        binary_path = _detect_binary()
        assert os.path.exists(binary_path), f"Binary not found at {binary_path}"
        assert os.access(binary_path, os.X_OK), f"Binary not executable at {binary_path}"
    
    def test_create_sample_mhtml(self):
        """Create a simple MHTML file for testing."""
        mhtml_content = '''MIME-Version: 1.0
Content-Type: multipart/related; boundary="----MultipartBoundary--test123"

------MultipartBoundary--test123
Content-Type: text/html; charset=utf-8
Content-Location: http://example.com/

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a test MHTML file.</p>
</body>
</html>

------MultipartBoundary--test123--
'''
        return mhtml_content.strip()
    
    def test_convert_simple_mhtml(self):
        """Test converting a simple MHTML file."""
        mhtml_content = self.test_create_sample_mhtml()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        try:
            # Test string output
            result = convert_mhtml(temp_mhtml)
            assert isinstance(result, str)
            assert "Hello World" in result
            assert "<!DOCTYPE html>" in result or "<html" in result
            
        finally:
            os.unlink(temp_mhtml)
    
    def test_convert_to_file(self):
        """Test converting MHTML and saving to file."""
        mhtml_content = self.test_create_sample_mhtml()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            temp_html = f.name
        
        try:
            # Test file output
            result = convert_mhtml(temp_mhtml, output_file=temp_html)
            assert isinstance(result, str)  # Returns file path when saving to file
            
            # Check the file was created and has content
            assert os.path.exists(temp_html)
            with open(temp_html, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Hello World" in content
                
        finally:
            os.unlink(temp_mhtml)
            if os.path.exists(temp_html):
                os.unlink(temp_html)
    
    def test_verbose_mode(self):
        """Test verbose mode shows additional output."""
        mhtml_content = self.test_create_sample_mhtml()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        try:
            # Test verbose mode (should not crash)
            result = convert_mhtml(temp_mhtml, verbose=True)
            assert isinstance(result, str)
            assert "Hello World" in result
            
        finally:
            os.unlink(temp_mhtml)
    
    def test_nonexistent_file(self):
        """Test error handling for nonexistent files."""
        with pytest.raises(FileNotFoundError):
            convert_mhtml("/path/that/does/not/exist.mht")
    
    def test_invalid_mhtml(self):
        """Test handling of invalid MHTML content."""
        invalid_content = "This is not valid MHTML content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(invalid_content)
            temp_mhtml = f.name
        
        try:
            # Should handle gracefully or raise RuntimeError
            try:
                result = convert_mhtml(temp_mhtml)
                assert isinstance(result, str)  # Should at least return a string
            except RuntimeError:
                # This is also acceptable - Go binary might reject invalid MHTML
                pass
            
        finally:
            os.unlink(temp_mhtml)


class TestEncodingDetection:
    """Test encoding detection functionality."""
    
    def test_chinese_mhtml_simulation(self):
        """Test handling of Chinese content (simulated)."""
        # Create MHTML with Chinese charset declaration
        mhtml_content = '''MIME-Version: 1.0
Content-Type: multipart/related; boundary="----MultipartBoundary--test123"

------MultipartBoundary--test123
Content-Type: text/html; charset=gbk
Content-Location: http://example.com/

<!DOCTYPE html>
<html>
<head>
    <meta charset="gbk">
    <title>Chinese Test</title>
</head>
<body>
    <h1>测试页面</h1>
    <p>这是一个中文测试页面。</p>
</body>
</html>

------MultipartBoundary--test123--
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False, encoding='utf-8') as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        try:
            result = convert_mhtml(temp_mhtml, verbose=True)
            assert isinstance(result, str)
            # The Go binary should handle the conversion
            
        finally:
            os.unlink(temp_mhtml)


def test_cli_import():
    """Test that CLI module can be imported."""
    from mhtml_converter.cli import main
    assert callable(main)


def test_package_import():
    """Test package imports work correctly."""
    import mhtml_converter
    assert hasattr(mhtml_converter, 'convert_mhtml')
    assert hasattr(mhtml_converter, '__version__')


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 