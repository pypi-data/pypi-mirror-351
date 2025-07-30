#pragma once

#include "tls_engine.h"
#include "browser_profiles.h"
#include <memory>
#include <vector>
#include <string>
#include <chrono>

namespace advanced_tls {

enum class DetectionSystem {
    CLOUDFLARE,
    AKAMAI,
    IMPERVA,
    DATADOME,
    PERIMETERX,
    SHAPE_SECURITY,
    KASADA,
    GENERIC
};

class EvasionEngine {
public:
    EvasionEngine();
    ~EvasionEngine();

    // Configure evasion for specific detection system
    void configure_for_target(DetectionSystem system);
    
    // Apply evasion techniques to fingerprint
    TLSFingerprint apply_evasion(const TLSFingerprint& original, DetectionSystem target);
    
    // Apply evasion to HTTP headers
    void apply_header_evasion(std::unordered_map<std::string, std::string>& headers, 
                             DetectionSystem target);
    
    // Timing evasion
    struct TimingStrategy {
        int min_request_interval_ms = 100;
        int max_request_interval_ms = 3000;
        bool use_exponential_backoff = false;
        bool simulate_human_timing = true;
        double jitter_factor = 0.2;
    };
    
    TimingStrategy get_timing_strategy(DetectionSystem target);
    
    // Request pattern evasion
    struct RequestPattern {
        bool randomize_request_order = true;
        bool use_referrer_chains = true;
        bool simulate_asset_loading = true;
        int max_concurrent_requests = 6;
        std::vector<std::string> common_paths;
    };
    
    RequestPattern get_request_pattern(DetectionSystem target);
    
    // ML-based adaptive evasion
    class MLEvasion {
    public:
        // Analyze detection response
        struct DetectionSignal {
            int status_code;
            std::string body_pattern;
            std::unordered_map<std::string, std::string> headers;
            std::chrono::milliseconds response_time;
        };
        
        bool is_detected(const DetectionSignal& signal);
        
        // Adapt strategy based on detection
        void adapt_strategy(const DetectionSignal& signal, TLSFingerprint& fp);
        
        // Get success probability for fingerprint
        double get_success_probability(const TLSFingerprint& fp, DetectionSystem target);
        
        // Update model with result
        void update_model(const TLSFingerprint& fp, DetectionSystem target, bool success);
    };
    
    // Anti-fingerprinting techniques
    struct AntiFingerprintingConfig {
        bool randomize_tcp_window_size = true;
        bool vary_tls_record_size = true;
        bool inject_random_delays = true;
        bool use_tcp_timestamps = false;
        bool randomize_alpn_order = true;
    };
    
    AntiFingerprintingConfig get_anti_fingerprinting_config(EvasionLevel level);
    
    // Cipher stunting protection
    void apply_cipher_stunting_protection(TLSFingerprint& fp);
    
    // JA3/JA4 randomization
    void randomize_ja3(TLSFingerprint& fp);
    void randomize_ja4(TLSFingerprint& fp);
    
    // HTTP/2 fingerprint evasion
    void apply_http2_evasion(BrowserProfileManager::HTTP2Settings& settings, 
                            DetectionSystem target);
    
    // Cookie handling for evasion
    struct CookieStrategy {
        bool accept_all_cookies = true;
        bool send_cookie_header = true;
        bool use_cookie_jar = true;
        std::vector<std::string> blacklisted_cookies;
    };
    
    CookieStrategy get_cookie_strategy(DetectionSystem target);
    
    // JavaScript challenge solving
    struct JSChallengeConfig {
        bool solve_basic_math = true;
        bool solve_proof_of_work = true;
        int max_solve_time_ms = 5000;
    };
    
    JSChallengeConfig get_js_challenge_config(DetectionSystem target);
    
    // Get ML evasion instance
    MLEvasion& get_ml_evasion();
    
private:
    DetectionSystem current_target_ = DetectionSystem::GENERIC;
    
    // Configuration flags
    bool enable_ja3_randomization_ = false;
    bool enable_ja4_randomization_ = false;
    bool enable_cipher_stunting_protection_ = false;
    bool enable_http2_fingerprint_randomization_ = false;
    bool enable_extension_shuffling_ = false;
    bool enable_timing_jitter_ = false;
    bool enable_header_order_randomization_ = false;
    bool enable_case_randomization_ = false;
    bool enable_value_obfuscation_ = false;
    bool enable_mouse_movement_simulation_ = false;
    bool enable_canvas_fingerprint_spoofing_ = false;
    bool enable_webgl_fingerprint_spoofing_ = false;
    bool enable_behavioral_simulation_ = false;
    bool enable_sensor_evasion_ = false;
    bool enable_challenge_solving_ = false;
    bool enable_machine_learning_evasion_ = false;
    bool enable_advanced_behavioral_simulation_ = false;
    bool enable_advanced_js_execution_ = false;
    bool enable_anti_debugging_evasion_ = false;
    bool enable_basic_randomization_ = false;
    bool enable_timing_variation_ = false;
    
    // Helper methods
    void configure_cloudflare_evasion();
    void configure_akamai_evasion();
    void configure_imperva_evasion();
    void configure_datadome_evasion();
    void configure_perimeterx_evasion();
    void configure_shape_evasion();
    void configure_kasada_evasion();
    void configure_generic_evasion();
    
    void apply_cloudflare_fingerprint_evasion(TLSFingerprint& fingerprint);
    void apply_akamai_fingerprint_evasion(TLSFingerprint& fingerprint);
    void apply_imperva_fingerprint_evasion(TLSFingerprint& fingerprint);
    void apply_generic_fingerprint_evasion(TLSFingerprint& fingerprint);
    
    void apply_cloudflare_header_evasion(std::unordered_map<std::string, std::string>& headers);
    void apply_akamai_header_evasion(std::unordered_map<std::string, std::string>& headers);
    void apply_imperva_header_evasion(std::unordered_map<std::string, std::string>& headers);
    void apply_generic_header_evasion(std::unordered_map<std::string, std::string>& headers);
    
    void randomize_ja3_components(TLSFingerprint& fingerprint);
    void randomize_ja4_components(TLSFingerprint& fingerprint);
    void shuffle_extensions(TLSFingerprint& fingerprint);
    void protect_against_cipher_stunting(TLSFingerprint& fingerprint);
    void apply_basic_randomization(TLSFingerprint& fingerprint);
    
    std::string generate_cf_ray();
    void randomize_header_case(std::unordered_map<std::string, std::string>& headers);
    void add_timing_headers(std::unordered_map<std::string, std::string>& headers);
    void add_common_browser_headers(std::unordered_map<std::string, std::string>& headers);
    void add_grease_values(TLSFingerprint& fingerprint);
};

// Evasion utilities
namespace evasion_utils {
    
    // Check if response indicates detection
    bool is_blocked_response(int status_code, const std::string& body);
    
    // Generate realistic referrer chain
    std::vector<std::string> generate_referrer_chain(const std::string& target_url);
    
    // Calculate human-like timing delay
    int calculate_human_delay(int action_number, int base_delay_ms);
    
    // Detect fingerprinting JavaScript
    bool contains_fingerprinting_js(const std::string& html);
    
    // Extract challenge from response
    std::string extract_challenge(const std::string& body, DetectionSystem system);
    
    // Generate solution for challenge
    std::string solve_challenge(const std::string& challenge, DetectionSystem system);
    
} // namespace evasion_utils

// Advanced evasion strategies
class AdvancedEvasionStrategy {
public:
    // Traffic pattern obfuscation
    struct TrafficObfuscation {
        bool enabled = true;
        int dummy_request_probability = 10; // percentage
        std::vector<std::string> dummy_endpoints;
        bool use_traffic_shaping = true;
    };
    
    // Behavioral mimicry
    struct BehavioralMimicry {
        bool simulate_mouse_movement = true;
        bool simulate_keyboard_input = true;
        bool simulate_page_scrolling = true;
        bool simulate_tab_switching = true;
        std::chrono::milliseconds avg_page_view_time{15000};
    };
    
    // Network-level evasion
    struct NetworkEvasion {
        bool use_tcp_fast_open = false;
        bool randomize_source_port = true;
        bool use_happy_eyeballs = true;
        int tcp_window_scaling = 7;
    };
    
    TrafficObfuscation get_traffic_obfuscation_config(EvasionLevel level);
    BehavioralMimicry get_behavioral_config(BrowserProfile profile);
    NetworkEvasion get_network_config(EvasionLevel level);
};

} // namespace advanced_tls