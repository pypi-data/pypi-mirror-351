#!/usr/bin/env python3
"""
Real-world usage scenarios for Advanced TLS Library.

These examples demonstrate practical use cases that developers commonly encounter.
"""

import advanced_tls as atls
import asyncio
import json
import time
from urllib.parse import urljoin

def web_scraping_with_rotation():
    """Web scraping with automatic browser rotation."""
    print("🕷️  Web Scraping with Browser Rotation")
    
    # Sites to scrape (using httpbin for demo)
    sites = [
        'https://httpbin.org/html',
        'https://httpbin.org/json', 
        'https://httpbin.org/xml',
    ]
    
    # Client with rotation for anti-detection
    client = atls.Client(
        browser_profile=atls.BrowserProfile.CHROME_LATEST,
        evasion_level=atls.EvasionLevel.ADVANCED,
        fingerprint_rotation=atls.FingerprintRotationStrategy.RANDOM
    )
    
    scraped_data = []
    
    for i, site in enumerate(sites):
        print(f"Scraping site {i+1}: {site}")
        
        try:
            response = client.get(site)
            
            if response.ok:
                # Extract data based on content type
                content_type = response.headers.get('content-type', '')
                
                if 'json' in content_type:
                    data = response.json
                elif 'html' in content_type:
                    data = {'html_length': len(response.text)}
                else:
                    data = {'content_length': len(response.text)}
                    
                scraped_data.append({
                    'url': site,
                    'status': response.status_code,
                    'data': data
                })
                
                print(f"  ✅ Success: {response.status_code}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        # Random delay between requests
        time.sleep(1 + (i * 0.5))
    
    print(f"\nScraped {len(scraped_data)} sites successfully")
    client.close()


def api_testing_multiple_browsers():
    """API testing across multiple browser fingerprints."""
    print("\n🧪 API Testing with Multiple Browsers")
    
    api_endpoint = 'https://httpbin.org/headers'
    browsers = [
        atls.BrowserProfile.CHROME_LATEST,
        atls.BrowserProfile.FIREFOX_LATEST,
        atls.BrowserProfile.SAFARI_17,
        atls.BrowserProfile.EDGE_LATEST,
    ]
    
    results = {}
    
    for browser in browsers:
        print(f"Testing with {browser.name}...")
        
        client = atls.Client(browser_profile=browser)
        
        try:
            response = client.get(api_endpoint)
            
            if response.ok:
                headers = response.json['headers']
                results[browser.name] = {
                    'user_agent': headers.get('User-Agent', 'Unknown'),
                    'accept': headers.get('Accept', 'Unknown'),
                    'status': response.status_code
                }
                print(f"  ✅ Success")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        client.close()
        time.sleep(0.5)
    
    # Compare results
    print("\n📊 Browser Comparison:")
    for browser, data in results.items():
        print(f"{browser}:")
        print(f"  User-Agent: {data['user_agent'][:60]}...")


async def concurrent_api_calls():
    """High-performance concurrent API calls."""
    print("\n🚀 Concurrent API Calls")
    
    # Simulate multiple API endpoints
    endpoints = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/get',
        'https://httpbin.org/headers',
        'https://httpbin.org/user-agent',
    ]
    
    async with atls.AsyncClient(
        browser='chrome',
        evasion_level=atls.EvasionLevel.ADVANCED
    ) as client:
        
        print(f"Making {len(endpoints)} concurrent requests...")
        start_time = time.time()
        
        # Create tasks
        tasks = [client.get(url) for url in endpoints]
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        
        # Process results
        successful = 0
        failed = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"  ❌ Request {i+1} failed: {response}")
                failed += 1
            else:
                print(f"  ✅ Request {i+1} success: {response.status_code}")
                successful += 1
        
        print(f"\nCompleted in {elapsed:.2f}s")
        print(f"Successful: {successful}, Failed: {failed}")


def form_automation():
    """Automate form submissions with proper headers."""
    print("\n📝 Form Automation")
    
    client = atls.Client(browser='chrome')
    
    # Simulate multi-step form process
    print("Step 1: Get form page")
    form_page = client.get('https://httpbin.org/forms/post')
    print(f"  Form page: {form_page.status_code}")
    
    print("Step 2: Submit form data")
    form_data = {
        'custname': 'John Doe',
        'custtel': '+1234567890',
        'custemail': 'john@example.com',
        'size': 'large',
        'topping': 'bacon',
        'delivery': '13:00',
        'comments': 'Please ring the doorbell'
    }
    
    # Add proper form headers
    headers = {
        'Referer': 'https://httpbin.org/forms/post',
        'Origin': 'https://httpbin.org'
    }
    
    response = client.post(
        'https://httpbin.org/post',
        data=form_data,
        headers=headers
    )
    
    if response.ok:
        result = response.json
        print(f"  ✅ Form submitted successfully")
        print(f"  Received data: {list(result['form'].keys())}")
    else:
        print(f"  ❌ Form submission failed: {response.status_code}")
    
    client.close()


def session_based_workflow():
    """Complex session-based workflow simulation."""
    print("\n🔄 Session-Based Workflow")
    
    client = atls.Client(
        browser='chrome',
        evasion_level=atls.EvasionLevel.ADVANCED
    )
    
    with client.session() as session:
        print("1. Landing page visit")
        landing = session.get('https://httpbin.org/cookies')
        print(f"   Status: {landing.status_code}")
        
        print("2. Login simulation")
        login_data = {
            'username': 'testuser',
            'password': 'secret123'
        }
        
        login_response = session.post(
            'https://httpbin.org/cookies/set/sessionid/abc123',
            data=login_data
        )
        print(f"   Login: {login_response.status_code}")
        
        print("3. Navigate to protected area")
        protected = session.get('https://httpbin.org/cookies')
        cookies = protected.json.get('cookies', {})
        print(f"   Session ID: {cookies.get('sessionid', 'None')}")
        
        print("4. Perform authenticated action")
        action_data = {
            'action': 'update_profile',
            'data': json.dumps({'name': 'John Doe', 'email': 'john@example.com'})
        }
        
        action_response = session.post(
            'https://httpbin.org/post',
            json=action_data
        )
        print(f"   Action: {action_response.status_code}")
        
        print("5. Logout")
        logout = session.post('https://httpbin.org/cookies/delete/sessionid')
        print(f"   Logout: {logout.status_code}")
    
    client.close()


def proxy_rotation():
    """Demonstrate proxy rotation (simulation)."""
    print("\n🌐 Proxy Rotation Simulation")
    
    # Simulate different proxy configurations
    proxy_configs = [
        None,  # Direct connection
        # In real usage, you would have actual proxy URLs
        # 'http://proxy1.example.com:8080',
        # 'http://proxy2.example.com:8080',
    ]
    
    for i, proxy in enumerate(proxy_configs):
        print(f"Connection {i+1}: {'Direct' if proxy is None else proxy}")
        
        client = atls.Client(
            browser='chrome',
            proxy=proxy,
            evasion_level=atls.EvasionLevel.ADVANCED
        )
        
        try:
            response = client.get('https://httpbin.org/ip')
            
            if response.ok:
                ip_data = response.json
                print(f"  ✅ IP: {ip_data.get('origin', 'Unknown')}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        client.close()
        time.sleep(1)


def error_handling_and_retries():
    """Robust error handling with intelligent retries."""
    print("\n🔄 Error Handling and Retries")
    
    client = atls.Client(
        browser='chrome',
        evasion_level=atls.EvasionLevel.MAXIMUM
    )
    
    # URLs that will cause different types of errors
    test_urls = [
        'https://httpbin.org/status/200',  # Success
        'https://httpbin.org/status/404',  # Not found
        'https://httpbin.org/status/500',  # Server error
        'https://httpbin.org/delay/10',    # Timeout (with short timeout)
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Set short timeout for delay endpoint
                timeout = 3.0 if 'delay' in url else 30.0
                
                response = client.get(url)
                
                if response.ok:
                    print(f"  ✅ Success on attempt {retry_count + 1}")
                    break
                elif response.status_code >= 500:
                    print(f"  🔄 Server error, retrying... (attempt {retry_count + 1})")
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    print(f"  ❌ Client error: {response.status_code}")
                    break
                    
            except atls.TimeoutError:
                print(f"  ⏱️  Timeout on attempt {retry_count + 1}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                break
        
        if retry_count >= max_retries:
            print(f"  💥 Failed after {max_retries} attempts")
    
    client.close()


def main():
    """Run all real-world scenario examples."""
    print("🌍 Advanced TLS Library - Real-World Scenarios\n")
    
    try:
        web_scraping_with_rotation()
        api_testing_multiple_browsers()
        
        # Run async example
        print("\nRunning concurrent API calls...")
        asyncio.run(concurrent_api_calls())
        
        form_automation()
        session_based_workflow()
        proxy_rotation()
        error_handling_and_retries()
        
        print("\n🎊 All real-world examples completed!")
        
    except Exception as e:
        print(f"\n💥 Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()