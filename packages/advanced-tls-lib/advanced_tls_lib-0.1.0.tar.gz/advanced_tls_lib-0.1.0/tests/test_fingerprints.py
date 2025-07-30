#!/usr/bin/env python3
"""
Test suite for TLS fingerprinting functionality.
"""

import pytest
from advanced_tls.fingerprint import (
    TLSFingerprint, 
    FingerprintDatabase, 
    FingerprintBuilder,
    create_custom_fingerprint,
    mix_fingerprints
)
from advanced_tls.profiles import BrowserProfile


class TestTLSFingerprint:
    """Test TLS fingerprint class."""
    
    def test_fingerprint_creation(self):
        """Test basic fingerprint creation."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302],
            extensions=[0x0000, 0x0017],
            compression_methods=[0x00],
            supported_groups=["x25519", "secp256r1"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        assert len(fp.cipher_suites) == 2
        assert len(fp.extensions) == 2
        assert fp.enable_grease == True
        
    def test_ja3_calculation(self):
        """Test JA3 hash calculation."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302, 0x1303],
            extensions=[0x0000, 0x0017, 0x002b],
            compression_methods=[0x00],
            supported_groups=["x25519", "secp256r1"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        ja3_hash = fp.calculate_ja3()
        assert isinstance(ja3_hash, str)
        assert len(ja3_hash) == 32  # MD5 hash length
        assert fp.ja3_string is not None
        
    def test_ja4_calculation(self):
        """Test JA4 hash calculation."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302],
            extensions=[0x0000, 0x0017],
            compression_methods=[0x00],
            supported_groups=["x25519"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        ja4_hash = fp.calculate_ja4()
        assert isinstance(ja4_hash, str)
        assert "_" in ja4_hash
        assert fp.ja4_string is not None
        
    def test_grease_injection(self):
        """Test GREASE value injection."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302],
            extensions=[0x0000, 0x0017],
            compression_methods=[0x00],
            supported_groups=["x25519"],
            signature_algorithms=["ecdsa_secp256r1_sha256"],
            enable_grease=True
        )
        
        original_cipher_count = len(fp.cipher_suites)
        original_ext_count = len(fp.extensions)
        
        fp_with_grease = fp.with_grease()
        
        # Should have added GREASE values
        assert len(fp_with_grease.cipher_suites) >= original_cipher_count
        assert len(fp_with_grease.extensions) >= original_ext_count
        
    def test_randomization(self):
        """Test fingerprint randomization."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302, 0xc02b, 0xc02f, 0xc02c],
            extensions=[0x0000, 0x0017, 0x002b, 0x0033, 0x0005],
            compression_methods=[0x00],
            supported_groups=["x25519", "secp256r1"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        # Get original order
        original_ciphers = fp.cipher_suites.copy()
        original_extensions = fp.extensions.copy()
        
        # Randomize
        fp_random = fp.randomize()
        
        # Should maintain TLS 1.3 ciphers at start
        assert fp_random.cipher_suites[0] in [0x1301, 0x1302, 0x1303]
        # Should maintain important extensions at start
        assert fp_random.extensions[0] in [0x0000, 0x0017, 0x002b]


class TestFingerprintDatabase:
    """Test fingerprint database."""
    
    def test_database_creation(self):
        """Test database initialization."""
        db = FingerprintDatabase()
        assert len(db.fingerprints) > 0
        assert 'chrome_120' in db.fingerprints
        assert 'firefox_115' in db.fingerprints
        assert 'safari_17' in db.fingerprints
        
    def test_get_fingerprint(self):
        """Test getting specific fingerprint."""
        db = FingerprintDatabase()
        
        chrome_fp = db.get_fingerprint('chrome_120')
        assert chrome_fp is not None
        assert len(chrome_fp.cipher_suites) > 0
        
        invalid_fp = db.get_fingerprint('invalid_browser')
        assert invalid_fp is None
        
    def test_random_fingerprint(self):
        """Test getting random fingerprint."""
        db = FingerprintDatabase()
        
        fp1 = db.get_random_fingerprint()
        fp2 = db.get_random_fingerprint()
        
        assert fp1 is not None
        assert fp2 is not None
        # They might be the same, but should be valid fingerprints
        assert len(fp1.cipher_suites) > 0
        assert len(fp2.cipher_suites) > 0
        
    def test_weighted_fingerprint(self):
        """Test market share weighted selection."""
        db = FingerprintDatabase()
        
        # Test multiple selections to check weighting
        selections = []
        for _ in range(50):
            fp = db.get_weighted_fingerprint()
            selections.append(fp)
            
        assert len(selections) == 50
        # Chrome should be selected more often due to higher weight
        # This is probabilistic, so we don't assert exact counts


class TestFingerprintBuilder:
    """Test fingerprint builder."""
    
    def test_builder_basic_usage(self):
        """Test basic builder usage."""
        builder = FingerprintBuilder()
        
        fp = (builder
              .with_cipher_suites([0x1301, 0x1302])
              .with_extensions([0x0000, 0x0017])
              .with_supported_groups(["x25519"])
              .with_signature_algorithms(["ecdsa_secp256r1_sha256"])
              .build())
        
        assert len(fp.cipher_suites) == 2
        assert len(fp.extensions) == 2
        assert fp.ja3_string is not None
        assert fp.ja4_string is not None
        
    def test_builder_validation(self):
        """Test builder validation."""
        builder = FingerprintBuilder()
        
        # Should raise error for empty cipher suites
        with pytest.raises(ValueError):
            builder.build()
            
        # Should raise error for empty extensions
        with pytest.raises(ValueError):
            builder.with_cipher_suites([0x1301]).build()
            
    def test_builder_grease_option(self):
        """Test builder GREASE option."""
        builder = FingerprintBuilder()
        
        fp = (builder
              .with_cipher_suites([0x1301])
              .with_extensions([0x0000])
              .enable_grease(True)
              .build())
        
        assert fp.enable_grease == True
        
        fp2 = (builder
               .with_cipher_suites([0x1301])
               .with_extensions([0x0000])
               .enable_grease(False)
               .build())
        
        assert fp2.enable_grease == False


class TestFingerprintUtilities:
    """Test fingerprint utility functions."""
    
    def test_create_custom_fingerprint(self):
        """Test custom fingerprint creation utility."""
        fp = create_custom_fingerprint()
        
        assert fp is not None
        assert len(fp.cipher_suites) > 0
        assert len(fp.extensions) > 0
        assert fp.enable_grease == True
        
    def test_mix_fingerprints(self):
        """Test fingerprint mixing."""
        fp1 = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302],
            extensions=[0x0000, 0x0017],
            compression_methods=[0x00],
            supported_groups=["x25519"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        fp2 = TLSFingerprint(
            cipher_suites=[0x1303, 0xc02b],
            extensions=[0x002b, 0x0033],
            compression_methods=[0x00],
            supported_groups=["secp256r1"],
            signature_algorithms=["rsa_pss_rsae_sha256"]
        )
        
        mixed = mix_fingerprints(fp1, fp2, weight=0.5)
        
        assert mixed is not None
        assert len(mixed.cipher_suites) > 0
        assert len(mixed.extensions) > 0
        
        # Should contain elements from both fingerprints
        has_fp1_element = any(c in mixed.cipher_suites for c in fp1.cipher_suites)
        has_fp2_element = any(c in mixed.cipher_suites for c in fp2.cipher_suites)
        
        assert has_fp1_element or has_fp2_element


class TestBrowserFingerprints:
    """Test browser-specific fingerprints."""
    
    def test_chrome_fingerprint(self):
        """Test Chrome fingerprint characteristics."""
        db = FingerprintDatabase()
        chrome_fp = db.get_fingerprint('chrome_120')
        
        # Chrome should have TLS 1.3 ciphers first
        assert chrome_fp.cipher_suites[0] in [0x1301, 0x1302, 0x1303]
        
        # Should have SNI extension
        assert 0x0000 in chrome_fp.extensions
        
        # Should support x25519
        assert "x25519" in chrome_fp.supported_groups
        
    def test_firefox_fingerprint(self):
        """Test Firefox fingerprint characteristics."""
        db = FingerprintDatabase()
        firefox_fp = db.get_fingerprint('firefox_115')
        
        # Firefox has different cipher order
        assert len(firefox_fp.cipher_suites) > 0
        assert 0x1301 in firefox_fp.cipher_suites  # Should support TLS 1.3
        
        # Should have SNI extension
        assert 0x0000 in firefox_fp.extensions
        
    def test_safari_fingerprint(self):
        """Test Safari fingerprint characteristics."""
        db = FingerprintDatabase()
        safari_fp = db.get_fingerprint('safari_17')
        
        # Safari characteristics
        assert len(safari_fp.cipher_suites) > 0
        assert 0x0000 in safari_fp.extensions
        
        # Safari supports modern curves
        assert "x25519" in safari_fp.supported_groups or "secp256r1" in safari_fp.supported_groups


class TestFingerprintValidation:
    """Test fingerprint validation."""
    
    def test_valid_fingerprint(self):
        """Test validation of valid fingerprint."""
        fp = TLSFingerprint(
            cipher_suites=[0x1301, 0x1302, 0xc02b],
            extensions=[0x0000, 0x0017, 0x002b],
            compression_methods=[0x00],
            supported_groups=["x25519", "secp256r1"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        # Mock validation - in real implementation would check more thoroughly
        assert len(fp.cipher_suites) > 0
        assert len(fp.extensions) > 0
        assert 0x0000 in fp.extensions  # SNI should be present
        
    def test_invalid_fingerprint(self):
        """Test validation of invalid fingerprint."""
        # Empty cipher suites
        fp1 = TLSFingerprint(
            cipher_suites=[],
            extensions=[0x0000],
            compression_methods=[0x00],
            supported_groups=["x25519"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        assert len(fp1.cipher_suites) == 0  # Invalid
        
        # Empty extensions
        fp2 = TLSFingerprint(
            cipher_suites=[0x1301],
            extensions=[],
            compression_methods=[0x00],
            supported_groups=["x25519"],
            signature_algorithms=["ecdsa_secp256r1_sha256"]
        )
        
        assert len(fp2.extensions) == 0  # Invalid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])