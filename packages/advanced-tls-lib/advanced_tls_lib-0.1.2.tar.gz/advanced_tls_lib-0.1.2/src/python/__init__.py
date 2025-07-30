"""
Advanced TLS Library - The Most Advanced TLS Library for Python

A revolutionary Python TLS library with unparalleled capabilities for browser
fingerprint simulation, detection evasion, and performance optimization.
"""

__version__ = "0.1.0"
__author__ = "Advanced TLS Team"
__all__ = [
    "Client",
    "AsyncClient", 
    "BrowserProfile",
    "EvasionLevel",
    "TLSFingerprint",
    "Session",
    "AsyncSession",
    "create_client",
    "create_async_client",
]

from .client import Client, AsyncClient, create_client, create_async_client
from .profiles import BrowserProfile
from .evasion import EvasionLevel
from .session import Session, AsyncSession
from .fingerprint import TLSFingerprint

# Import native extensions
try:
    from advanced_tls_cpp import *
    _CPP_AVAILABLE = True
except ImportError:
    _CPP_AVAILABLE = False
    import warnings
    warnings.warn("C++ extensions not available, using pure Python fallback")

try:
    from advanced_tls_rust import *
    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False
    import warnings
    warnings.warn("Rust extensions not available, performance may be reduced")

def get_version():
    """Get the current version of the library."""
    return __version__

def check_extensions():
    """Check which native extensions are available."""
    return {
        "cpp": _CPP_AVAILABLE,
        "rust": _RUST_AVAILABLE
    }