#!/usr/bin/env python3
"""
Advanced features demonstration for Advanced TLS Library.

This shows the most powerful capabilities of the library.
"""

import asyncio
import time
import advanced_tls as atls
from advanced_tls import BrowserProfile, EvasionLevel, FingerprintRotationStrategy

def browser_fingerprint_rotation():
    """Demonstrate automatic browser fingerprint rotation."""
    print("🔄 Browser Fingerprint Rotation")
    
    # Client with intelligent fingerprint rotation
    client = atls.Client(
        browser_profile=BrowserProfile.CHROME_LATEST,
        fingerprint_rotation=FingerprintRotationStrategy.INTELLIGENT,
        evasion_level=EvasionLevel.MAXIMUM
    )
    
    # Make multiple requests - fingerprint will rotate
    for i in range(3):
        response = client.get('https://httpbin.org/headers')
        user_agent = response.json['headers']['User-Agent']
        print(f"Request {i+1} User-Agent: {user_agent}")
        
        # Small delay between requests
        time.sleep(1)
    
    client.close()


def custom_tls_fingerprint():
    """Create and use custom TLS fingerprint."""
    print("\n🔧 Custom TLS Fingerprint")
    
    # Create custom fingerprint
    fingerprint = atls.create_custom_fingerprint()
    
    # Client with custom fingerprint
    client = atls.Client(custom_fingerprint=fingerprint)
    
    response = client.get('https://httpbin.org/get')
    print(f"Custom fingerprint JA3: {client.engine.get_ja3_hash()}")
    print(f"Custom fingerprint JA4: {client.engine.get_ja4_hash()}")
    
    client.close()


def evasion_levels():
    """Demonstrate different evasion levels."""
    print("\n🥷 Detection Evasion Levels")
    
    evasion_levels = [
        EvasionLevel.BASIC,
        EvasionLevel.ADVANCED, 
        EvasionLevel.MAXIMUM
    ]
    
    for level in evasion_levels:
        print(f"\nTesting {level.name} evasion:")
        
        client = atls.Client(evasion_level=level)
        
        start_time = time.time()
        response = client.get('https://httpbin.org/get')
        elapsed = time.time() - start_time
        
        print(f"  Response time: {elapsed:.2f}s")
        print(f"  Status: {response.status_code}")
        
        client.close()


def mobile_browser_simulation():
    """Simulate mobile browsers."""
    print("\n📱 Mobile Browser Simulation")
    
    mobile_profiles = [
        BrowserProfile.CHROME_MOBILE,
        BrowserProfile.SAFARI_IOS,
    ]
    
    for profile in mobile_profiles:
        print(f"\nUsing {profile.name}:")
        
        client = atls.Client(browser_profile=profile)
        response = client.get('https://httpbin.org/headers')
        
        headers = response.json['headers']
        print(f"  User-Agent: {headers['User-Agent']}")
        if 'Sec-Ch-Ua-Mobile' in headers:
            print(f"  Mobile: {headers['Sec-Ch-Ua-Mobile']}")
        
        client.close()


async def async_requests():
    """Demonstrate async/await usage."""
    print("\n⚡ Async/Await Usage")
    
    async with atls.AsyncClient(browser='chrome') as client:
        # Concurrent requests
        tasks = []
        urls = [
            'https://httpbin.org/delay/1',
            'https://httpbin.org/delay/2', 
            'https://httpbin.org/delay/1',
        ]
        
        start_time = time.time()
        
        for url in urls:
            task = client.get(url)
            tasks.append(task)
            
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        print(f"Completed {len(responses)} requests in {elapsed:.2f}s")
        for i, resp in enumerate(responses):
            print(f"  Response {i+1}: {resp.status_code}")


def session_management():
    """Advanced session management."""
    print("\n🍪 Advanced Session Management")
    
    client = atls.Client(browser='chrome')
    
    with client.session() as session:
        # Login simulation
        login_data = {
            'username': 'testuser',
            'password': 'secret123'
        }
        
        # First request - login
        resp1 = session.post('https://httpbin.org/cookies/set/sessionid/abc123xyz')
        print(f"Login response: {resp1.status_code}")
        
        # Session automatically maintains cookies
        resp2 = session.get('https://httpbin.org/cookies')
        cookies = resp2.json.get('cookies', {})
        print(f"Session cookies: {cookies}")
        
        # Make authenticated request
        resp3 = session.get('https://httpbin.org/headers')
        cookie_header = resp3.json['headers'].get('Cookie', 'None')
        print(f"Cookie header sent: {cookie_header}")
    
    client.close()


def performance_monitoring():
    """Monitor performance metrics."""
    print("\n📊 Performance Monitoring")
    
    # Client with performance monitoring enabled
    client = atls.Client(performance_monitor=True)
    
    # Make several requests
    urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/post',
        'https://httpbin.org/headers',
    ]
    
    for url in urls:
        if 'post' in url:
            client.post(url, json={'test': 'data'})
        else:
            client.get(url)
    
    # Get performance stats
    if hasattr(client, 'perf_monitor') and client.perf_monitor:
        stats = client.perf_monitor.get_stats()
        print(f"Requests made: {stats.get('request_count', 0)}")
        print(f"Bytes sent: {stats.get('bytes_sent', 0)}")
        print(f"Bytes received: {stats.get('bytes_received', 0)}")
        print(f"Average latency: {stats.get('avg_latency_ms', 0)}ms")
    
    client.close()


def stealth_mode():
    """Ultra-stealth mode for maximum evasion."""
    print("\n👻 Stealth Mode")
    
    # Maximum stealth configuration
    client = atls.Client(
        browser_profile=BrowserProfile.CHROME_LATEST,
        evasion_level=EvasionLevel.MAXIMUM,
        fingerprint_rotation=FingerprintRotationStrategy.INTELLIGENT,
        enable_http2=True,
        enable_http3=False,  # Disable newer protocols for compatibility
    )
    
    # Enable ML evasion if available
    if hasattr(client.engine, 'enable_ml_evasion'):
        client.engine.enable_ml_evasion(True)
    
    # Make request with maximum stealth
    response = client.get('https://httpbin.org/headers')
    
    if response.ok:
        print("✅ Stealth request successful!")
        headers = response.json['headers']
        print(f"User-Agent: {headers['User-Agent'][:50]}...")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    client.close()


def challenge_solving():
    """Simulate challenge solving capabilities."""
    print("\n🧩 Challenge Solving Simulation")
    
    from advanced_tls.evasion import EvasionStrategy, DetectionSystem
    
    # Create evasion strategy
    strategy = EvasionStrategy(EvasionLevel.MAXIMUM)
    
    # Simulate detection
    mock_response = {
        'status_code': 403,
        'headers': {'CF-RAY': '12345'},
        'body': 'Checking your browser before accessing the website.'
    }
    
    # Detect system
    detected_system = strategy.detect_system(mock_response)
    if detected_system:
        print(f"Detected system: {detected_system.name}")
        
        # Get evasion headers
        evasion_headers = strategy.get_evasion_headers(detected_system)
        print(f"Evasion headers: {evasion_headers}")
        
        # Apply timing evasion
        print("Applying timing evasion...")
        strategy.apply_timing_evasion(request_number=1)
    else:
        print("No detection system detected")


def main():
    """Run all advanced examples."""
    print("🚀 Advanced TLS Library - Advanced Features Demo\n")
    
    try:
        browser_fingerprint_rotation()
        custom_tls_fingerprint()
        evasion_levels()
        mobile_browser_simulation()
        
        # Run async example
        print("\n⚡ Running async example...")
        asyncio.run(async_requests())
        
        session_management()
        performance_monitoring()
        stealth_mode()
        challenge_solving()
        
        print("\n🎉 All advanced examples completed!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()