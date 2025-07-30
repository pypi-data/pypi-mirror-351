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
import subprocess
from pathlib import Path

# Add the parent directory to sys.path so we can import mhtml_converter
sys.path.insert(0, str(Path(__file__).parent.parent))

from mhtml_converter.cli import main


class TestCLI:
    """Test the command-line interface."""
    
    def create_sample_mhtml(self):
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
    <title>CLI Test Page</title>
</head>
<body>
    <h1>CLI Test</h1>
    <p>This is a test MHTML file for CLI testing.</p>
</body>
</html>

------MultipartBoundary--test123--
'''
        return mhtml_content.strip()
    
    def test_cli_help(self):
        """Test that CLI shows help."""
        # Test help flag using subprocess to call the module directly
        result = subprocess.run([
            sys.executable, "-m", "mhtml_converter.cli", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should exit with code 0 for help
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "convert mhtml" in result.stdout.lower()
    
    def test_cli_convert_file(self):
        """Test CLI file conversion."""
        mhtml_content = self.create_sample_mhtml()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            temp_html = f.name
        
        try:
            # Test CLI conversion using subprocess
            result = subprocess.run([
                sys.executable, "-m", "mhtml_converter.cli", 
                temp_mhtml, "-o", temp_html
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # Should succeed
            assert result.returncode == 0
            
            # Check output file exists and has content
            assert os.path.exists(temp_html)
            with open(temp_html, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "CLI Test" in content
                
        finally:
            os.unlink(temp_mhtml)
            if os.path.exists(temp_html):
                os.unlink(temp_html)
    
    def test_cli_verbose_mode(self):
        """Test CLI verbose mode."""
        mhtml_content = self.create_sample_mhtml()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mht', delete=False) as f:
            f.write(mhtml_content)
            temp_mhtml = f.name
        
        try:
            # Test verbose mode
            result = subprocess.run([
                sys.executable, "-m", "mhtml_converter.cli",
                temp_mhtml, "--verbose"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # Should succeed and show output
            assert result.returncode == 0
            # Should have HTML output in stdout
            assert "CLI Test" in result.stdout
                
        finally:
            os.unlink(temp_mhtml)
    
    def test_cli_nonexistent_file(self):
        """Test CLI with nonexistent file."""
        result = subprocess.run([
            sys.executable, "-m", "mhtml_converter.cli",
            "/path/that/does/not/exist.mht"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should fail with non-zero exit code
        assert result.returncode != 0
        assert "Error" in result.stderr or "error" in result.stderr.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"]) 