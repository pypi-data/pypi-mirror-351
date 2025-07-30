# MHTML to HTML (Python)

A Python wrapper for the excellent [gonejack/mhtml-to-html](https://github.com/gonejack/mhtml-to-html) Go tool, adding automatic encoding detection for Chinese, Japanese, and Korean content.

NOTE: This is 100% vibe coded, including all the effusive LLM slop below. It works and has tests, that's all I can say.

## Features

- 🌍 **Smart Encoding Detection**: Automatically detects and converts Chinese (GBK, GB18030), Japanese (Shift_JIS), Korean (EUC-KR) and other encodings
- ⚡ **Fast Performance**: Uses optimized Go binary under the hood
- 🖥️ **Cross-Platform**: Works on Linux, macOS, and Windows (x64 & ARM64)
- 🐍 **Simple Python API**: Clean interface with optional CLI
- 📦 **Zero Dependencies**: Self-contained with embedded binaries
- 🙏 **Built on Excellence**: Wraps the proven [mhtml-to-html](https://github.com/gonejack/mhtml-to-html) Go tool

## Installation

```bash
pip install mhtml-to-html-py
```

## Quick Start

### Python API

```python
from mhtml_converter import convert_mhtml

# Convert MHTML to HTML string
html_content = convert_mhtml("document.mht")

# Save to file with verbose encoding detection
convert_mhtml("chinese_doc.mht", output_file="output.html", verbose=True)

# Convert with explicit encoding (if detection fails)
html_content = convert_mhtml("document.mht", encoding="gbk")
```

### Command Line

```bash
# Convert single file
mhtml-to-html-py input.mht -o output.html

# Verbose mode to see encoding detection
mhtml-to-html-py input.mht -o output.html --verbose

# Convert multiple files
mhtml-to-html-py *.mht --output-dir converted/
```

## Why This Package?

Many MHTML files, especially those saved from Chinese, Japanese, or Korean websites, use non-UTF-8 encodings that cause garbled text when converted naively. This package:

1. **Detects encoding** from HTML meta tags and content analysis
2. **Converts properly** to UTF-8 for universal compatibility  
3. **Preserves formatting** and embedded resources
4. **Works reliably** across different platforms and languages

## Use Cases

- Converting saved web pages from Asian websites
- Processing email archives in MHTML format
- Batch conversion of documentation
- Web scraping pipeline preprocessing
- Digital preservation workflows

## Technical Details

This package wraps the high-performance [mhtml-to-html](https://github.com/gonejack/mhtml-to-html) Go binary that handles the actual conversion. The Python layer provides a clean API, handles platform detection automatically, and adds enhanced encoding detection capabilities.

### Supported Platforms

| OS | Architecture | Status |
|---|---|---|
| Linux | x86_64 | ✅ |
| Linux | ARM64 | ✅ |
| macOS | Intel | ✅ |
| macOS | Apple Silicon | ✅ |
| Windows | x86_64 | ✅ |

## Credits

This project is a Python wrapper around the excellent [gonejack/mhtml-to-html](https://github.com/gonejack/mhtml-to-html) Go tool. All the heavy lifting for MHTML parsing and conversion is done by that project. We've added:

- Python packaging and distribution
- Cross-platform binary embedding
- Enhanced encoding detection
- Simplified Python API

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests welcome! This project wraps the excellent [gonejack/mhtml-to-html](https://github.com/gonejack/mhtml-to-html) Go tool with Python convenience layers. 