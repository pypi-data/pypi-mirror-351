use std::sync::Arc;
use parking_lot::RwLock;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

/// High-performance cryptographic operations
pub struct CryptoEngine {
    rng: Arc<RwLock<StdRng>>,
}

impl CryptoEngine {
    pub fn new() -> Self {
        Self {
            rng: Arc::new(RwLock::new(StdRng::from_entropy())),
        }
    }

    /// Generate cryptographically secure random bytes
    pub fn random_bytes(&self, len: usize) -> Vec<u8> {
        let mut rng = self.rng.write();
        let mut bytes = vec![0u8; len];
        rng.fill(&mut bytes[..]);
        bytes
    }

    /// Generate GREASE values for TLS
    pub fn generate_grease_value(&self) -> u16 {
        const GREASE_VALUES: [u16; 16] = [
            0x0a0a, 0x1a1a, 0x2a2a, 0x3a3a,
            0x4a4a, 0x5a5a, 0x6a6a, 0x7a7a,
            0x8a8a, 0x9a9a, 0xaaaa, 0xbaba,
            0xcaca, 0xdada, 0xeaea, 0xfafa,
        ];

        let mut rng = self.rng.write();
        let index = rng.gen_range(0..GREASE_VALUES.len());
        GREASE_VALUES[index]
    }

    /// Shuffle array in-place (Fisher-Yates)
    pub fn shuffle<T>(&self, items: &mut [T]) {
        let mut rng = self.rng.write();
        let len = items.len();
        
        for i in (1..len).rev() {
            let j = rng.gen_range(0..=i);
            items.swap(i, j);
        }
    }

    /// Generate random padding for TLS
    pub fn generate_padding(&self, min: usize, max: usize) -> Vec<u8> {
        let mut rng = self.rng.write();
        let len = rng.gen_range(min..=max);
        vec![0u8; len]
    }
}

/// Fast hash functions for fingerprinting
pub mod hash {
    use std::hash::{Hash, Hasher};
    use std::collections::hash_map::DefaultHasher;

    /// FNV-1a hash for fast non-cryptographic hashing
    pub struct FnvHasher {
        state: u64,
    }

    impl FnvHasher {
        const FNV_PRIME: u64 = 1099511628211;
        const FNV_OFFSET_BASIS: u64 = 14695981039346656037;

        pub fn new() -> Self {
            Self {
                state: Self::FNV_OFFSET_BASIS,
            }
        }

        pub fn write(&mut self, bytes: &[u8]) {
            for &byte in bytes {
                self.state ^= u64::from(byte);
                self.state = self.state.wrapping_mul(Self::FNV_PRIME);
            }
        }

        pub fn finish(&self) -> u64 {
            self.state
        }
    }

    /// xxHash for high-speed hashing
    pub fn xxhash64(data: &[u8], seed: u64) -> u64 {
        const PRIME1: u64 = 11400714785074694791;
        const PRIME2: u64 = 14029467366897019727;
        const PRIME3: u64 = 1609587929392839161;
        const PRIME4: u64 = 9650029242287828579;
        const PRIME5: u64 = 2870177450012600261;

        let mut h64 = seed.wrapping_add(PRIME5);
        
        if data.len() >= 32 {
            let mut v1 = seed.wrapping_add(PRIME1).wrapping_add(PRIME2);
            let mut v2 = seed.wrapping_add(PRIME2);
            let mut v3 = seed;
            let mut v4 = seed.wrapping_sub(PRIME1);

            let chunks = data.chunks_exact(32);
            let remainder = chunks.remainder();

            for chunk in chunks {
                v1 = round(v1, read_u64(&chunk[0..8]));
                v2 = round(v2, read_u64(&chunk[8..16]));
                v3 = round(v3, read_u64(&chunk[16..24]));
                v4 = round(v4, read_u64(&chunk[24..32]));
            }

            h64 = rotate_left(v1, 1)
                .wrapping_add(rotate_left(v2, 7))
                .wrapping_add(rotate_left(v3, 12))
                .wrapping_add(rotate_left(v4, 18));

            h64 = merge_round(h64, v1);
            h64 = merge_round(h64, v2);
            h64 = merge_round(h64, v3);
            h64 = merge_round(h64, v4);

            h64 = h64.wrapping_add(data.len() as u64);

            // Process remainder
            let mut offset = data.len() - remainder.len();
            while offset + 8 <= data.len() {
                let k1 = round(0, read_u64(&data[offset..offset + 8]));
                h64 ^= k1;
                h64 = rotate_left(h64, 27).wrapping_mul(PRIME1).wrapping_add(PRIME4);
                offset += 8;
            }

            if offset + 4 <= data.len() {
                h64 ^= (read_u32(&data[offset..offset + 4]) as u64).wrapping_mul(PRIME1);
                h64 = rotate_left(h64, 23).wrapping_mul(PRIME2).wrapping_add(PRIME3);
                offset += 4;
            }

            while offset < data.len() {
                h64 ^= (data[offset] as u64).wrapping_mul(PRIME5);
                h64 = rotate_left(h64, 11).wrapping_mul(PRIME1);
                offset += 1;
            }
        } else {
            h64 = h64.wrapping_add(data.len() as u64);
            
            let mut offset = 0;
            while offset + 8 <= data.len() {
                let k1 = round(0, read_u64(&data[offset..offset + 8]));
                h64 ^= k1;
                h64 = rotate_left(h64, 27).wrapping_mul(PRIME1).wrapping_add(PRIME4);
                offset += 8;
            }

            if offset + 4 <= data.len() {
                h64 ^= (read_u32(&data[offset..offset + 4]) as u64).wrapping_mul(PRIME1);
                h64 = rotate_left(h64, 23).wrapping_mul(PRIME2).wrapping_add(PRIME3);
                offset += 4;
            }

            while offset < data.len() {
                h64 ^= (data[offset] as u64).wrapping_mul(PRIME5);
                h64 = rotate_left(h64, 11).wrapping_mul(PRIME1);
                offset += 1;
            }
        }

        // Final mix
        h64 ^= h64 >> 33;
        h64 = h64.wrapping_mul(PRIME2);
        h64 ^= h64 >> 29;
        h64 = h64.wrapping_mul(PRIME3);
        h64 ^= h64 >> 32;

        h64
    }

    #[inline]
    fn round(acc: u64, input: u64) -> u64 {
        const PRIME1: u64 = 11400714785074694791;
        const PRIME2: u64 = 14029467366897019727;
        
        acc.wrapping_add(input.wrapping_mul(PRIME2))
            .rotate_left(31)
            .wrapping_mul(PRIME1)
    }

    #[inline]
    fn merge_round(acc: u64, val: u64) -> u64 {
        const PRIME1: u64 = 11400714785074694791;
        const PRIME4: u64 = 9650029242287828579;
        
        let val = round(0, val);
        (acc ^ val).wrapping_mul(PRIME1).wrapping_add(PRIME4)
    }

    #[inline]
    fn rotate_left(x: u64, r: u32) -> u64 {
        (x << r) | (x >> (64 - r))
    }

    #[inline]
    fn read_u64(bytes: &[u8]) -> u64 {
        u64::from_le_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3],
            bytes[4], bytes[5], bytes[6], bytes[7],
        ])
    }

    #[inline]
    fn read_u32(bytes: &[u8]) -> u32 {
        u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
    }

    /// Simple hash for Python interop
    pub fn simple_hash<T: Hash>(t: &T) -> u64 {
        let mut hasher = DefaultHasher::new();
        t.hash(&mut hasher);
        hasher.finish()
    }
}

/// Python-exposed functions
#[pyfunction]
pub fn generate_random_bytes(py: Python, length: usize) -> PyResult<&PyBytes> {
    let engine = CryptoEngine::new();
    let bytes = engine.random_bytes(length);
    Ok(PyBytes::new(py, &bytes))
}

#[pyfunction]
pub fn generate_grease_values(count: usize) -> Vec<u16> {
    let engine = CryptoEngine::new();
    (0..count).map(|_| engine.generate_grease_value()).collect()
}

#[pyfunction]
pub fn shuffle_list(mut items: Vec<u16>) -> Vec<u16> {
    let engine = CryptoEngine::new();
    engine.shuffle(&mut items);
    items
}

#[pyfunction]
pub fn fast_hash(data: &[u8]) -> u64 {
    hash::xxhash64(data, 0)
}

/// Timing-safe comparison
pub fn constant_time_compare(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }

    let mut result = 0u8;
    for (x, y) in a.iter().zip(b.iter()) {
        result |= x ^ y;
    }

    result == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_grease_generation() {
        let engine = CryptoEngine::new();
        let grease = engine.generate_grease_value();
        assert_eq!(grease & 0x0f0f, 0x0a0a);
    }

    #[test]
    fn test_xxhash() {
        let data = b"Hello, World!";
        let hash1 = hash::xxhash64(data, 0);
        let hash2 = hash::xxhash64(data, 0);
        assert_eq!(hash1, hash2);

        let hash3 = hash::xxhash64(data, 1);
        assert_ne!(hash1, hash3);
    }

    #[test]
    fn test_constant_time_compare() {
        assert!(constant_time_compare(b"test", b"test"));
        assert!(!constant_time_compare(b"test", b"fail"));
        assert!(!constant_time_compare(b"test", b"test2"));
    }
}