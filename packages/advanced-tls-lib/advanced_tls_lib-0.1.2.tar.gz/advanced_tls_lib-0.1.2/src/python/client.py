import asyncio
from typing import Dict, Optional, Union, Any, List, Tuple
from contextlib import contextmanager, asynccontextmanager
import time
import json
from urllib.parse import urlparse, urljoin
import warnings

from .profiles import BrowserProfile, get_browser_profile
from .evasion import EvasionLevel, EvasionStrategy
from .fingerprint import TLSFingerprint, FingerprintRotationStrategy
from .utils import parse_headers, build_request_headers, parse_response
from .exceptions import TLSError, ConnectionError, DetectionError

try:
    from advanced_tls_cpp import TLSEngine, AsyncTLSEngine, BrowserProfileManager
    _USE_NATIVE = True
except ImportError:
    _USE_NATIVE = False
    from .fallback import TLSEngine, AsyncTLSEngine, BrowserProfileManager

try:
    from advanced_tls_rust import RustConnectionPool, RustPerformanceMonitor
    _USE_RUST_POOL = True
except ImportError:
    _USE_RUST_POOL = False
    from .fallback import ConnectionPool as RustConnectionPool
    from .fallback import PerformanceMonitor as RustPerformanceMonitor


class Client:
    """
    Advanced TLS Client with browser fingerprint simulation.
    
    Example:
        >>> client = Client()
        >>> response = client.get('https://example.com')
        >>> print(response.text)
        
        >>> # With specific browser
        >>> client = Client(browser='chrome')
        >>> response = client.get('https://example.com')
        
        >>> # With advanced evasion
        >>> client = Client(
        ...     browser_profile=BrowserProfile.CHROME_LATEST,
        ...     evasion_level=EvasionLevel.MAXIMUM,
        ...     fingerprint_rotation=FingerprintRotationStrategy.INTELLIGENT
        ... )
    """
    
    def __init__(
        self,
        browser: Optional[str] = None,
        browser_profile: Optional[BrowserProfile] = None,
        evasion_level: EvasionLevel = EvasionLevel.ADVANCED,
        fingerprint_rotation: Optional[FingerprintRotationStrategy] = None,
        proxy: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        max_redirects: int = 10,
        enable_http2: bool = True,
        enable_http3: bool = False,
        custom_fingerprint: Optional[TLSFingerprint] = None,
        performance_monitor: bool = False,
    ):
        """
        Initialize the Advanced TLS Client.
        
        Args:
            browser: Simple browser name ('chrome', 'firefox', 'safari')
            browser_profile: Specific browser profile enum
            evasion_level: Level of detection evasion
            fingerprint_rotation: Strategy for rotating fingerprints
            proxy: Proxy URL
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_redirects: Maximum number of redirects to follow
            enable_http2: Enable HTTP/2 support
            enable_http3: Enable HTTP/3 support
            custom_fingerprint: Custom TLS fingerprint
            performance_monitor: Enable performance monitoring
        """
        # Determine browser profile
        if browser_profile:
            self.browser_profile = browser_profile
        elif browser:
            self.browser_profile = get_browser_profile(browser)
        else:
            self.browser_profile = BrowserProfile.CHROME_LATEST
            
        self.evasion_level = evasion_level
        self.fingerprint_rotation = fingerprint_rotation or FingerprintRotationStrategy.NONE
        
        # Initialize engine
        self.engine = TLSEngine()
        
        # Initialize with fingerprint
        if custom_fingerprint:
            self.engine.initialize_custom(custom_fingerprint)
        else:
            self.engine.initialize(self.browser_profile, self.evasion_level)
            
        # Set connection options
        from advanced_tls_cpp import ConnectionOptions
        options = ConnectionOptions()
        options.proxy_url = proxy or ""
        options.timeout_ms = int(timeout * 1000)
        options.verify_ssl = verify_ssl
        options.max_redirects = max_redirects
        options.enable_http2 = enable_http2
        options.enable_http3 = enable_http3
        
        self.engine.set_connection_options(options)
        
        # Browser profile manager
        self.profile_manager = BrowserProfileManager()
        self.browser_chars = self.profile_manager.get_profile(self.browser_profile)
        
        # Performance monitoring
        self.perf_monitor = RustPerformanceMonitor() if performance_monitor else None
        
        # Session state
        self.cookies = {}
        self.headers = {}
        self._closed = False
        
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> 'Response':
        """Send GET request."""
        return self.request('GET', url, headers=headers, params=params, 
                          allow_redirects=allow_redirects, **kwargs)
    
    def post(
        self,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> 'Response':
        """Send POST request."""
        return self.request('POST', url, data=data, json=json, 
                          headers=headers, **kwargs)
    
    def put(
        self,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> 'Response':
        """Send PUT request."""
        return self.request('PUT', url, data=data, json=json, 
                          headers=headers, **kwargs)
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> 'Response':
        """Send DELETE request."""
        return self.request('DELETE', url, headers=headers, **kwargs)
    
    def request(
        self,
        method: str,
        url: str,
        data: Optional[Union[str, bytes, Dict]] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> 'Response':
        """
        Send HTTP request with advanced TLS fingerprinting.
        
        Args:
            method: HTTP method
            url: Target URL
            data: Request body data
            json: JSON data (will be serialized)
            headers: Additional headers
            params: URL parameters
            allow_redirects: Follow redirects
            
        Returns:
            Response object
        """
        if self._closed:
            raise RuntimeError("Client is closed")
            
        start_time = time.time()
        
        # Parse URL
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        if params:
            # Add params to URL
            from urllib.parse import urlencode
            separator = '&' if '?' in path else '?'
            path += separator + urlencode(params)
            
        # Prepare headers
        request_headers = build_request_headers(
            self.browser_chars.characteristics,
            hostname,
            method,
            additional_headers=headers
        )
        
        # Handle cookies
        if self.cookies:
            cookie_str = '; '.join(f'{k}={v}' for k, v in self.cookies.items())
            request_headers['Cookie'] = cookie_str
            
        # Prepare body
        body = ""
        if json is not None:
            body = json.dumps(json)
            request_headers['Content-Type'] = 'application/json'
        elif data is not None:
            if isinstance(data, dict):
                from urllib.parse import urlencode
                body = urlencode(data)
                request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                body = str(data)
                
        # Apply evasion if needed
        if self.evasion_level != EvasionLevel.BASIC:
            self._apply_evasion_techniques(request_headers)
            
        # Rotate fingerprint if needed
        if self.fingerprint_rotation != FingerprintRotationStrategy.NONE:
            self._rotate_fingerprint()
            
        # Connect
        if not self.engine.connect(hostname, port):
            raise ConnectionError(f"Failed to connect to {hostname}:{port}")
            
        try:
            # Send request
            if not self.engine.send_request(method, path, request_headers, body):
                raise TLSError("Failed to send request")
                
            # Receive response
            raw_response = self.engine.receive_response()
            if not raw_response:
                raise TLSError("Failed to receive response")
                
            # Parse response
            response = parse_response(raw_response, url)
            
            # Update cookies
            if 'set-cookie' in response.headers:
                self._update_cookies(response.headers['set-cookie'])
                
            # Handle redirects
            if allow_redirects and response.is_redirect:
                return self._handle_redirect(response, method, **kwargs)
                
            # Record metrics
            if self.perf_monitor:
                elapsed = time.time() - start_time
                self.perf_monitor.record_request(
                    len(body),
                    len(raw_response),
                    int(elapsed * 1000)
                )
                
            return response
            
        except Exception as e:
            if self.perf_monitor:
                self.perf_monitor.record_error()
            raise
        finally:
            self.engine.close()
            
    def session(self) -> 'Session':
        """Create a session for multiple requests."""
        from .session import Session
        return Session(self)
    
    def close(self):
        """Close the client and cleanup resources."""
        if not self._closed:
            self.engine.close()
            self._closed = True
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def _apply_evasion_techniques(self, headers: Dict[str, str]):
        """Apply advanced evasion techniques."""
        # Add timing variations
        import random
        time.sleep(random.uniform(0.1, 0.3))
        
        # Randomize header order
        items = list(headers.items())
        random.shuffle(items[2:])  # Keep first two headers in place
        headers.clear()
        headers.update(items)
        
    def _rotate_fingerprint(self):
        """Rotate TLS fingerprint based on strategy."""
        if self.fingerprint_rotation == FingerprintRotationStrategy.RANDOM:
            self.engine.rotate_fingerprint()
        elif self.fingerprint_rotation == FingerprintRotationStrategy.INTELLIGENT:
            # Intelligent rotation based on success rates
            current_fp = self.engine.get_current_fingerprint()
            # Would check success rates and choose optimal fingerprint
            
    def _update_cookies(self, cookie_header: Union[str, List[str]]):
        """Update cookies from Set-Cookie headers."""
        if isinstance(cookie_header, str):
            cookie_header = [cookie_header]
            
        for cookie in cookie_header:
            # Simple cookie parsing
            parts = cookie.split(';')[0].split('=', 1)
            if len(parts) == 2:
                self.cookies[parts[0].strip()] = parts[1].strip()
                
    def _handle_redirect(self, response: 'Response', method: str, **kwargs) -> 'Response':
        """Handle HTTP redirects."""
        location = response.headers.get('location')
        if not location:
            return response
            
        # Build absolute URL
        next_url = urljoin(response.url, location)
        
        # For 303, always use GET
        if response.status_code == 303:
            method = 'GET'
            kwargs.pop('data', None)
            kwargs.pop('json', None)
            
        return self.request(method, next_url, **kwargs)


class AsyncClient:
    """
    Asynchronous Advanced TLS Client.
    
    Example:
        >>> async with AsyncClient() as client:
        ...     response = await client.get('https://example.com')
        ...     print(response.text)
    """
    
    def __init__(self, **kwargs):
        """Initialize async client with same parameters as Client."""
        self.sync_client = Client(**kwargs)
        self.engine = AsyncTLSEngine()
        self._closed = False
        
    async def get(self, url: str, **kwargs) -> 'Response':
        """Async GET request."""
        return await self.request('GET', url, **kwargs)
        
    async def post(self, url: str, **kwargs) -> 'Response':
        """Async POST request."""
        return await self.request('POST', url, **kwargs)
        
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> 'Response':
        """Send async HTTP request."""
        # Use thread pool for now, full async implementation would be better
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.sync_client.request, 
            method, 
            url,
            **kwargs
        )
        
    async def close(self):
        """Close async client."""
        if not self._closed:
            self.sync_client.close()
            self._closed = True
            
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_client(**kwargs) -> Client:
    """Factory function to create a client."""
    return Client(**kwargs)


def create_async_client(**kwargs) -> AsyncClient:
    """Factory function to create an async client."""
    return AsyncClient(**kwargs)


class Response:
    """HTTP Response object."""
    
    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        body: bytes,
        url: str,
        encoding: Optional[str] = None
    ):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.url = url
        self.encoding = encoding or 'utf-8'
        
    @property
    def text(self) -> str:
        """Get response body as text."""
        return self.body.decode(self.encoding)
        
    @property
    def json(self) -> Dict:
        """Parse response body as JSON."""
        return json.loads(self.text)
        
    @property
    def ok(self) -> bool:
        """Check if response status is successful."""
        return 200 <= self.status_code < 300
        
    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect."""
        return 300 <= self.status_code < 400
        
    def raise_for_status(self):
        """Raise exception for non-2xx status codes."""
        if not self.ok:
            raise TLSError(f"HTTP {self.status_code}: {self.text[:100]}")
            
    def __repr__(self):
        return f"<Response [{self.status_code}]>"