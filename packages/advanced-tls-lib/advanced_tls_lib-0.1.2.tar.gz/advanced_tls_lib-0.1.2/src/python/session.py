from typing import Dict, Optional, Any, List
import asyncio
from contextlib import contextmanager, asynccontextmanager
import time

from .client import Client, AsyncClient, Response
from .profiles import BrowserProfile
from .evasion import EvasionLevel


class Session:
    """
    Session object for maintaining state across requests.
    
    Example:
        >>> client = Client()
        >>> with client.session() as session:
        ...     response = session.get('https://example.com/login')
        ...     response = session.post('https://example.com/login', data={'user': 'test'})
    """
    
    def __init__(self, client: Client):
        self.client = client
        self.cookies = {}
        self.headers = {}
        self.auth = None
        self.proxies = {}
        self.verify = True
        self.cert = None
        self.max_redirects = 10
        self.trust_env = True
        self.stream = False
        
        # Session-specific state
        self._base_url = None
        self._request_count = 0
        self._last_response = None
        
    def get(self, url: str, **kwargs) -> Response:
        """Send GET request in session context."""
        return self.request('GET', url, **kwargs)
        
    def post(self, url: str, **kwargs) -> Response:
        """Send POST request in session context."""
        return self.request('POST', url, **kwargs)
        
    def put(self, url: str, **kwargs) -> Response:
        """Send PUT request in session context."""
        return self.request('PUT', url, **kwargs)
        
    def delete(self, url: str, **kwargs) -> Response:
        """Send DELETE request in session context."""
        return self.request('DELETE', url, **kwargs)
        
    def patch(self, url: str, **kwargs) -> Response:
        """Send PATCH request in session context."""
        return self.request('PATCH', url, **kwargs)
        
    def head(self, url: str, **kwargs) -> Response:
        """Send HEAD request in session context."""
        return self.request('HEAD', url, **kwargs)
        
    def options(self, url: str, **kwargs) -> Response:
        """Send OPTIONS request in session context."""
        return self.request('OPTIONS', url, **kwargs)
        
    def request(self, method: str, url: str, **kwargs) -> Response:
        """Send request with session state."""
        # Merge session cookies with request cookies
        request_cookies = kwargs.get('cookies', {})
        merged_cookies = {**self.cookies, **request_cookies}
        kwargs['cookies'] = merged_cookies
        
        # Merge session headers with request headers
        request_headers = kwargs.get('headers', {})
        merged_headers = {**self.headers, **request_headers}
        kwargs['headers'] = merged_headers
        
        # Apply session auth
        if self.auth and 'auth' not in kwargs:
            kwargs['auth'] = self.auth
            
        # Apply session proxies
        if self.proxies and 'proxies' not in kwargs:
            kwargs['proxies'] = self.proxies
            
        # Apply session verify
        if 'verify' not in kwargs:
            kwargs['verify'] = self.verify
            
        # Apply session cert
        if self.cert and 'cert' not in kwargs:
            kwargs['cert'] = self.cert
            
        # Apply max redirects
        if 'max_redirects' not in kwargs:
            kwargs['max_redirects'] = self.max_redirects
            
        # Make request
        response = self.client.request(method, url, **kwargs)
        
        # Update session state
        self._request_count += 1
        self._last_response = response
        
        # Update session cookies from response
        if 'set-cookie' in response.headers:
            self._update_cookies_from_response(response)
            
        return response
        
    def _update_cookies_from_response(self, response: Response):
        """Update session cookies from response."""
        set_cookie = response.headers.get('set-cookie')
        if isinstance(set_cookie, str):
            set_cookie = [set_cookie]
            
        for cookie in set_cookie or []:
            # Simple cookie parsing
            parts = cookie.split(';')[0].split('=', 1)
            if len(parts) == 2:
                key, value = parts
                self.cookies[key.strip()] = value.strip()
                
    def close(self):
        """Close the session."""
        # Session cleanup if needed
        pass
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    @property
    def request_count(self) -> int:
        """Get number of requests made in this session."""
        return self._request_count
        
    @property
    def last_response(self) -> Optional[Response]:
        """Get last response received."""
        return self._last_response
        
    def mount(self, prefix: str, adapter):
        """Mount a custom adapter for handling requests to a specific prefix."""
        # This would allow custom protocol handling
        pass
        
    def prepare_request(self, request) -> Any:
        """Prepare a request with session state."""
        # Would prepare request object with session configuration
        return request
        
    def rebuild_auth(self, prepared_request, response):
        """Rebuild authentication after redirect."""
        # Would handle auth updates after redirects
        pass
        
    def rebuild_proxies(self, prepared_request, proxies):
        """Rebuild proxy configuration."""
        # Would handle proxy updates
        pass
        
    def should_strip_auth(self, old_url: str, new_url: str) -> bool:
        """Check if auth should be stripped on redirect."""
        # Would check if redirecting to different host
        from urllib.parse import urlparse
        old_parsed = urlparse(old_url)
        new_parsed = urlparse(new_url)
        return old_parsed.hostname != new_parsed.hostname


class AsyncSession:
    """
    Async session for maintaining state across async requests.
    
    Example:
        >>> async with AsyncClient().session() as session:
        ...     response = await session.get('https://example.com')
    """
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.cookies = {}
        self.headers = {}
        self._request_count = 0
        self._last_response = None
        
    async def get(self, url: str, **kwargs) -> Response:
        """Send async GET request."""
        return await self.request('GET', url, **kwargs)
        
    async def post(self, url: str, **kwargs) -> Response:
        """Send async POST request."""
        return await self.request('POST', url, **kwargs)
        
    async def put(self, url: str, **kwargs) -> Response:
        """Send async PUT request."""
        return await self.request('PUT', url, **kwargs)
        
    async def delete(self, url: str, **kwargs) -> Response:
        """Send async DELETE request."""
        return await self.request('DELETE', url, **kwargs)
        
    async def request(self, method: str, url: str, **kwargs) -> Response:
        """Send async request with session state."""
        # Merge session state
        request_cookies = kwargs.get('cookies', {})
        merged_cookies = {**self.cookies, **request_cookies}
        kwargs['cookies'] = merged_cookies
        
        request_headers = kwargs.get('headers', {})
        merged_headers = {**self.headers, **request_headers}
        kwargs['headers'] = merged_headers
        
        # Make request
        response = await self.client.request(method, url, **kwargs)
        
        # Update session state
        self._request_count += 1
        self._last_response = response
        
        # Update cookies
        if 'set-cookie' in response.headers:
            self._update_cookies_from_response(response)
            
        return response
        
    def _update_cookies_from_response(self, response: Response):
        """Update session cookies from response."""
        set_cookie = response.headers.get('set-cookie')
        if isinstance(set_cookie, str):
            set_cookie = [set_cookie]
            
        for cookie in set_cookie or []:
            parts = cookie.split(';')[0].split('=', 1)
            if len(parts) == 2:
                key, value = parts
                self.cookies[key.strip()] = value.strip()
                
    async def close(self):
        """Close async session."""
        await self.client.close()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    @property
    def request_count(self) -> int:
        """Get number of requests made."""
        return self._request_count
        
    @property  
    def last_response(self) -> Optional[Response]:
        """Get last response."""
        return self._last_response


class ConnectionPool:
    """
    Connection pool for reusing connections.
    
    This is a simplified interface - the actual implementation
    uses the Rust connection pool for performance.
    """
    
    def __init__(self, max_connections: int = 100, max_keepalive: int = 20):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self._connections = {}
        
    def get_connection(self, host: str, port: int):
        """Get a connection from the pool."""
        key = f"{host}:{port}"
        # Simplified - would actually manage connection lifecycle
        return self._connections.get(key)
        
    def return_connection(self, host: str, port: int, connection):
        """Return a connection to the pool."""
        key = f"{host}:{port}"
        # Simplified - would actually validate and store connection
        self._connections[key] = connection
        
    def clear(self):
        """Clear all connections."""
        self._connections.clear()
        
    def close(self):
        """Close all connections."""
        # Would close all active connections
        self.clear()


@contextmanager
def temporary_session(**kwargs):
    """Create a temporary session context."""
    client = Client(**kwargs)
    session = client.session()
    try:
        yield session
    finally:
        session.close()
        client.close()


@asynccontextmanager
async def async_temporary_session(**kwargs):
    """Create a temporary async session context."""
    client = AsyncClient(**kwargs)
    session = AsyncSession(client)
    try:
        yield session
    finally:
        await session.close()