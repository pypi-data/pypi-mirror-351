"""
Fallback implementations when native extensions are not available.
"""

import socket
import ssl
import time
from typing import Dict, Any, Optional
import warnings


class TLSEngine:
    """Fallback TLS engine using Python's ssl module."""
    
    def __init__(self):
        self.socket = None
        self.ssl_socket = None
        self.fingerprint = {}
        
    def initialize(self, profile, evasion_level):
        """Initialize with browser profile."""
        warnings.warn("Using fallback TLS engine - performance will be reduced")
        return True
        
    def initialize_custom(self, fingerprint):
        """Initialize with custom fingerprint."""
        self.fingerprint = fingerprint
        return True
        
    def set_connection_options(self, options):
        """Set connection options."""
        pass
        
    def connect(self, hostname: str, port: int) -> bool:
        """Connect using standard Python SSL."""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30.0)
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Connect
            self.socket.connect((hostname, port))
            self.ssl_socket = context.wrap_socket(
                self.socket, 
                server_hostname=hostname
            )
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def send_request(self, method: str, path: str, headers: Dict[str, str], body: str = "") -> bool:
        """Send HTTP request."""
        if not self.ssl_socket:
            return False
            
        try:
            # Build request
            request_lines = [f"{method} {path} HTTP/1.1"]
            for key, value in headers.items():
                request_lines.append(f"{key}: {value}")
            request_lines.append("")  # Empty line
            if body:
                request_lines.append(body)
                
            request_str = "\r\n".join(request_lines)
            
            # Send request
            self.ssl_socket.send(request_str.encode())
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False
            
    def receive_response(self) -> str:
        """Receive HTTP response."""
        if not self.ssl_socket:
            return ""
            
        try:
            # Receive response
            response = b""
            while True:
                chunk = self.ssl_socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                
                # Check if we have complete headers
                if b"\r\n\r\n" in response:
                    # We have headers, check for Content-Length
                    headers_end = response.find(b"\r\n\r\n")
                    headers_str = response[:headers_end].decode()
                    
                    # Simple content-length parsing
                    if "content-length:" in headers_str.lower():
                        for line in headers_str.split('\n'):
                            if line.lower().startswith('content-length:'):
                                length = int(line.split(':')[1].strip())
                                body_received = len(response) - headers_end - 4
                                if body_received >= length:
                                    return response.decode()
                    else:
                        # No content-length, assume chunked or connection close
                        time.sleep(0.1)  # Wait a bit more
                        if len(chunk) < 4096:  # Partial chunk, likely done
                            break
                            
            return response.decode()
        except Exception as e:
            print(f"Receive failed: {e}")
            return ""
            
    def close(self):
        """Close connection."""
        if self.ssl_socket:
            self.ssl_socket.close()
            self.ssl_socket = None
        if self.socket:
            self.socket.close()
            self.socket = None
            
    def get_current_fingerprint(self):
        """Get current fingerprint."""
        return self.fingerprint
        
    def rotate_fingerprint(self):
        """Rotate fingerprint."""
        pass
        
    def get_ja3_hash(self) -> str:
        """Get JA3 hash."""
        return "fallback_ja3"
        
    def get_ja4_hash(self) -> str:
        """Get JA4 hash."""
        return "fallback_ja4"
        
    def enable_ml_evasion(self, enable: bool):
        """Enable ML evasion."""
        pass


class AsyncTLSEngine:
    """Fallback async TLS engine."""
    
    def __init__(self):
        self.sync_engine = TLSEngine()
        
    def connect_async(self, hostname: str, port: int):
        """Connect asynchronously."""
        # In real implementation, would use asyncio
        self.sync_engine.connect(hostname, port)
        
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.sync_engine.ssl_socket is not None
        
    def get_connect_result(self) -> bool:
        """Get connection result."""
        return self.is_connected()


class BrowserProfileManager:
    """Fallback browser profile manager."""
    
    def __init__(self):
        pass
        
    def get_profile(self, profile):
        """Get browser profile."""
        # Return mock profile
        class MockProfile:
            def __init__(self):
                self.characteristics = MockCharacteristics()
                
        return MockProfile()


class MockCharacteristics:
    """Mock browser characteristics."""
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.accept_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }


class ConnectionPool:
    """Fallback connection pool."""
    
    def __init__(self, max_connections_per_host=None, max_idle_connections=None, idle_timeout_secs=None):
        warnings.warn("Using fallback connection pool - performance will be reduced")
        
    def get_stats(self):
        """Get pool statistics."""
        return {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0
        }
        
    def shutdown(self):
        """Shutdown pool."""
        pass


class PerformanceMonitor:
    """Fallback performance monitor."""
    
    def __init__(self):
        self.stats = {
            'request_count': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'error_count': 0
        }
        
    def record_request(self, bytes_sent: int, bytes_received: int, latency_ms: int):
        """Record request metrics."""
        self.stats['request_count'] += 1
        self.stats['bytes_sent'] += bytes_sent
        self.stats['bytes_received'] += bytes_received
        
    def record_error(self):
        """Record error."""
        self.stats['error_count'] += 1
        
    def get_stats(self):
        """Get statistics."""
        return self.stats
        
    def add_connection(self):
        """Add connection."""
        pass
        
    def remove_connection(self):
        """Remove connection."""
        pass