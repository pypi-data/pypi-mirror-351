import re
import json
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs
import base64


def parse_headers(header_string: str) -> Dict[str, str]:
    """Parse HTTP headers from string."""
    headers = {}
    lines = header_string.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
            
    return headers


def build_request_headers(
    browser_chars,
    hostname: str,
    method: str = 'GET',
    path: str = '/',
    additional_headers: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """Build complete request headers for browser simulation."""
    headers = {
        'Host': hostname,
        'User-Agent': browser_chars.user_agent,
        'Accept': browser_chars.accept_headers['Accept'],
        'Accept-Language': browser_chars.accept_headers['Accept-Language'],
        'Accept-Encoding': browser_chars.accept_headers['Accept-Encoding'],
        'Connection': 'keep-alive',
    }
    
    # Add Sec-CH-UA headers if available
    if hasattr(browser_chars, 'sec_ch_ua') and browser_chars.sec_ch_ua:
        for key, value in browser_chars.sec_ch_ua.items():
            headers[key] = value
            
    # Add method-specific headers
    if method == 'GET':
        headers['Upgrade-Insecure-Requests'] = '1'
        
    # Add additional headers if provided
    if additional_headers:
        headers.update(additional_headers)
        
    return headers


def parse_response(raw_response: str, request_url: str):
    """Parse raw HTTP response."""
    from .client import Response
    
    # Split response into headers and body
    if '\r\n\r\n' in raw_response:
        header_part, body_part = raw_response.split('\r\n\r\n', 1)
    elif '\n\n' in raw_response:
        header_part, body_part = raw_response.split('\n\n', 1)
    else:
        header_part = raw_response
        body_part = ''
        
    # Parse status line
    lines = header_part.split('\n')
    status_line = lines[0]
    
    # Extract status code
    status_match = re.match(r'HTTP/[\d.]+ (\d+)', status_line)
    status_code = int(status_match.group(1)) if status_match else 200
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
            
    # Determine encoding
    encoding = 'utf-8'
    content_type = headers.get('content-type', '')
    if 'charset=' in content_type:
        encoding = content_type.split('charset=')[-1].strip()
        
    return Response(
        status_code=status_code,
        headers=headers,
        body=body_part.encode(encoding),
        url=request_url,
        encoding=encoding
    )


def encode_form_data(data: Dict[str, str]) -> str:
    """Encode form data for POST requests."""
    from urllib.parse import urlencode
    return urlencode(data)


def encode_json_data(data: Dict) -> str:
    """Encode JSON data for POST requests."""
    return json.dumps(data, separators=(',', ':'))


def decode_response_body(body: bytes, encoding: str = 'utf-8') -> str:
    """Decode response body with proper encoding."""
    try:
        return body.decode(encoding)
    except UnicodeDecodeError:
        # Try common encodings
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return body.decode(enc)
            except UnicodeDecodeError:
                continue
        # Fallback
        return body.decode('utf-8', errors='replace')


def extract_cookies(headers: Dict[str, str]) -> Dict[str, str]:
    """Extract cookies from Set-Cookie headers."""
    cookies = {}
    set_cookie = headers.get('set-cookie', '')
    
    if isinstance(set_cookie, list):
        cookie_strings = set_cookie
    else:
        cookie_strings = [set_cookie] if set_cookie else []
        
    for cookie_string in cookie_strings:
        # Simple cookie parsing
        parts = cookie_string.split(';')[0].split('=', 1)
        if len(parts) == 2:
            key, value = parts
            cookies[key.strip()] = value.strip()
            
    return cookies


def build_cookie_header(cookies: Dict[str, str]) -> str:
    """Build Cookie header from cookie dict."""
    return '; '.join(f'{k}={v}' for k, v in cookies.items())


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc


def is_redirect_status(status_code: int) -> bool:
    """Check if status code is a redirect."""
    return 300 <= status_code < 400


def get_redirect_url(response_headers: Dict[str, str], base_url: str) -> Optional[str]:
    """Get redirect URL from response headers."""
    location = response_headers.get('location')
    if not location:
        return None
        
    # Handle relative URLs
    if location.startswith('/'):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}://{parsed_base.netloc}{location}"
    elif not location.startswith('http'):
        return f"{base_url.rstrip('/')}/{location.lstrip('/')}"
    else:
        return location


def calculate_content_length(data: Union[str, bytes]) -> int:
    """Calculate content length for request body."""
    if isinstance(data, str):
        return len(data.encode('utf-8'))
    return len(data)


def generate_boundary() -> str:
    """Generate boundary for multipart/form-data."""
    import random
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=16))


def encode_multipart_form_data(
    fields: Dict[str, str],
    files: Dict[str, Tuple[str, bytes, str]] = None
) -> Tuple[str, bytes]:
    """Encode multipart/form-data."""
    boundary = generate_boundary()
    content_type = f'multipart/form-data; boundary={boundary}'
    
    body_parts = []
    
    # Add form fields
    for key, value in fields.items():
        part = f'--{boundary}\r\n'
        part += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
        part += f'{value}\r\n'
        body_parts.append(part.encode('utf-8'))
        
    # Add files
    if files:
        for key, (filename, data, content_type_file) in files.items():
            part = f'--{boundary}\r\n'
            part += f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'
            part += f'Content-Type: {content_type_file}\r\n\r\n'
            body_parts.append(part.encode('utf-8'))
            body_parts.append(data)
            body_parts.append(b'\r\n')
            
    # Add closing boundary
    body_parts.append(f'--{boundary}--\r\n'.encode('utf-8'))
    
    body = b''.join(body_parts)
    return content_type, body


def is_json_response(headers: Dict[str, str]) -> bool:
    """Check if response is JSON."""
    content_type = headers.get('content-type', '')
    return 'application/json' in content_type


def is_html_response(headers: Dict[str, str]) -> bool:
    """Check if response is HTML."""
    content_type = headers.get('content-type', '')
    return 'text/html' in content_type


def extract_charset(content_type: str) -> str:
    """Extract charset from Content-Type header."""
    if 'charset=' in content_type:
        charset = content_type.split('charset=')[-1].strip()
        return charset.split(';')[0].strip()
    return 'utf-8'


def normalize_header_name(name: str) -> str:
    """Normalize header name to lowercase."""
    return name.lower().strip()


def normalize_header_value(value: str) -> str:
    """Normalize header value."""
    return value.strip()


def parse_quality_values(header_value: str) -> List[Tuple[str, float]]:
    """Parse quality values from Accept headers."""
    items = []
    for item in header_value.split(','):
        item = item.strip()
        if ';q=' in item:
            value, quality = item.split(';q=', 1)
            try:
                quality = float(quality)
            except ValueError:
                quality = 1.0
        else:
            value = item
            quality = 1.0
        items.append((value.strip(), quality))
    
    return sorted(items, key=lambda x: x[1], reverse=True)


def build_user_agent(browser: str, version: str, os: str) -> str:
    """Build User-Agent string."""
    templates = {
        'chrome': 'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
        'firefox': 'Mozilla/5.0 ({os}) Gecko/20100101 Firefox/{version}',
        'safari': 'Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15',
    }
    
    template = templates.get(browser.lower(), templates['chrome'])
    return template.format(os=os, version=version)


def escape_header_value(value: str) -> str:
    """Escape header value for HTTP transmission."""
    # Remove control characters
    value = re.sub(r'[\x00-\x1F\x7F]', '', value)
    return value


def detect_encoding(body: bytes, headers: Dict[str, str]) -> str:
    """Detect encoding from headers and content."""
    # Check Content-Type header
    content_type = headers.get('content-type', '')
    if 'charset=' in content_type:
        return extract_charset(content_type)
        
    # Check HTML meta tag
    try:
        html_start = body[:2048].decode('latin-1')
        charset_match = re.search(
            r'<meta[^>]+charset[="\s]+([^">\s]+)',
            html_start,
            re.IGNORECASE
        )
        if charset_match:
            return charset_match.group(1).lower()
    except:
        pass
        
    # Default to UTF-8
    return 'utf-8'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = 'unnamed'
        
    return filename