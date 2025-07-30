#!/usr/bin/env python3
"""
Setup script for Advanced TLS Library.

This script builds the hybrid Python/C++/Rust library with all optimizations.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from setuptools import setup, Extension, find_packages

# Handle missing pybind11 gracefully during build dependency installation
try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext
    from pybind11 import get_cmake_dir
    import pybind11
    PYBIND11_AVAILABLE = True
except ImportError:
    PYBIND11_AVAILABLE = False
    # Fallback for when pybind11 is not yet installed
    from setuptools import Extension as Pybind11Extension
    from setuptools.command.build_ext import build_ext

# Handle missing setuptools-rust gracefully
try:
    from setuptools_rust import Binding, RustExtension
    SETUPTOOLS_RUST_AVAILABLE = True
except ImportError:
    SETUPTOOLS_RUST_AVAILABLE = False

# Check Python version
if sys.version_info < (3, 8):
    raise RuntimeError("Python 3.8+ is required")

# Get version
def get_version():
    """Get version from VERSION file."""
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.1.0"

VERSION = "0.1.1"

# Check for required dependencies
def check_openssl():
    """Check for OpenSSL/BoringSSL."""
    try:
        import ssl
        # Also check for development headers
        import subprocess
        try:
            subprocess.check_output(['gcc', '-E', '-x', 'c', '-'], 
                                   input='#include <openssl/ssl.h>\n', 
                                   text=True, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try with local installation
            home = os.path.expanduser("~")
            local_include = os.path.join(home, ".local", "include")
            if os.path.exists(os.path.join(local_include, "openssl", "ssl.h")):
                return True
            return False
    except ImportError:
        return False

def check_rust():
    """Check for Rust installation."""
    try:
        subprocess.check_output(['cargo', '--version'])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_cmake():
    """Check for CMake."""
    try:
        subprocess.check_output(['cmake', '--version'])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Check dependencies
if not check_openssl():
    print("Warning: OpenSSL not found. Some features may not work.")

if not check_rust():
    print("Warning: Rust not found. Performance optimizations will be disabled.")

if not check_cmake():
    print("Warning: CMake not found. Building without CMake optimizations.")

# Build settings
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes", "on")
PARALLEL = os.environ.get("PARALLEL", "1") != "0"

# Compiler flags
extra_compile_args = []
extra_link_args = []

if platform.system() == "Windows":
    extra_compile_args.extend(["/std:c++17", "/bigobj", "/EHsc"])
    if not DEBUG:
        extra_compile_args.extend(["/O2", "/DNDEBUG"])
else:
    extra_compile_args.extend(["-std=c++17", "-fvisibility=hidden"])
    if not DEBUG:
        extra_compile_args.extend(["-O3", "-DNDEBUG", "-flto"])
        extra_link_args.extend(["-flto"])
    else:
        extra_compile_args.extend(["-g", "-O0"])

# Define C++ extension
ext_modules = []

if check_cmake() and check_openssl() and PYBIND11_AVAILABLE:
    # Determine include directories
    include_dirs_list = [".", "src", pybind11.get_include()]
    
    # Check for local OpenSSL installation
    home = os.path.expanduser("~")
    local_include = os.path.join(home, ".local", "include")
    local_lib = os.path.join(home, ".local", "lib")
    local_lib64 = os.path.join(home, ".local", "lib64")
    
    if os.path.exists(os.path.join(local_include, "openssl")):
        include_dirs_list.append(local_include)
        extra_link_args.extend([f"-L{local_lib}", "-Wl,-rpath," + local_lib])
        # Also check lib64 for libraries
        if os.path.exists(local_lib64):
            extra_link_args.extend([f"-L{local_lib64}", "-Wl,-rpath," + local_lib64])
    
    # Use CMake build
    cmake_ext = Pybind11Extension(
        "advanced_tls_cpp",
        sorted([
            "bindings/cpp_bindings.cpp",
            "src/core/tls_engine.cpp",
            "src/core/fingerprint_gen.cpp", 
            "src/core/browser_profiles.cpp",
            "src/core/detection_evasion.cpp",
        ]),
        include_dirs=include_dirs_list,
        libraries=["ssl", "crypto"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=17,
    )
    ext_modules.append(cmake_ext)
else:
    if not PYBIND11_AVAILABLE:
        print("Info: pybind11 not available during initial setup. Extensions will be built when dependencies are installed.")
    elif not check_cmake():
        print("Warning: CMake not found. Installing Python-only version.")
    elif not check_openssl():
        print("Warning: OpenSSL development headers not found. Installing Python-only version.")
        print("Run './install_deps.sh' to install dependencies for full functionality.")

# Define Rust extension (temporarily disabled due to compilation issues)
rust_extensions = []
if check_rust() and SETUPTOOLS_RUST_AVAILABLE:
    try:
        rust_ext = RustExtension(
            "advanced_tls_rust",
            path="src/rust/Cargo.toml",
            binding=Binding.PyO3,
            debug=DEBUG,
            features=["extension-module"] if not DEBUG else ["extension-module", "dev"],
        )
        rust_extensions.append(rust_ext)
    except Exception as e:
        print(f"Warning: Rust extension disabled due to: {e}")

# Custom build command
class CustomBuildExt(build_ext):
    """Custom build extension to handle special requirements."""
    
    def build_extensions(self):
        # Build Rust extensions first if available
        if rust_extensions and SETUPTOOLS_RUST_AVAILABLE:
            print("Building Rust extensions...")
            try:
                subprocess.check_call([
                    "cargo", "build", 
                    "--release" if not DEBUG else "",
                    "--manifest-path", "src/rust/Cargo.toml"
                ], cwd=Path(__file__).parent)
            except subprocess.CalledProcessError as e:
                print(f"Rust build failed: {e}")
            except FileNotFoundError:
                print("Warning: cargo not found, skipping Rust extensions")
                
        # Build C++ extensions
        super().build_extensions()
        
    def build_extension(self, ext):
        """Build individual extension with optimizations."""
        # Enable parallel compilation
        if PARALLEL and hasattr(self.compiler, 'compile'):
            original_compile = self.compiler.compile
            
            def parallel_compile(*args, **kwargs):
                kwargs.setdefault('extra_postargs', [])
                if platform.system() == "Windows":
                    kwargs['extra_postargs'].append('/MP')
                # Убираем -j для Linux, так как он вызывает ошибку
                return original_compile(*args, **kwargs)
                
            self.compiler.compile = parallel_compile
            
        super().build_extension(ext)

# Read long description
def read_file(filename):
    """Read file content."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

long_description = read_file("README.md")

# Package requirements
install_requires = [
    "pybind11>=2.10.0",
    "typing-extensions>=4.0.0",
]

extras_require = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-benchmark>=4.0.0",
        "black>=22.0.0",
        "isort>=5.0.0",
        "mypy>=1.0.0",
        "flake8>=5.0.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
        "sphinx-autodoc-typehints>=1.0.0",
    ],
    "performance": [
        "cython>=0.29.0",
    ],
}

# Setup configuration
setup(
    name="advanced-tls",
    version=VERSION,
    description="The Most Advanced TLS Library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Advanced TLS Team",
    author_email="team@advancedtls.dev",
    url="https://github.com/advanced-tls/advanced-tls-lib",
    project_urls={
        "Bug Reports": "https://github.com/advanced-tls/advanced-tls-lib/issues",
        "Source": "https://github.com/advanced-tls/advanced-tls-lib",
        "Documentation": "https://docs.advancedtls.dev",
    },
    
    # Package configuration
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    python_requires=">=3.8",
    
    # Extensions
    ext_modules=ext_modules,
    rust_extensions=rust_extensions,
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False,
    
    # Dependencies
    install_requires=install_requires,
    extras_require=extras_require,
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Programming Language :: Rust",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    keywords="tls ssl http browser fingerprint evasion bot detection",
    
    # Entry points
    entry_points={
        "console_scripts": [
            "advanced-tls=advanced_tls.cli:main",
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        "advanced_tls": ["py.typed"],
    },
)

# Post-install message
print(f"""
🚀 Advanced TLS Library v{VERSION} installation complete!

Features installed:
✅ Core Python API
{'✅' if ext_modules else '❌'} C++ Core Engine (BoringSSL integration)
{'✅' if rust_extensions else '❌'} Rust Performance Layer
{'✅' if check_openssl() else '❌'} OpenSSL/TLS Support

Quick start:
    import advanced_tls as atls
    
    client = atls.Client()
    response = client.get('https://example.com', browser='chrome')
    print(response.text)

Documentation: https://docs.advancedtls.dev
Examples: https://github.com/advanced-tls/advanced-tls-lib/tree/main/examples
""")

if not check_rust():
    print("⚠️  Install Rust for maximum performance: https://rustup.rs/")

if not ext_modules:
    print("⚠️  C++ extensions not built. Install cmake and OpenSSL for full features.")