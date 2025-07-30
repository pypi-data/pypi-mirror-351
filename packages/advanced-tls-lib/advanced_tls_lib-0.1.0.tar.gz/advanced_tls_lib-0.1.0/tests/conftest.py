#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Advanced TLS Library tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import advanced_tls as atls


@pytest.fixture
def mock_tls_engine():
    """Mock TLS engine for testing."""
    engine = Mock()
    engine.initialize.return_value = True
    engine.initialize_custom.return_value = True
    engine.connect.return_value = True
    engine.send_request.return_value = True
    engine.receive_response.return_value = 'HTTP/1.1 200 OK\r\n\r\n{"test": "response"}'
    engine.close.return_value = None
    engine.get_ja3_hash.return_value = "mock_ja3_hash"
    engine.get_ja4_hash.return_value = "mock_ja4_hash"
    engine.get_current_fingerprint.return_value = Mock()
    engine.rotate_fingerprint.return_value = None
    engine.enable_ml_evasion.return_value = None
    return engine


@pytest.fixture
def mock_client(mock_tls_engine):
    """Mock client for testing."""
    with patch('advanced_tls.client.TLSEngine') as mock_engine_class:
        mock_engine_class.return_value = mock_tls_engine
        client = atls.Client()
        yield client
        client.close()


@pytest.fixture
def sample_fingerprint():
    """Sample TLS fingerprint for testing."""
    from advanced_tls.fingerprint import TLSFingerprint
    
    return TLSFingerprint(
        cipher_suites=[0x1301, 0x1302, 0x1303, 0xc02b, 0xc02f],
        extensions=[0x0000, 0x0017, 0x002b, 0x0033],
        compression_methods=[0x00],
        supported_groups=["x25519", "secp256r1", "secp384r1"],
        signature_algorithms=[
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256",
            "rsa_pkcs1_sha256"
        ]
    )


@pytest.fixture
def sample_response():
    """Sample HTTP response for testing."""
    return atls.client.Response(
        status_code=200,
        headers={
            'content-type': 'application/json',
            'content-length': '25'
        },
        body=b'{"status": "success"}',
        url='https://example.com/test'
    )


@pytest.fixture
def chrome_characteristics():
    """Chrome browser characteristics for testing."""
    from advanced_tls.profiles import BrowserCharacteristics
    chars = BrowserCharacteristics(atls.BrowserProfile.CHROME_LATEST)
    return chars


@pytest.fixture
def firefox_characteristics():
    """Firefox browser characteristics for testing."""
    from advanced_tls.profiles import BrowserCharacteristics
    chars = BrowserCharacteristics(atls.BrowserProfile.FIREFOX_LATEST)
    return chars


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_connection_pool():
    """Mock connection pool for testing."""
    pool = Mock()
    pool.get_stats.return_value = {
        'total_connections': 5,
        'active_connections': 2,
        'idle_connections': 3,
        'connections_created': 10,
        'connections_closed': 5,
        'connections_reused': 8
    }
    pool.shutdown.return_value = None
    return pool


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitor for testing."""
    monitor = Mock()
    monitor.record_request.return_value = None
    monitor.record_error.return_value = None
    monitor.add_connection.return_value = None
    monitor.remove_connection.return_value = None
    monitor.get_stats.return_value = {
        'request_count': 15,
        'bytes_sent': 2048,
        'bytes_received': 4096,
        'error_count': 1,
        'avg_latency_ms': 150,
        'p99_latency_ms': 500,
        'requests_per_second': 10.5
    }
    return monitor


@pytest.fixture(params=[
    atls.BrowserProfile.CHROME_LATEST,
    atls.BrowserProfile.FIREFOX_LATEST,
    atls.BrowserProfile.SAFARI_17,
])
def browser_profile(request):
    """Parametrized browser profiles for testing."""
    return request.param


@pytest.fixture(params=[
    atls.EvasionLevel.BASIC,
    atls.EvasionLevel.ADVANCED,
    atls.EvasionLevel.MAXIMUM,
])
def evasion_level(request):
    """Parametrized evasion levels for testing."""
    return request.param


@pytest.fixture
def test_urls():
    """Common test URLs."""
    return {
        'get': 'https://httpbin.org/get',
        'post': 'https://httpbin.org/post',
        'headers': 'https://httpbin.org/headers',
        'json': 'https://httpbin.org/json',
        'status_200': 'https://httpbin.org/status/200',
        'status_404': 'https://httpbin.org/status/404',
        'status_500': 'https://httpbin.org/status/500',
        'delay': 'https://httpbin.org/delay/1',
        'redirect': 'https://httpbin.org/redirect/1',
    }


@pytest.fixture
def sample_headers():
    """Sample HTTP headers for testing."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


@pytest.fixture
def sample_form_data():
    """Sample form data for testing."""
    return {
        'username': 'testuser',
        'password': 'secret123',
        'email': 'test@example.com',
        'remember': 'true'
    }


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {
        'user_id': 12345,
        'action': 'test_action',
        'data': {
            'key1': 'value1',
            'key2': 42,
            'key3': True
        },
        'timestamp': '2024-01-01T12:00:00Z'
    }


# Markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark"
    )


# Skip network tests if no internet connection
@pytest.fixture(autouse=True)
def skip_network_tests(request):
    """Skip network tests if no internet connection."""
    if request.node.get_closest_marker('network'):
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            pytest.skip("No internet connection available")


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup resources after each test."""
    yield
    # Cleanup code here if needed
    pass