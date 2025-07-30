"""
Core converter functionality for MHTML to HTML conversion.
"""

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Union, Optional


def _detect_binary() -> str:
    """Detect the correct binary for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    if machine in ("x86_64", "amd64", "x64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    elif machine in ("i386", "i686", "x86"):
        arch = "386"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")
    
    # Normalize system names
    if system == "darwin":
        system = "darwin"
    elif system == "linux":
        system = "linux"
    elif system == "windows":
        system = "windows"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")
    
    # Construct binary name
    binary_name = f"mhtml-to-html-{system}-{arch}"
    if system == "windows":
        binary_name += ".exe"
    
    # Find binary in package
    package_dir = Path(__file__).parent
    binary_path = package_dir / "bin" / binary_name
    
    if not binary_path.exists():
        raise FileNotFoundError(
            f"No binary found for {system}-{arch}. "
            f"Expected: {binary_path}"
        )
    
    # Make sure it's executable on Unix systems
    if system != "windows":
        os.chmod(binary_path, 0o755)
    
    return str(binary_path)


def convert_mhtml(mhtml_path: Union[str, Path], 
                  verbose: bool = False,
                  output_file: Optional[Union[str, Path]] = None) -> str:
    """
    Convert MHTML file to HTML.
    
    Args:
        mhtml_path: Path to the MHTML file (.mht or .mhtml)
        verbose: Enable verbose logging (shows encoding detection info)
        output_file: Optional output file path. If None, returns HTML as string.
        
    Returns:
        HTML content as string (if output_file is None)
        
    Raises:
        FileNotFoundError: If MHTML file or binary not found
        subprocess.CalledProcessError: If conversion fails
        RuntimeError: If platform is unsupported
    """
    binary_path = _detect_binary()
    mhtml_path = Path(mhtml_path)
    
    if not mhtml_path.exists():
        raise FileNotFoundError(f"MHTML file not found: {mhtml_path}")
    
    # Build command
    cmd = [binary_path]
    if verbose:
        cmd.append("--verbose")
    
    if output_file:
        output_file = Path(output_file)
        cmd.extend(["-o", str(output_file)])
    
    cmd.append(str(mhtml_path))
    
    # Execute command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        if output_file:
            # When saving to file, return the file path
            return str(output_file)
        else:
            # When outputting to stdout, return the HTML content
            return result.stdout
            
    except subprocess.CalledProcessError as e:
        error_msg = f"MHTML conversion failed: {e.stderr}"
        if verbose and e.stdout:
            error_msg += f"\nOutput: {e.stdout}"
        raise RuntimeError(error_msg) from e


def convert_mhtml_file(mhtml_path: Union[str, Path], 
                      output_path: Union[str, Path],
                      verbose: bool = False) -> str:
    """
    Convert MHTML file to HTML file.
    
    Args:
        mhtml_path: Path to input MHTML file
        output_path: Path to output HTML file
        verbose: Enable verbose logging
        
    Returns:
        Path to the created HTML file
    """
    return convert_mhtml(mhtml_path, verbose=verbose, output_file=output_path)


# Convenience functions for common use cases
def mhtml_to_html_string(mhtml_path: Union[str, Path], 
                        verbose: bool = False) -> str:
    """Convert MHTML to HTML string (memory-based)."""
    return convert_mhtml(mhtml_path, verbose=verbose)


def mhtml_to_html_file(mhtml_path: Union[str, Path], 
                      output_path: Union[str, Path],
                      verbose: bool = False) -> str:
    """Convert MHTML to HTML file (file-based)."""
    return convert_mhtml_file(mhtml_path, output_path, verbose=verbose) 