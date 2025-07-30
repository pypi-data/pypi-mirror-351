#include "browser_profiles.h"
#include "fingerprint_gen.h"
#include <sstream>
#include <random>
#include <chrono>
#include <iomanip>

namespace advanced_tls {

class BrowserProfileManager::Impl {
public:
    std::mt19937 rng{std::chrono::steady_clock::now().time_since_epoch().count()};
    
    // Chrome versions and their characteristics
    struct ChromeVersion {
        int version;
        std::string full_version;
        std::string user_agent_template;
    };
    
    std::vector<ChromeVersion> chrome_versions = {
        {120, "120.0.6099.109", "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"},
        {119, "119.0.6045.159", "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"},
        {118, "118.0.5993.117", "Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"},
    };
    
    std::string get_os_string(const std::string& os) {
        if (!os.empty()) return os;
        
        std::vector<std::string> os_strings = {
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64",
            "Windows NT 11.0; Win64; x64"
        };
        
        std::uniform_int_distribution<size_t> dist(0, os_strings.size() - 1);
        return os_strings[dist(rng)];
    }
    
    BrowserCharacteristics get_chrome_characteristics(int version) {
        BrowserCharacteristics chars;
        
        // Find matching version or use latest
        ChromeVersion chrome_ver = chrome_versions[0];
        for (const auto& v : chrome_versions) {
            if (v.version == version) {
                chrome_ver = v;
                break;
            }
        }
        
        // User agent
        std::string ua_template = chrome_ver.user_agent_template;
        std::string os = get_os_string("");
        std::string version_str = chrome_ver.full_version;
        
        // Replace placeholders
        size_t pos = ua_template.find("{os}");
        if (pos != std::string::npos) {
            ua_template.replace(pos, 4, os);
        }
        pos = ua_template.find("{version}");
        if (pos != std::string::npos) {
            ua_template.replace(pos, 9, version_str);
        }
        
        chars.user_agent = ua_template;
        
        // Accept headers
        chars.accept_headers = {
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        };
        
        // Languages
        chars.accept_languages = {"en-US,en;q=0.9"};
        
        // Encodings
        chars.accept_encodings = {"gzip, deflate, br"};
        
        // Client hints
        chars.sec_ch_ua = "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"" + std::to_string(version) + "\", \"Google Chrome\";v=\"" + std::to_string(version) + "\"";
        chars.sec_ch_ua_mobile = "?0";
        chars.sec_ch_ua_platform = "\"Windows\"";
        
        chars.supports_http2 = true;
        chars.supports_http3 = version >= 100;
        chars.supports_brotli = true;
        
        // Additional Chrome-specific headers
        chars.additional_headers = {
            {"Sec-Fetch-Site", "none"},
            {"Sec-Fetch-Mode", "navigate"},
            {"Sec-Fetch-User", "?1"},
            {"Sec-Fetch-Dest", "document"},
            {"Upgrade-Insecure-Requests", "1"}
        };
        
        return chars;
    }
    
    BrowserCharacteristics get_firefox_characteristics(int version) {
        BrowserCharacteristics chars;
        
        chars.user_agent = "Mozilla/5.0 (" + get_os_string("") + ") Gecko/20100101 Firefox/" + std::to_string(version) + ".0";
        
        chars.accept_headers = {
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        };
        
        chars.accept_languages = {"en-US,en;q=0.5"};
        chars.accept_encodings = {"gzip, deflate, br"};
        
        // Firefox doesn't send Client Hints by default
        chars.sec_ch_ua = "";
        chars.sec_ch_ua_mobile = "";
        chars.sec_ch_ua_platform = "";
        
        chars.supports_http2 = true;
        chars.supports_http3 = version >= 90;
        chars.supports_brotli = true;
        
        chars.additional_headers = {
            {"Upgrade-Insecure-Requests", "1"},
            {"DNT", "1"}
        };
        
        return chars;
    }
    
    BrowserCharacteristics get_safari_characteristics(int version) {
        BrowserCharacteristics chars;
        
        std::string webkit_version = "605.1.15";
        if (version >= 17) webkit_version = "617.1.17";
        else if (version >= 16) webkit_version = "616.1.36";
        
        chars.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/" + 
                          webkit_version + " (KHTML, like Gecko) Version/" + 
                          std::to_string(version) + ".0 Safari/" + webkit_version;
        
        chars.accept_headers = {
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        };
        
        chars.accept_languages = {"en-US,en;q=0.9"};
        chars.accept_encodings = {"gzip, deflate, br"};
        
        // Safari doesn't send Client Hints
        chars.sec_ch_ua = "";
        chars.sec_ch_ua_mobile = "";
        chars.sec_ch_ua_platform = "";
        
        chars.supports_http2 = true;
        chars.supports_http3 = version >= 16;
        chars.supports_brotli = version >= 16;
        
        return chars;
    }
    
    HTTP2Settings get_chrome_http2_settings() {
        HTTP2Settings settings;
        
        settings.header_table_size = 65536;
        settings.enable_push = 1;
        settings.max_concurrent_streams = 1000;
        settings.initial_window_size = 6291456;
        settings.max_frame_size = 16384;
        settings.max_header_list_size = 262144;
        
        // Chrome sends settings in this order
        settings.settings_order = {1, 2, 3, 4, 5, 6};
        
        settings.window_update_increment = 15;
        
        // Chrome pseudo-header order
        settings.pseudo_header_order = {":method", ":authority", ":scheme", ":path"};
        
        return settings;
    }
    
    HTTP2Settings get_firefox_http2_settings() {
        HTTP2Settings settings;
        
        settings.header_table_size = 65536;
        settings.enable_push = 0; // Firefox disables push
        settings.max_concurrent_streams = 100;
        settings.initial_window_size = 131072;
        settings.max_frame_size = 16384;
        settings.max_header_list_size = 393216;
        
        // Firefox sends settings in different order
        settings.settings_order = {1, 3, 4, 5, 6, 2};
        
        settings.window_update_increment = 12;
        
        settings.pseudo_header_order = {":method", ":path", ":authority", ":scheme"};
        
        return settings;
    }
    
    HTTP2Settings get_safari_http2_settings() {
        HTTP2Settings settings;
        
        settings.header_table_size = 4096;
        settings.enable_push = 1;
        settings.max_concurrent_streams = 100;
        settings.initial_window_size = 65535;
        settings.max_frame_size = 16384;
        settings.max_header_list_size = 8192;
        
        settings.settings_order = {1, 3, 4};
        
        settings.window_update_increment = 20;
        
        settings.pseudo_header_order = {":method", ":scheme", ":authority", ":path"};
        
        return settings;
    }
};

BrowserProfileManager::BrowserProfileManager() : pImpl(std::make_unique<Impl>()) {}

BrowserProfileManager::~BrowserProfileManager() = default;

BrowserProfileManager::CompleteProfile BrowserProfileManager::get_profile(BrowserProfile profile) {
    CompleteProfile complete;
    
    // Generate TLS fingerprint
    FingerprintGenerator gen;
    complete.tls_fingerprint = gen.generate(profile);
    
    // Get browser characteristics
    switch (profile) {
        case BrowserProfile::CHROME_LATEST:
        case BrowserProfile::CHROME_120:
            complete.characteristics = pImpl->get_chrome_characteristics(120);
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_chrome_http2_settings());
            break;
            
        case BrowserProfile::FIREFOX_LATEST:
        case BrowserProfile::FIREFOX_115:
            complete.characteristics = pImpl->get_firefox_characteristics(115);
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_firefox_http2_settings());
            break;
            
        case BrowserProfile::SAFARI_17:
        case BrowserProfile::SAFARI_16:
            complete.characteristics = pImpl->get_safari_characteristics(17);
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_safari_http2_settings());
            break;
            
        case BrowserProfile::EDGE_LATEST:
            complete.characteristics = pImpl->get_chrome_characteristics(120);
            complete.characteristics.user_agent.replace(
                complete.characteristics.user_agent.find("Chrome"),
                6, "Edg");
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_chrome_http2_settings());
            break;
            
        case BrowserProfile::CHROME_MOBILE:
            complete.characteristics = pImpl->get_chrome_characteristics(120);
            complete.characteristics.user_agent = 
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36";
            complete.characteristics.sec_ch_ua_mobile = "?1";
            complete.characteristics.sec_ch_ua_platform = "\"Android\"";
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_chrome_http2_settings());
            break;
            
        case BrowserProfile::SAFARI_IOS:
            complete.characteristics = pImpl->get_safari_characteristics(17);
            complete.characteristics.user_agent = 
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";
            complete.http2_fingerprint = generate_http2_fingerprint(pImpl->get_safari_http2_settings());
            break;
            
        default:
            complete = get_profile(BrowserProfile::CHROME_LATEST);
    }
    
    return complete;
}

BrowserProfileManager::CompleteProfile BrowserProfileManager::get_chrome_profile(int version) {
    CompleteProfile profile;
    
    FingerprintGenerator gen;
    profile.tls_fingerprint = gen.generate(BrowserProfile::CHROME_LATEST);
    profile.characteristics = pImpl->get_chrome_characteristics(version);
    profile.http2_fingerprint = generate_http2_fingerprint(pImpl->get_chrome_http2_settings());
    
    return profile;
}

BrowserProfileManager::CompleteProfile BrowserProfileManager::get_firefox_profile(int version) {
    CompleteProfile profile;
    
    FingerprintGenerator gen;
    profile.tls_fingerprint = gen.generate(BrowserProfile::FIREFOX_LATEST);
    profile.characteristics = pImpl->get_firefox_characteristics(version);
    profile.http2_fingerprint = generate_http2_fingerprint(pImpl->get_firefox_http2_settings());
    
    return profile;
}

BrowserProfileManager::CompleteProfile BrowserProfileManager::get_safari_profile(int version) {
    CompleteProfile profile;
    
    FingerprintGenerator gen;
    profile.tls_fingerprint = gen.generate(BrowserProfile::SAFARI_17);
    profile.characteristics = pImpl->get_safari_characteristics(version);
    profile.http2_fingerprint = generate_http2_fingerprint(pImpl->get_safari_http2_settings());
    
    return profile;
}

BrowserProfileManager::CompleteProfile BrowserProfileManager::get_chrome_mobile_profile(const std::string& device) {
    CompleteProfile profile = get_profile(BrowserProfile::CHROME_MOBILE);
    
    // Customize for specific device
    if (device == "pixel") {
        profile.characteristics.user_agent = 
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36";
    } else if (device == "samsung") {
        profile.characteristics.user_agent = 
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36";
    }
    
    return profile;
}

bool BrowserProfileManager::validate_profile(const CompleteProfile& profile) {
    // Validate TLS fingerprint
    FingerprintGenerator gen;
    if (!gen.validate(profile.tls_fingerprint)) {
        return false;
    }
    
    // Validate characteristics
    if (profile.characteristics.user_agent.empty()) {
        return false;
    }
    
    if (profile.characteristics.accept_headers.empty()) {
        return false;
    }
    
    return true;
}

BrowserProfileManager::HTTP2Settings BrowserProfileManager::get_http2_settings(BrowserProfile profile) {
    switch (profile) {
        case BrowserProfile::CHROME_LATEST:
        case BrowserProfile::CHROME_120:
        case BrowserProfile::CHROME_110:
        case BrowserProfile::EDGE_LATEST:
        case BrowserProfile::CHROME_MOBILE:
            return pImpl->get_chrome_http2_settings();
            
        case BrowserProfile::FIREFOX_LATEST:
        case BrowserProfile::FIREFOX_115:
            return pImpl->get_firefox_http2_settings();
            
        case BrowserProfile::SAFARI_17:
        case BrowserProfile::SAFARI_16:
        case BrowserProfile::SAFARI_IOS:
            return pImpl->get_safari_http2_settings();
            
        default:
            return pImpl->get_chrome_http2_settings();
    }
}

std::string BrowserProfileManager::generate_user_agent(BrowserProfile profile, const std::string& os) {
    CompleteProfile complete = get_profile(profile);
    
    if (!os.empty()) {
        // Replace OS portion
        std::string ua = complete.characteristics.user_agent;
        size_t start = ua.find('(');
        size_t end = ua.find(')');
        if (start != std::string::npos && end != std::string::npos) {
            ua.replace(start + 1, end - start - 1, os);
            return ua;
        }
    }
    
    return complete.characteristics.user_agent;
}

BrowserProfileManager::ClientHints BrowserProfileManager::get_client_hints(BrowserProfile profile) {
    ClientHints hints;
    
    switch (profile) {
        case BrowserProfile::CHROME_LATEST:
        case BrowserProfile::CHROME_120:
            hints.sec_ch_ua = "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"";
            hints.sec_ch_ua_mobile = "?0";
            hints.sec_ch_ua_platform = "\"Windows\"";
            hints.sec_ch_ua_platform_version = "\"10.0.0\"";
            hints.sec_ch_ua_arch = "\"x86\"";
            hints.sec_ch_ua_bitness = "\"64\"";
            hints.sec_ch_ua_model = "";
            hints.sec_ch_ua_full_version_list = true;
            break;
            
        case BrowserProfile::CHROME_MOBILE:
            hints.sec_ch_ua = "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"";
            hints.sec_ch_ua_mobile = "?1";
            hints.sec_ch_ua_platform = "\"Android\"";
            hints.sec_ch_ua_platform_version = "\"13.0.0\"";
            hints.sec_ch_ua_model = "\"Pixel 7\"";
            break;
            
        default:
            // Other browsers don't send Client Hints by default
            break;
    }
    
    return hints;
}

// Browser behavior implementation
MousePattern BrowserBehavior::generate_human_mouse_pattern() {
    MousePattern pattern;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> move_dist(50, 20);
    std::normal_distribution<> click_dist(150, 50);
    
    // Generate realistic mouse movements
    for (int i = 0; i < 10; ++i) {
        int x = static_cast<int>(move_dist(gen));
        int y = static_cast<int>(move_dist(gen));
        pattern.movements.push_back({x, y});
        
        int click_interval = std::max(50, static_cast<int>(click_dist(gen)));
        pattern.click_intervals_ms.push_back(click_interval);
    }
    
    pattern.speed_variance = 0.3;
    
    return pattern;
}

TypingPattern BrowserBehavior::generate_human_typing_pattern() {
    TypingPattern pattern;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> typing_dist(150, 40);
    
    pattern.speed_wpm = 40.0 + (gen() % 30);
    pattern.error_rate = 0.02 + (gen() % 3) * 0.01;
    
    // Generate key intervals
    for (int i = 0; i < 50; ++i) {
        int interval = std::max(50, static_cast<int>(typing_dist(gen)));
        pattern.key_intervals_ms.push_back(interval);
    }
    
    return pattern;
}

TimingPattern BrowserBehavior::get_browser_timing_pattern(BrowserProfile profile) {
    TimingPattern pattern;
    
    switch (profile) {
        case BrowserProfile::CHROME_LATEST:
        case BrowserProfile::CHROME_120:
        case BrowserProfile::EDGE_LATEST:
            pattern.min_delay_ms = 10;
            pattern.max_delay_ms = 500;
            pattern.burst_probability = 0.7;
            pattern.burst_size = 6;
            break;
            
        case BrowserProfile::FIREFOX_LATEST:
            pattern.min_delay_ms = 15;
            pattern.max_delay_ms = 600;
            pattern.burst_probability = 0.6;
            pattern.burst_size = 4;
            break;
            
        case BrowserProfile::SAFARI_17:
        case BrowserProfile::SAFARI_IOS:
            pattern.min_delay_ms = 20;
            pattern.max_delay_ms = 700;
            pattern.burst_probability = 0.5;
            pattern.burst_size = 3;
            break;
            
        default:
            pattern.min_delay_ms = 10;
            pattern.max_delay_ms = 500;
            pattern.burst_probability = 0.6;
            pattern.burst_size = 5;
    }
    
    return pattern;
}

// HTTP/2 fingerprint generation
std::string generate_http2_fingerprint(const BrowserProfileManager::HTTP2Settings& settings) {
    std::stringstream fp;
    
    // Format: settings_order|window_update|pseudo_header_order|values
    for (size_t i = 0; i < settings.settings_order.size(); ++i) {
        if (i > 0) fp << ",";
        fp << settings.settings_order[i];
    }
    fp << "|";
    
    fp << static_cast<int>(settings.window_update_increment) << "|";
    
    for (size_t i = 0; i < settings.pseudo_header_order.size(); ++i) {
        if (i > 0) fp << ",";
        fp << settings.pseudo_header_order[i];
    }
    fp << "|";
    
    // Add setting values
    fp << settings.header_table_size << "," 
       << settings.enable_push << ","
       << settings.max_concurrent_streams << ","
       << settings.initial_window_size << ","
       << settings.max_frame_size << ","
       << settings.max_header_list_size;
    
    return fp.str();
}

// QUIC fingerprint generation
std::string generate_quic_fingerprint(const BrowserProfileManager::QUICParameters& params) {
    std::stringstream fp;
    
    fp << "QUIC|"
       << params.max_idle_timeout << ","
       << params.max_udp_payload_size << ","
       << params.initial_max_data << ","
       << params.initial_max_streams_bidi << ","
       << params.initial_max_streams_uni;
    
    return fp.str();
}

} // namespace advanced_tls