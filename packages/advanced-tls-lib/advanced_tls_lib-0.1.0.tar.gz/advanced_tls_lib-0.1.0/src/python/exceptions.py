"""
Exception classes for Advanced TLS Library.
"""


class TLSError(Exception):
    """Base exception for TLS-related errors."""
    pass


class ConnectionError(TLSError):
    """Connection-related errors."""
    pass


class TimeoutError(TLSError):
    """Timeout-related errors."""
    pass


class SSLError(TLSError):
    """SSL/TLS-related errors."""
    pass


class DetectionError(TLSError):
    """Bot detection-related errors."""
    pass


class FingerprintError(TLSError):
    """Fingerprint-related errors."""
    pass


class ProxyError(TLSError):
    """Proxy-related errors."""
    pass


class HTTPError(TLSError):
    """HTTP-related errors."""
    
    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.response = response


class TooManyRedirects(TLSError):
    """Too many redirects error."""
    pass


class InvalidURL(TLSError):
    """Invalid URL error."""
    pass


class InvalidHeader(TLSError):
    """Invalid header error."""
    pass


class ChunkedEncodingError(TLSError):
    """Chunked encoding error."""
    pass


class ContentDecodingError(TLSError):
    """Content decoding error."""
    pass


class StreamConsumedError(TLSError):
    """Stream already consumed error."""
    pass


class RetryError(TLSError):
    """Retry limit exceeded error."""
    pass


class ConfigurationError(TLSError):
    """Configuration error."""
    pass


class ChallengeError(TLSError):
    """Challenge solving error."""
    pass


class FingerprintValidationError(FingerprintError):
    """Fingerprint validation error."""
    pass


class BrowserProfileError(TLSError):
    """Browser profile error."""
    pass


class EvasionError(TLSError):
    """Evasion strategy error."""
    pass