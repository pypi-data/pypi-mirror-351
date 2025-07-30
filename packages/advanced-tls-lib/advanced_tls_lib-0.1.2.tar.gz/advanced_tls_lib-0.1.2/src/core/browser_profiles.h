#pragma once

#include "tls_engine.h"
#include <string>
#include <vector>
#include <memory>

namespace advanced_tls {

struct BrowserCharacteristics {
    std::string user_agent;
    std::vector<std::string> accept_headers;
    std::vector<std::string> accept_languages;
    std::vector<std::string> accept_encodings;
    std::string sec_ch_ua;
    std::string sec_ch_ua_mobile;
    std::string sec_ch_ua_platform;
    bool supports_http2 = true;
    bool supports_http3 = false;
    bool supports_brotli = true;
    std::vector<std::pair<std::string, std::string>> additional_headers;
};

class BrowserProfileManager {
public:
    BrowserProfileManager();
    ~BrowserProfileManager();

    // Get complete browser profile
    struct CompleteProfile {
        TLSFingerprint tls_fingerprint;
        BrowserCharacteristics characteristics;
        std::string http2_fingerprint;
    };
    
    CompleteProfile get_profile(BrowserProfile profile);
    
    // Get specific browser version profiles
    CompleteProfile get_chrome_profile(int version);
    CompleteProfile get_firefox_profile(int version);
    CompleteProfile get_safari_profile(int version);
    CompleteProfile get_edge_profile(int version);
    
    // Get mobile browser profiles
    CompleteProfile get_chrome_mobile_profile(const std::string& device);
    CompleteProfile get_safari_ios_profile(const std::string& device);
    CompleteProfile get_samsung_browser_profile();
    
    // Custom profile creation
    CompleteProfile create_custom_profile(
        const TLSFingerprint& tls_fp,
        const BrowserCharacteristics& chars
    );
    
    // Profile validation
    bool validate_profile(const CompleteProfile& profile);
    
    // Get HTTP/2 fingerprint settings
    struct HTTP2Settings {
        uint32_t header_table_size = 65536;
        uint32_t enable_push = 1;
        uint32_t max_concurrent_streams = 1000;
        uint32_t initial_window_size = 6291456;
        uint32_t max_frame_size = 16384;
        uint32_t max_header_list_size = 262144;
        std::vector<uint16_t> settings_order;
        uint8_t window_update_increment = 15; // As percentage
        std::vector<std::string> pseudo_header_order;
    };
    
    HTTP2Settings get_http2_settings(BrowserProfile profile);
    
    // Get HTTP/3 QUIC parameters
    struct QUICParameters {
        uint32_t max_idle_timeout = 30000;
        uint32_t max_udp_payload_size = 1200;
        uint32_t initial_max_data = 10485760;
        uint32_t initial_max_stream_data_bidi_local = 6291456;
        uint32_t initial_max_stream_data_bidi_remote = 6291456;
        uint32_t initial_max_stream_data_uni = 6291456;
        uint32_t initial_max_streams_bidi = 100;
        uint32_t initial_max_streams_uni = 100;
        bool disable_active_migration = false;
    };
    
    QUICParameters get_quic_parameters(BrowserProfile profile);
    
    // User agent generation
    std::string generate_user_agent(BrowserProfile profile, const std::string& os = "");
    
    // Accept header generation
    std::vector<std::string> generate_accept_headers(BrowserProfile profile);
    
    // Get SEC-CH-UA headers for Client Hints
    struct ClientHints {
        std::string sec_ch_ua;
        std::string sec_ch_ua_mobile;
        std::string sec_ch_ua_platform;
        std::string sec_ch_ua_platform_version;
        std::string sec_ch_ua_arch;
        std::string sec_ch_ua_bitness;
        std::string sec_ch_ua_model;
        bool sec_ch_ua_full_version_list = false;
    };
    
    ClientHints get_client_hints(BrowserProfile profile);
    
private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

// Forward declarations for browser behavior types
struct MousePattern {
    std::vector<std::pair<int, int>> movements;
    std::vector<int> click_intervals_ms;
    double speed_variance;
};

struct TypingPattern {
    std::vector<int> key_intervals_ms;
    double speed_wpm;
    double error_rate;
};

struct TimingPattern {
    int page_load_min_ms;
    int page_load_max_ms;
    int inter_request_min_ms;
    int inter_request_max_ms;
    double human_factor;
    int min_delay_ms;
    int max_delay_ms;
    double burst_probability;
    int burst_size;
};

// Page load behavior
struct PageLoadBehavior {
    bool load_images = true;
    bool load_stylesheets = true;
    bool load_scripts = true;
    bool load_fonts = true;
    bool execute_javascript = false;
    std::vector<std::string> resource_priorities;
};

// Browser behavior emulation
class BrowserBehavior {
public:
    static MousePattern generate_human_mouse_pattern();
    static TypingPattern generate_human_typing_pattern();
    static TimingPattern get_browser_timing_pattern(BrowserProfile profile);
    static PageLoadBehavior get_page_load_behavior(BrowserProfile profile);
};

// HTTP/2 fingerprint generation
std::string generate_http2_fingerprint(const BrowserProfileManager::HTTP2Settings& settings);

// QUIC fingerprint generation  
std::string generate_quic_fingerprint(const BrowserProfileManager::QUICParameters& params);

// Browser behavior patterns - removed duplicate definitions

} // namespace advanced_tls