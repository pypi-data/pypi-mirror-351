#!/usr/bin/env python3
"""
Basic usage examples for Advanced TLS Library.

This demonstrates the simplest ways to use the library for common tasks.
"""

import advanced_tls as atls

def basic_get_request():
    """Simple GET request with default Chrome fingerprint."""
    print("🔥 Basic GET Request")
    
    # Create client with default settings
    client = atls.Client()
    
    # Make request
    response = client.get('https://httpbin.org/get')
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(list(response.headers.items())[:3])}...")
    print(f"Body: {response.text[:100]}...")
    
    client.close()


def browser_specific_request():
    """Request with specific browser simulation."""
    print("\n🦊 Firefox Browser Simulation")
    
    # Create Firefox client
    client = atls.Client(browser='firefox')
    
    response = client.get('https://httpbin.org/headers')
    data = response.json
    
    print(f"User-Agent: {data['headers']['User-Agent']}")
    print(f"Accept: {data['headers']['Accept']}")
    
    client.close()


def multiple_requests():
    """Multiple requests with session persistence."""
    print("\n🔄 Session with Multiple Requests")
    
    with atls.Client(browser='chrome') as client:
        # First request
        resp1 = client.get('https://httpbin.org/cookies/set/session/abc123')
        print(f"Set cookie response: {resp1.status_code}")
        
        # Second request with cookies
        resp2 = client.get('https://httpbin.org/cookies')
        cookies = resp2.json.get('cookies', {})
        print(f"Received cookies: {cookies}")


def post_request_with_data():
    """POST request with form data."""
    print("\n📤 POST Request with Data")
    
    client = atls.Client()
    
    # Form data
    data = {
        'username': 'testuser',
        'password': 'secret123',
        'remember': 'true'
    }
    
    response = client.post('https://httpbin.org/post', data=data)
    result = response.json
    
    print(f"Form data received: {result['form']}")
    
    client.close()


def json_post_request():
    """POST request with JSON data."""
    print("\n📋 JSON POST Request")
    
    client = atls.Client()
    
    # JSON data
    json_data = {
        'user_id': 12345,
        'action': 'login',
        'metadata': {
            'ip': '192.168.1.1',
            'browser': 'Chrome'
        }
    }
    
    response = client.post('https://httpbin.org/post', json=json_data)
    result = response.json
    
    print(f"JSON data received: {result['json']}")
    print(f"Content-Type: {result['headers']['Content-Type']}")
    
    client.close()


def custom_headers():
    """Request with custom headers."""
    print("\n🏷️  Custom Headers")
    
    client = atls.Client()
    
    headers = {
        'X-API-Key': 'secret-api-key-123',
        'X-Client-Version': '2.1.4',
        'X-Custom-Header': 'custom-value'
    }
    
    response = client.get('https://httpbin.org/headers', headers=headers)
    received_headers = response.json['headers']
    
    print(f"API Key: {received_headers.get('X-Api-Key')}")
    print(f"Client Version: {received_headers.get('X-Client-Version')}")
    
    client.close()


def error_handling():
    """Proper error handling."""
    print("\n⚠️  Error Handling")
    
    client = atls.Client()
    
    try:
        # This will return 404
        response = client.get('https://httpbin.org/status/404')
        print(f"Status: {response.status_code}")
        
        # Check if successful
        if not response.ok:
            print(f"Request failed with status {response.status_code}")
            
    except atls.ConnectionError as e:
        print(f"Connection error: {e}")
    except atls.TimeoutError as e:
        print(f"Timeout error: {e}")
    except atls.TLSError as e:
        print(f"TLS error: {e}")
    finally:
        client.close()


def timeout_configuration():
    """Configure request timeout."""
    print("\n⏱️  Timeout Configuration")
    
    # Client with 5 second timeout
    client = atls.Client(timeout=5.0)
    
    try:
        # This endpoint delays for 3 seconds
        response = client.get('https://httpbin.org/delay/3')
        print(f"Request completed: {response.status_code}")
    except atls.TimeoutError:
        print("Request timed out!")
    
    client.close()


def main():
    """Run all basic examples."""
    print("🚀 Advanced TLS Library - Basic Usage Examples\n")
    
    try:
        basic_get_request()
        browser_specific_request()
        multiple_requests()
        post_request_with_data()
        json_post_request()
        custom_headers()
        error_handling()
        timeout_configuration()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()