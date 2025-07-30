#include "fingerprint_gen.h"
#include <chrono>
#include <algorithm>
#include <unordered_set>
#include <cmath>

namespace advanced_tls {

// Browser market share data (approximate)
static const std::unordered_map<BrowserProfile, double> BROWSER_MARKET_SHARE = {
    {BrowserProfile::CHROME_LATEST, 0.65},
    {BrowserProfile::SAFARI_17, 0.19},
    {BrowserProfile::EDGE_LATEST, 0.05},
    {BrowserProfile::FIREFOX_LATEST, 0.03},
    {BrowserProfile::CHROME_MOBILE, 0.05},
    {BrowserProfile::SAFARI_IOS, 0.03}
};

// Known suspicious patterns
static const std::unordered_set<uint16_t> SUSPICIOUS_CIPHER_COMBINATIONS = {
    0x0001, 0x0002, 0x0004, 0x0005 // Very old cipher suites
};

class FingerprintGenerator::Impl {
public:
    mutable std::mutex mutex;
    std::mt19937 rng{std::chrono::steady_clock::now().time_since_epoch().count()};
    
    // Fingerprint database
    struct FingerprintEntry {
        TLSFingerprint fingerprint;
        double success_rate = 1.0;
        size_t use_count = 0;
        std::chrono::steady_clock::time_point last_used;
    };
    
    std::unordered_map<BrowserProfile, std::vector<FingerprintEntry>> fingerprint_db;
    
    Impl() {
        initialize_database();
    }
    
    void initialize_database() {
        // Pre-generate fingerprints for each browser profile
        for (const auto& [profile, share] : BROWSER_MARKET_SHARE) {
            for (int i = 0; i < 10; ++i) { // 10 variations per profile
                FingerprintEntry entry;
                entry.fingerprint = generate_browser_fingerprint(profile);
                
                // Apply variations
                if (i % 2 == 0) {
                    shuffle_extensions(entry.fingerprint);
                }
                if (i % 3 == 0) {
                    add_random_extensions(entry.fingerprint);
                }
                
                fingerprint_db[profile].push_back(entry);
            }
        }
    }
    
    void shuffle_extensions(TLSFingerprint& fp) {
        // Keep important extensions at the beginning
        if (fp.extensions.size() > 3) {
            std::shuffle(fp.extensions.begin() + 3, fp.extensions.end(), rng);
        }
    }
    
    void add_random_extensions(TLSFingerprint& fp) {
        // Additional extensions that browsers might use
        std::vector<uint16_t> optional_extensions = {
            0x000a, // supported_groups (old)
            0x000b, // ec_point_formats
            0x000d, // signature_algorithms
            0x0015, // padding
            0x0016, // encrypt_then_mac
            0x001b, // compress_certificate
        };
        
        std::uniform_int_distribution<size_t> dist(0, optional_extensions.size() - 1);
        std::uniform_int_distribution<int> count_dist(1, 3);
        
        int add_count = count_dist(rng);
        for (int i = 0; i < add_count; ++i) {
            auto ext = optional_extensions[dist(rng)];
            if (std::find(fp.extensions.begin(), fp.extensions.end(), ext) == fp.extensions.end()) {
                fp.extensions.push_back(ext);
            }
        }
    }
    
    TLSFingerprint select_weighted_profile() {
        std::uniform_real_distribution<double> dist(0.0, 1.0);
        double rand_val = dist(rng);
        double cumulative = 0.0;
        
        for (const auto& [profile, share] : BROWSER_MARKET_SHARE) {
            cumulative += share;
            if (rand_val <= cumulative) {
                return select_from_database(profile);
            }
        }
        
        // Fallback to Chrome
        return select_from_database(BrowserProfile::CHROME_LATEST);
    }
    
    TLSFingerprint select_from_database(BrowserProfile profile) {
        std::lock_guard<std::mutex> lock(mutex);
        
        auto& entries = fingerprint_db[profile];
        if (entries.empty()) {
            // Generate new if none exist
            FingerprintEntry entry;
            entry.fingerprint = generate_browser_fingerprint(profile);
            entries.push_back(entry);
        }
        
        // Select based on success rate and recency
        double best_score = -1.0;
        size_t best_index = 0;
        
        auto now = std::chrono::steady_clock::now();
        
        for (size_t i = 0; i < entries.size(); ++i) {
            auto& entry = entries[i];
            
            // Calculate time decay
            auto time_since_use = std::chrono::duration_cast<std::chrono::hours>(
                now - entry.last_used).count();
            double time_factor = std::exp(-time_since_use / 24.0); // Decay over 24 hours
            
            // Calculate score
            double score = entry.success_rate * time_factor;
            
            if (score > best_score) {
                best_score = score;
                best_index = i;
            }
        }
        
        entries[best_index].use_count++;
        entries[best_index].last_used = now;
        
        return entries[best_index].fingerprint;
    }
    
    TLSFingerprint mutate_fingerprint(const TLSFingerprint& original) {
        TLSFingerprint mutated = original;
        
        std::uniform_int_distribution<int> mutation_type(0, 3);
        
        switch (mutation_type(rng)) {
            case 0: // Shuffle cipher suites (keeping TLS 1.3 ciphers first)
                if (mutated.cipher_suites.size() > 3) {
                    std::shuffle(mutated.cipher_suites.begin() + 3, 
                               mutated.cipher_suites.end(), rng);
                }
                break;
                
            case 1: // Add/remove extensions
                add_random_extensions(mutated);
                break;
                
            case 2: // Change supported groups order
                std::shuffle(mutated.supported_groups.begin(), 
                           mutated.supported_groups.end(), rng);
                break;
                
            case 3: // Toggle GREASE
                mutated.enable_grease = !mutated.enable_grease;
                break;
        }
        
        return mutated;
    }
};

FingerprintGenerator::FingerprintGenerator() : pImpl(std::make_unique<Impl>()) {}

FingerprintGenerator::~FingerprintGenerator() = default;

TLSFingerprint FingerprintGenerator::generate(BrowserProfile profile) {
    return pImpl->select_from_database(profile);
}

TLSFingerprint FingerprintGenerator::generate_adaptive(const std::string& target_domain) {
    // In a real implementation, this would use ML to select optimal fingerprint
    // For now, use weighted selection with domain-specific adjustments
    
    TLSFingerprint fp = pImpl->select_weighted_profile();
    
    // Apply domain-specific optimizations
    if (target_domain.find("cloudflare") != std::string::npos) {
        // Cloudflare-specific optimizations
        fp.enable_grease = true;
        // Ensure modern cipher suites
        if (std::find(fp.cipher_suites.begin(), fp.cipher_suites.end(), 0x1301) == fp.cipher_suites.end()) {
            fp.cipher_suites.insert(fp.cipher_suites.begin(), 0x1301);
        }
    } else if (target_domain.find("akamai") != std::string::npos) {
        // Akamai-specific optimizations
        fp = fingerprint_utils::apply_anti_stunting(fp);
    }
    
    return fp;
}

TLSFingerprint FingerprintGenerator::generate_weighted() {
    return pImpl->select_weighted_profile();
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::with_cipher_suites(
    const std::vector<uint16_t>& suites) {
    fingerprint.cipher_suites = suites;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::with_extensions(
    const std::vector<uint16_t>& exts) {
    fingerprint.extensions = exts;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::with_compression_methods(
    const std::vector<uint8_t>& methods) {
    fingerprint.compression_methods = methods;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::with_supported_groups(
    const std::vector<std::string>& groups) {
    fingerprint.supported_groups = groups;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::with_signature_algorithms(
    const std::vector<std::string>& algos) {
    fingerprint.signature_algorithms = algos;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::enable_grease(bool enable) {
    fingerprint.enable_grease = enable;
    return *this;
}

FingerprintGenerator::Builder& FingerprintGenerator::Builder::randomize_order() {
    // Randomize extensions order (keeping critical ones in place)
    if (fingerprint.extensions.size() > 3) {
        std::shuffle(fingerprint.extensions.begin() + 3, fingerprint.extensions.end(), rng);
    }
    
    // Randomize cipher suites (keeping TLS 1.3 ones first)
    size_t tls13_count = 0;
    for (const auto& cipher : fingerprint.cipher_suites) {
        if (cipher >= 0x1301 && cipher <= 0x1305) {
            tls13_count++;
        }
    }
    if (fingerprint.cipher_suites.size() > tls13_count) {
        std::shuffle(fingerprint.cipher_suites.begin() + tls13_count, 
                    fingerprint.cipher_suites.end(), rng);
    }
    
    return *this;
}

TLSFingerprint FingerprintGenerator::Builder::build() {
    // Set defaults if not specified
    if (fingerprint.compression_methods.empty()) {
        fingerprint.compression_methods = {0x00}; // No compression
    }
    
    // Calculate JA3/JA4
    fingerprint.ja3_string = calculate_ja3_hash(fingerprint);
    fingerprint.ja4_string = calculate_ja4_hash(fingerprint);
    
    return fingerprint;
}

FingerprintGenerator::Builder FingerprintGenerator::builder() {
    return Builder();
}

bool FingerprintGenerator::validate(const TLSFingerprint& fp) const {
    // Basic validation checks
    if (fp.cipher_suites.empty()) return false;
    if (fp.extensions.empty()) return false;
    if (fp.compression_methods.empty()) return false;
    
    // Check for suspicious patterns
    if (fingerprint_utils::is_suspicious(fp)) return false;
    
    // Ensure at least one TLS 1.3 cipher suite
    bool has_tls13 = false;
    for (const auto& cipher : fp.cipher_suites) {
        if (cipher >= 0x1301 && cipher <= 0x1305) {
            has_tls13 = true;
            break;
        }
    }
    
    return has_tls13;
}

TLSFingerprint FingerprintGenerator::mutate(const TLSFingerprint& original) {
    return pImpl->mutate_fingerprint(original);
}

FingerprintGenerator::DatabaseStats FingerprintGenerator::get_stats() const {
    std::lock_guard<std::mutex> lock(pImpl->mutex);
    
    DatabaseStats stats;
    stats.total_fingerprints = 0;
    
    for (const auto& [profile, entries] : pImpl->fingerprint_db) {
        stats.total_fingerprints += entries.size();
        
        // Convert profile to string
        std::string profile_name;
        switch (profile) {
            case BrowserProfile::CHROME_LATEST: profile_name = "Chrome Latest"; break;
            case BrowserProfile::FIREFOX_LATEST: profile_name = "Firefox Latest"; break;
            case BrowserProfile::SAFARI_17: profile_name = "Safari 17"; break;
            case BrowserProfile::EDGE_LATEST: profile_name = "Edge Latest"; break;
            case BrowserProfile::CHROME_MOBILE: profile_name = "Chrome Mobile"; break;
            case BrowserProfile::SAFARI_IOS: profile_name = "Safari iOS"; break;
            default: profile_name = "Unknown"; break;
        }
        
        stats.browser_distribution[profile_name] = entries.size();
        
        // Calculate average success rate
        double avg_success = 0.0;
        for (const auto& entry : entries) {
            avg_success += entry.success_rate;
        }
        if (!entries.empty()) {
            avg_success /= entries.size();
        }
        stats.success_rates[profile_name] = avg_success;
    }
    
    return stats;
}

// Fingerprint utilities implementation
namespace fingerprint_utils {

bool is_suspicious(const TLSFingerprint& fp) {
    // Check for known suspicious patterns
    
    // 1. Old cipher suites mixed with new ones
    bool has_old = false;
    bool has_new = false;
    
    for (const auto& cipher : fp.cipher_suites) {
        if (SUSPICIOUS_CIPHER_COMBINATIONS.count(cipher) > 0) {
            has_old = true;
        }
        if (cipher >= 0x1301 && cipher <= 0x1305) {
            has_new = true;
        }
    }
    
    if (has_old && has_new) return true;
    
    // 2. Unusual extension combinations
    bool has_sni = std::find(fp.extensions.begin(), fp.extensions.end(), 0x0000) != fp.extensions.end();
    if (!has_sni) return true; // All browsers use SNI
    
    // 3. Too many or too few extensions
    if (fp.extensions.size() < 5 || fp.extensions.size() > 20) return true;
    
    return false;
}

TLSFingerprint apply_time_variation(const TLSFingerprint& fp, int hour_of_day) {
    TLSFingerprint varied = fp;
    
    // Apply time-based variations (e.g., mobile traffic increases in evening)
    if (hour_of_day >= 18 || hour_of_day <= 6) {
        // Evening/night - more mobile traffic
        // Remove some desktop-specific extensions
        varied.extensions.erase(
            std::remove(varied.extensions.begin(), varied.extensions.end(), 0x0001),
            varied.extensions.end()
        );
    }
    
    return varied;
}

TLSFingerprint apply_geo_variation(const TLSFingerprint& fp, const std::string& country_code) {
    TLSFingerprint varied = fp;
    
    // Apply geographic variations
    if (country_code == "CN" || country_code == "RU") {
        // Some regions prefer certain cipher suites
        // Prioritize non-ECDSA cipher suites
        std::stable_partition(varied.cipher_suites.begin(), varied.cipher_suites.end(),
            [](uint16_t cipher) {
                return cipher != 0xc02b && cipher != 0xc02c; // ECDSA variants
            });
    }
    
    return varied;
}

TLSFingerprint mix_fingerprints(const TLSFingerprint& fp1, const TLSFingerprint& fp2, double weight) {
    TLSFingerprint mixed;
    
    // Mix cipher suites
    size_t fp1_ciphers = static_cast<size_t>(fp1.cipher_suites.size() * weight);
    size_t fp2_ciphers = static_cast<size_t>(fp2.cipher_suites.size() * (1.0 - weight));
    
    mixed.cipher_suites.insert(mixed.cipher_suites.end(),
        fp1.cipher_suites.begin(), fp1.cipher_suites.begin() + fp1_ciphers);
    mixed.cipher_suites.insert(mixed.cipher_suites.end(),
        fp2.cipher_suites.begin(), fp2.cipher_suites.begin() + fp2_ciphers);
    
    // Remove duplicates
    std::sort(mixed.cipher_suites.begin(), mixed.cipher_suites.end());
    mixed.cipher_suites.erase(
        std::unique(mixed.cipher_suites.begin(), mixed.cipher_suites.end()),
        mixed.cipher_suites.end()
    );
    
    // Mix extensions similarly
    mixed.extensions = fp1.extensions;
    for (const auto& ext : fp2.extensions) {
        if (std::find(mixed.extensions.begin(), mixed.extensions.end(), ext) == mixed.extensions.end()) {
            mixed.extensions.push_back(ext);
        }
    }
    
    // Use fp1's other properties
    mixed.compression_methods = fp1.compression_methods;
    mixed.supported_groups = fp1.supported_groups;
    mixed.signature_algorithms = fp1.signature_algorithms;
    mixed.enable_grease = fp1.enable_grease || fp2.enable_grease;
    
    return mixed;
}

TLSFingerprint to_mobile_variant(const TLSFingerprint& desktop_fp) {
    TLSFingerprint mobile = desktop_fp;
    
    // Remove desktop-specific extensions
    mobile.extensions.erase(
        std::remove_if(mobile.extensions.begin(), mobile.extensions.end(),
            [](uint16_t ext) {
                return ext == 0x0001 || ext == 0x0015; // max_fragment_length, padding
            }),
        mobile.extensions.end()
    );
    
    // Reduce supported groups
    if (mobile.supported_groups.size() > 2) {
        mobile.supported_groups.resize(2);
    }
    
    // Reduce cipher suites slightly
    if (mobile.cipher_suites.size() > 12) {
        mobile.cipher_suites.resize(12);
    }
    
    return mobile;
}

TLSFingerprint apply_anti_stunting(const TLSFingerprint& fp) {
    TLSFingerprint protected_fp = fp;
    
    // Ensure cipher suite order is not too predictable
    // Add slight randomization while keeping important ciphers first
    if (protected_fp.cipher_suites.size() > 5) {
        // Shuffle middle section
        std::random_device rd;
        std::mt19937 g(rd());
        std::shuffle(protected_fp.cipher_suites.begin() + 3,
                    protected_fp.cipher_suites.end() - 2, g);
    }
    
    // Ensure GREASE values are properly distributed
    if (protected_fp.enable_grease) {
        // GREASE values should not be at predictable positions
        std::random_device rd;
        std::uniform_int_distribution<size_t> dist(1, protected_fp.extensions.size() - 1);
        
        // Remove any existing GREASE values
        protected_fp.extensions.erase(
            std::remove_if(protected_fp.extensions.begin(), protected_fp.extensions.end(),
                [](uint16_t ext) {
                    return (ext & 0x0f0f) == 0x0a0a;
                }),
            protected_fp.extensions.end()
        );
    }
    
    return protected_fp;
}

} // namespace fingerprint_utils

} // namespace advanced_tls