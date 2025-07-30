from dataclasses import dataclass
from typing import List, Optional, Dict
import hashlib
import random
from enum import Enum, auto


class FingerprintRotationStrategy(Enum):
    """Fingerprint rotation strategies."""
    NONE = auto()
    RANDOM = auto()
    SEQUENTIAL = auto()
    INTELLIGENT = auto()
    TIME_BASED = auto()


@dataclass
class TLSFingerprint:
    """TLS Fingerprint configuration."""
    cipher_suites: List[int]
    extensions: List[int]
    compression_methods: List[int]
    supported_groups: List[str]
    signature_algorithms: List[str]
    enable_grease: bool = True
    ja3_string: Optional[str] = None
    ja4_string: Optional[str] = None
    
    def calculate_ja3(self) -> str:
        """Calculate JA3 fingerprint hash."""
        # Build JA3 string
        parts = []
        
        # TLS Version (771 = TLS 1.2)
        parts.append("771")
        
        # Cipher Suites
        cipher_str = "-".join(str(c) for c in self.cipher_suites)
        parts.append(cipher_str)
        
        # Extensions
        ext_str = "-".join(str(e) for e in self.extensions)
        parts.append(ext_str)
        
        # Supported Groups (Elliptic Curves)
        group_ids = []
        for group in self.supported_groups:
            if group == "x25519":
                group_ids.append("29")
            elif group == "secp256r1":
                group_ids.append("23")
            elif group == "secp384r1":
                group_ids.append("24")
            elif group == "secp521r1":
                group_ids.append("25")
                
        group_str = "-".join(group_ids)
        parts.append(group_str)
        
        # Point Formats (always 0 for uncompressed)
        parts.append("0")
        
        # Join and hash
        ja3_string = ",".join(parts)
        self.ja3_string = ja3_string
        
        # Calculate MD5 hash
        ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()
        return ja3_hash
        
    def calculate_ja4(self) -> str:
        """Calculate JA4 fingerprint hash."""
        # JA4 format: protocol_sni_ciphers_extensions_alpn_signature
        parts = []
        
        # Protocol version
        parts.append("t13")  # TLS 1.3
        
        # SNI (d for domain)
        parts.append("d")
        
        # Number of ciphers (2 digits)
        parts.append(f"{len(self.cipher_suites):02d}")
        
        # Number of extensions (2 digits)
        parts.append(f"{len(self.extensions):02d}")
        
        # ALPN
        parts.append("h2")  # HTTP/2
        
        # First cipher suite
        if self.cipher_suites:
            parts.append(f"{self.cipher_suites[0]:04x}")
        else:
            parts.append("0000")
            
        # Hash of sorted extensions
        sorted_exts = sorted(self.extensions)
        ext_str = ",".join(str(e) for e in sorted_exts)
        ext_hash = hashlib.sha256(ext_str.encode()).hexdigest()[:12]
        parts.append(ext_hash)
        
        self.ja4_string = "_".join(parts)
        return self.ja4_string
        
    def with_grease(self) -> 'TLSFingerprint':
        """Add GREASE values to fingerprint."""
        if not self.enable_grease:
            return self
            
        # GREASE values
        grease_values = [
            0x0a0a, 0x1a1a, 0x2a2a, 0x3a3a,
            0x4a4a, 0x5a5a, 0x6a6a, 0x7a7a,
            0x8a8a, 0x9a9a, 0xaaaa, 0xbaba,
            0xcaca, 0xdada, 0xeaea, 0xfafa
        ]
        
        # Add GREASE cipher suite
        grease_cipher = random.choice(grease_values)
        position = random.randint(0, len(self.cipher_suites))
        self.cipher_suites.insert(position, grease_cipher)
        
        # Add GREASE extension
        grease_ext = random.choice(grease_values)
        position = random.randint(0, len(self.extensions))
        self.extensions.insert(position, grease_ext)
        
        return self
        
    def randomize(self) -> 'TLSFingerprint':
        """Randomize fingerprint ordering."""
        # Keep TLS 1.3 ciphers at the beginning
        tls13_ciphers = [c for c in self.cipher_suites if 0x1301 <= c <= 0x1305]
        other_ciphers = [c for c in self.cipher_suites if c not in tls13_ciphers]
        
        random.shuffle(other_ciphers)
        self.cipher_suites = tls13_ciphers + other_ciphers
        
        # Randomize extensions (keep important ones at start)
        important_exts = [0x0000, 0x0017, 0x002b]  # SNI, extended_master_secret, supported_versions
        other_exts = [e for e in self.extensions if e not in important_exts]
        
        random.shuffle(other_exts)
        self.extensions = important_exts + other_exts
        
        return self


class FingerprintDatabase:
    """Database of browser fingerprints."""
    
    def __init__(self):
        self.fingerprints = self._init_fingerprints()
        
    def _init_fingerprints(self) -> Dict[str, TLSFingerprint]:
        """Initialize fingerprint database."""
        return {
            'chrome_120': TLSFingerprint(
                cipher_suites=[
                    0x1301, 0x1302, 0x1303, 0xc02b, 0xc02f,
                    0xc02c, 0xc030, 0xcca9, 0xcca8, 0xc013,
                    0xc014, 0x009c, 0x009d, 0x002f, 0x0035
                ],
                extensions=[
                    0x0000, 0x0017, 0x0001, 0x0005, 0x0012,
                    0x0023, 0x002b, 0x002d, 0x0033
                ],
                compression_methods=[0x00],
                supported_groups=["x25519", "secp256r1", "secp384r1"],
                signature_algorithms=[
                    "ecdsa_secp256r1_sha256",
                    "rsa_pss_rsae_sha256",
                    "rsa_pkcs1_sha256",
                    "ecdsa_secp384r1_sha384",
                    "rsa_pss_rsae_sha384",
                    "rsa_pkcs1_sha384",
                    "rsa_pss_rsae_sha512",
                    "rsa_pkcs1_sha512"
                ]
            ),
            
            'firefox_115': TLSFingerprint(
                cipher_suites=[
                    0x1301, 0x1303, 0x1302, 0xcca9, 0xcca8,
                    0xc02b, 0xc02f, 0xc02c, 0xc030, 0xc009,
                    0xc013, 0xc00a, 0xc014
                ],
                extensions=[
                    0x0000, 0x0017, 0x0005, 0x0023, 0x0010,
                    0x002b, 0x002d, 0x0033
                ],
                compression_methods=[0x00],
                supported_groups=["x25519", "secp256r1", "secp384r1", "secp521r1"],
                signature_algorithms=[
                    "ecdsa_secp256r1_sha256",
                    "ecdsa_secp384r1_sha384",
                    "ecdsa_secp521r1_sha512",
                    "rsa_pss_rsae_sha256",
                    "rsa_pss_rsae_sha384",
                    "rsa_pss_rsae_sha512",
                    "rsa_pkcs1_sha256",
                    "rsa_pkcs1_sha384",
                    "rsa_pkcs1_sha512"
                ]
            ),
            
            'safari_17': TLSFingerprint(
                cipher_suites=[
                    0x1301, 0x1302, 0x1303, 0xc02c, 0xc02b,
                    0xcca9, 0xc030, 0xc02f, 0xcca8, 0xc00a,
                    0xc009, 0xc014, 0xc013
                ],
                extensions=[
                    0x0000, 0x0017, 0x0010, 0x0005, 0x0023,
                    0x002b, 0x0033
                ],
                compression_methods=[0x00],
                supported_groups=["x25519", "secp256r1", "secp384r1"],
                signature_algorithms=[
                    "ecdsa_secp256r1_sha256",
                    "rsa_pss_rsae_sha256",
                    "rsa_pkcs1_sha256",
                    "ecdsa_secp384r1_sha384",
                    "ecdsa_secp521r1_sha512",
                    "rsa_pss_rsae_sha384",
                    "rsa_pss_rsae_sha512",
                    "rsa_pkcs1_sha384",
                    "rsa_pkcs1_sha512"
                ]
            ),
        }
        
    def get_fingerprint(self, browser: str) -> Optional[TLSFingerprint]:
        """Get fingerprint for browser."""
        return self.fingerprints.get(browser)
        
    def get_random_fingerprint(self) -> TLSFingerprint:
        """Get random fingerprint from database."""
        return random.choice(list(self.fingerprints.values()))
        
    def get_weighted_fingerprint(self) -> TLSFingerprint:
        """Get fingerprint based on market share."""
        weights = {
            'chrome_120': 0.65,
            'firefox_115': 0.03,
            'safari_17': 0.19,
        }
        
        browsers = list(weights.keys())
        probs = list(weights.values())
        
        chosen = random.choices(browsers, weights=probs)[0]
        return self.fingerprints[chosen]


class FingerprintBuilder:
    """Builder for custom TLS fingerprints."""
    
    def __init__(self):
        self.fingerprint = TLSFingerprint(
            cipher_suites=[],
            extensions=[],
            compression_methods=[0x00],
            supported_groups=[],
            signature_algorithms=[]
        )
        
    def with_cipher_suites(self, suites: List[int]) -> 'FingerprintBuilder':
        """Set cipher suites."""
        self.fingerprint.cipher_suites = suites
        return self
        
    def with_extensions(self, extensions: List[int]) -> 'FingerprintBuilder':
        """Set extensions."""
        self.fingerprint.extensions = extensions
        return self
        
    def with_supported_groups(self, groups: List[str]) -> 'FingerprintBuilder':
        """Set supported groups."""
        self.fingerprint.supported_groups = groups
        return self
        
    def with_signature_algorithms(self, algos: List[str]) -> 'FingerprintBuilder':
        """Set signature algorithms."""
        self.fingerprint.signature_algorithms = algos
        return self
        
    def enable_grease(self, enable: bool = True) -> 'FingerprintBuilder':
        """Enable GREASE values."""
        self.fingerprint.enable_grease = enable
        return self
        
    def build(self) -> TLSFingerprint:
        """Build the fingerprint."""
        # Validate
        if not self.fingerprint.cipher_suites:
            raise ValueError("Cipher suites cannot be empty")
            
        if not self.fingerprint.extensions:
            raise ValueError("Extensions cannot be empty")
            
        # Calculate hashes
        self.fingerprint.calculate_ja3()
        self.fingerprint.calculate_ja4()
        
        return self.fingerprint


def create_custom_fingerprint() -> TLSFingerprint:
    """Create a custom fingerprint with builder."""
    return (FingerprintBuilder()
            .with_cipher_suites([0x1301, 0x1302, 0x1303, 0xc02b, 0xc02f])
            .with_extensions([0x0000, 0x0017, 0x002b, 0x0033])
            .with_supported_groups(["x25519", "secp256r1"])
            .with_signature_algorithms(["ecdsa_secp256r1_sha256", "rsa_pss_rsae_sha256"])
            .enable_grease()
            .build())


def mix_fingerprints(fp1: TLSFingerprint, fp2: TLSFingerprint, weight: float = 0.5) -> TLSFingerprint:
    """Mix two fingerprints to create a hybrid."""
    # Take ciphers from both
    fp1_count = int(len(fp1.cipher_suites) * weight)
    fp2_count = len(fp2.cipher_suites) - fp1_count
    
    mixed_ciphers = fp1.cipher_suites[:fp1_count] + fp2.cipher_suites[:fp2_count]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ciphers = []
    for cipher in mixed_ciphers:
        if cipher not in seen:
            seen.add(cipher)
            unique_ciphers.append(cipher)
            
    # Mix extensions similarly
    mixed_extensions = list(set(fp1.extensions + fp2.extensions))
    
    return TLSFingerprint(
        cipher_suites=unique_ciphers,
        extensions=mixed_extensions,
        compression_methods=fp1.compression_methods,
        supported_groups=fp1.supported_groups,
        signature_algorithms=fp1.signature_algorithms,
        enable_grease=fp1.enable_grease or fp2.enable_grease
    )