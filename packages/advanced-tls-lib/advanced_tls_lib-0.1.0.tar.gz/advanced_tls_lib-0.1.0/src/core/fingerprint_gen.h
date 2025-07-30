#pragma once

#include "tls_engine.h"
#include <memory>
#include <mutex>
#include <random>

namespace advanced_tls {

class FingerprintGenerator {
public:
    FingerprintGenerator();
    ~FingerprintGenerator();

    // Generate fingerprint for specific browser
    TLSFingerprint generate(BrowserProfile profile);
    
    // Generate fingerprint with ML-based selection
    TLSFingerprint generate_adaptive(const std::string& target_domain);
    
    // Generate fingerprint based on market share
    TLSFingerprint generate_weighted();
    
    // Custom fingerprint builder
    class Builder {
    public:
        Builder& with_cipher_suites(const std::vector<uint16_t>& suites);
        Builder& with_extensions(const std::vector<uint16_t>& exts);
        Builder& with_compression_methods(const std::vector<uint8_t>& methods);
        Builder& with_supported_groups(const std::vector<std::string>& groups);
        Builder& with_signature_algorithms(const std::vector<std::string>& algos);
        Builder& enable_grease(bool enable = true);
        Builder& randomize_order();
        TLSFingerprint build();
        
    private:
        TLSFingerprint fingerprint;
        std::mt19937 rng{std::random_device{}()};
    };
    
    // Get builder instance
    static Builder builder();
    
    // Fingerprint validation
    bool validate(const TLSFingerprint& fp) const;
    
    // Fingerprint mutation (for evasion)
    TLSFingerprint mutate(const TLSFingerprint& original);
    
    // Get fingerprint database stats
    struct DatabaseStats {
        size_t total_fingerprints;
        std::unordered_map<std::string, size_t> browser_distribution;
        std::unordered_map<std::string, double> success_rates;
    };
    
    DatabaseStats get_stats() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

// Fingerprint utilities
namespace fingerprint_utils {
    
    // Check if fingerprint matches known detection patterns
    bool is_suspicious(const TLSFingerprint& fp);
    
    // Generate time-based variations
    TLSFingerprint apply_time_variation(const TLSFingerprint& fp, int hour_of_day);
    
    // Apply geographic variations
    TLSFingerprint apply_geo_variation(const TLSFingerprint& fp, const std::string& country_code);
    
    // Mix two fingerprints for hybrid approach
    TLSFingerprint mix_fingerprints(const TLSFingerprint& fp1, const TLSFingerprint& fp2, double weight = 0.5);
    
    // Generate mobile variant
    TLSFingerprint to_mobile_variant(const TLSFingerprint& desktop_fp);
    
    // Anti-cipher stunting protection
    TLSFingerprint apply_anti_stunting(const TLSFingerprint& fp);
    
} // namespace fingerprint_utils

} // namespace advanced_tls