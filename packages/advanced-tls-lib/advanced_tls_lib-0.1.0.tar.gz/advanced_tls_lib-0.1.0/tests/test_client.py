#!/usr/bin/env python3
"""
Test suite for Advanced TLS Library client functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
import advanced_tls as atls


class TestBasicClient:
    """Test basic client functionality."""
    
    def test_client_creation(self):
        """Test client can be created with default settings."""
        client = atls.Client()
        assert client is not None
        assert hasattr(client, 'browser_profile')
        assert hasattr(client, 'evasion_level')
        client.close()
        
    def test_client_with_browser(self):
        """Test client creation with specific browser."""
        client = atls.Client(browser='chrome')
        assert client.browser_profile == atls.BrowserProfile.CHROME_LATEST
        client.close()
        
        client = atls.Client(browser='firefox')
        assert client.browser_profile == atls.BrowserProfile.FIREFOX_LATEST
        client.close()
        
    def test_client_with_profile(self):
        """Test client creation with browser profile enum."""
        profile = atls.BrowserProfile.SAFARI_17
        client = atls.Client(browser_profile=profile)
        assert client.browser_profile == profile
        client.close()
        
    def test_context_manager(self):
        """Test client as context manager."""
        with atls.Client() as client:
            assert client is not None
            assert not client._closed
        # Should be closed after context
        
    def test_custom_fingerprint(self):
        """Test client with custom fingerprint."""
        fingerprint = atls.create_custom_fingerprint()
        client = atls.Client(custom_fingerprint=fingerprint)
        assert client is not None
        client.close()


class TestRequests:
    """Test HTTP request methods."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        client = atls.Client(browser='chrome')
        yield client
        client.close()
        
    def test_get_request(self, client):
        """Test GET request."""
        # Mock the underlying engine
        with patch.object(client.engine, 'connect', return_value=True), \
             patch.object(client.engine, 'send_request', return_value=True), \
             patch.object(client.engine, 'receive_response', return_value='HTTP/1.1 200 OK\r\n\r\n{"test": "data"}'):
            
            response = client.get('https://example.com')
            assert response.status_code == 200
            
    def test_post_request(self, client):
        """Test POST request with data."""
        with patch.object(client.engine, 'connect', return_value=True), \
             patch.object(client.engine, 'send_request', return_value=True), \
             patch.object(client.engine, 'receive_response', return_value='HTTP/1.1 200 OK\r\n\r\n{"result": "success"}'):
            
            data = {'key': 'value'}
            response = client.post('https://example.com', data=data)
            assert response.status_code == 200
            
    def test_json_request(self, client):
        """Test POST request with JSON data."""
        with patch.object(client.engine, 'connect', return_value=True), \
             patch.object(client.engine, 'send_request', return_value=True), \
             patch.object(client.engine, 'receive_response', return_value='HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"received": true}'):
            
            json_data = {'test': 'json'}
            response = client.post('https://example.com', json=json_data)
            assert response.status_code == 200
            
    def test_custom_headers(self, client):
        """Test request with custom headers."""
        with patch.object(client.engine, 'connect', return_value=True), \
             patch.object(client.engine, 'send_request', return_value=True), \
             patch.object(client.engine, 'receive_response', return_value='HTTP/1.1 200 OK\r\n\r\n{}'):
            
            headers = {'X-Custom': 'test-value'}
            response = client.get('https://example.com', headers=headers)
            assert response.status_code == 200


class TestResponse:
    """Test response object functionality."""
    
    def test_response_creation(self):
        """Test response object creation."""
        response = atls.client.Response(
            status_code=200,
            headers={'content-type': 'application/json'},
            body=b'{"test": "data"}',
            url='https://example.com'
        )
        
        assert response.status_code == 200
        assert response.ok
        assert not response.is_redirect
        assert 'test' in response.text
        
    def test_json_response(self):
        """Test JSON response parsing."""
        response = atls.client.Response(
            status_code=200,
            headers={'content-type': 'application/json'},
            body=b'{"key": "value", "number": 42}',
            url='https://example.com'
        )
        
        data = response.json
        assert data['key'] == 'value'
        assert data['number'] == 42
        
    def test_response_properties(self):
        """Test response properties."""
        # Successful response
        response = atls.client.Response(200, {}, b'success', 'https://example.com')
        assert response.ok
        assert not response.is_redirect
        
        # Redirect response
        response = atls.client.Response(302, {}, b'redirect', 'https://example.com')
        assert not response.ok
        assert response.is_redirect
        
        # Error response
        response = atls.client.Response(404, {}, b'not found', 'https://example.com')
        assert not response.ok
        assert not response.is_redirect
        
    def test_raise_for_status(self):
        """Test raise_for_status method."""
        # Successful response should not raise
        response = atls.client.Response(200, {}, b'ok', 'https://example.com')
        response.raise_for_status()  # Should not raise
        
        # Error response should raise
        response = atls.client.Response(404, {}, b'not found', 'https://example.com')
        with pytest.raises(atls.TLSError):
            response.raise_for_status()


class TestAsyncClient:
    """Test async client functionality."""
    
    @pytest.mark.asyncio
    async def test_async_client_creation(self):
        """Test async client creation."""
        async with atls.AsyncClient() as client:
            assert client is not None
            assert hasattr(client, 'sync_client')
            
    @pytest.mark.asyncio
    async def test_async_get_request(self):
        """Test async GET request."""
        async with atls.AsyncClient() as client:
            # Mock the sync client
            with patch.object(client.sync_client, 'request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = 'test response'
                mock_request.return_value = mock_response
                
                response = await client.get('https://example.com')
                assert response.status_code == 200
                
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async client context manager."""
        client = None
        async with atls.AsyncClient() as c:
            client = c
            assert not client._closed
        # Should be closed after context


class TestSession:
    """Test session functionality."""
    
    def test_session_creation(self):
        """Test session creation."""
        client = atls.Client()
        session = client.session()
        assert session is not None
        assert session.client == client
        session.close()
        client.close()
        
    def test_session_context_manager(self):
        """Test session context manager."""
        client = atls.Client()
        with client.session() as session:
            assert session is not None
        client.close()
        
    def test_session_cookie_persistence(self):
        """Test session cookie persistence."""
        client = atls.Client()
        with client.session() as session:
            # Set initial cookies
            session.cookies['test'] = 'value'
            
            # Mock responses
            with patch.object(session.client.engine, 'connect', return_value=True), \
                 patch.object(session.client.engine, 'send_request', return_value=True), \
                 patch.object(session.client.engine, 'receive_response', return_value='HTTP/1.1 200 OK\r\nSet-Cookie: session=abc123\r\n\r\nSuccess'):
                
                response = session.get('https://example.com')
                
                # Check that cookies were updated
                assert 'session' in session.cookies
        client.close()


class TestErrorHandling:
    """Test error handling."""
    
    def test_connection_error(self):
        """Test connection error handling."""
        client = atls.Client()
        
        with patch.object(client.engine, 'connect', return_value=False):
            with pytest.raises(atls.ConnectionError):
                client.get('https://example.com')
        
        client.close()
        
    def test_tls_error(self):
        """Test TLS error handling."""
        client = atls.Client()
        
        with patch.object(client.engine, 'connect', return_value=True), \
             patch.object(client.engine, 'send_request', return_value=False):
            with pytest.raises(atls.TLSError):
                client.get('https://example.com')
        
        client.close()
        
    def test_invalid_url(self):
        """Test invalid URL handling."""
        client = atls.Client()
        
        # This should handle gracefully or raise appropriate error
        try:
            response = client.get('invalid-url')
            # If it doesn't raise, check for error status
            assert not response.ok
        except (atls.InvalidURL, atls.TLSError):
            # Expected behavior
            pass
        
        client.close()


class TestFingerprinting:
    """Test fingerprinting functionality."""
    
    def test_browser_profiles(self):
        """Test different browser profiles."""
        profiles = [
            atls.BrowserProfile.CHROME_LATEST,
            atls.BrowserProfile.FIREFOX_LATEST,
            atls.BrowserProfile.SAFARI_17,
        ]
        
        for profile in profiles:
            client = atls.Client(browser_profile=profile)
            assert client.browser_profile == profile
            client.close()
            
    def test_evasion_levels(self):
        """Test different evasion levels."""
        levels = [
            atls.EvasionLevel.BASIC,
            atls.EvasionLevel.ADVANCED,
            atls.EvasionLevel.MAXIMUM,
        ]
        
        for level in levels:
            client = atls.Client(evasion_level=level)
            assert client.evasion_level == level
            client.close()
            
    def test_fingerprint_rotation(self):
        """Test fingerprint rotation."""
        client = atls.Client(
            fingerprint_rotation=atls.FingerprintRotationStrategy.RANDOM
        )
        assert client.fingerprint_rotation == atls.FingerprintRotationStrategy.RANDOM
        client.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])