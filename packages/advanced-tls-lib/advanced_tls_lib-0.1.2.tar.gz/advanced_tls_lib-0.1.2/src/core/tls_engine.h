#pragma once

#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <openssl/ssl.h>
#include <openssl/bio.h>
#include <openssl/err.h>

namespace advanced_tls {

enum class BrowserProfile {
    CHROME_LATEST,
    CHROME_120,
    CHROME_110,
    FIREFOX_LATEST,
    FIREFOX_115,
    SAFARI_17,
    SAFARI_16,
    EDGE_LATEST,
    CHROME_MOBILE,
    SAFARI_IOS,
    CUSTOM
};

enum class EvasionLevel {
    BASIC,
    ADVANCED,
    MAXIMUM
};

struct TLSFingerprint {
    std::vector<uint16_t> cipher_suites;
    std::vector<uint16_t> extensions;
    std::vector<uint8_t> compression_methods;
    std::vector<std::string> supported_groups;
    std::vector<std::string> signature_algorithms;
    bool enable_grease = true;
    std::string ja3_string;
    std::string ja4_string;
};

struct ConnectionOptions {
    std::string proxy_url;
    int timeout_ms = 30000;
    bool verify_ssl = true;
    std::string custom_ca_path;
    int max_redirects = 10;
    bool enable_http2 = true;
    bool enable_http3 = false;
};

class TLSEngine {
public:
    TLSEngine();
    ~TLSEngine();

    // Disable copy constructor and assignment
    TLSEngine(const TLSEngine&) = delete;
    TLSEngine& operator=(const TLSEngine&) = delete;

    // Initialize with browser profile
    bool initialize(BrowserProfile profile, EvasionLevel evasion_level = EvasionLevel::ADVANCED);
    
    // Initialize with custom fingerprint
    bool initialize(const TLSFingerprint& fingerprint);

    // Set connection options
    void set_connection_options(const ConnectionOptions& options);

    // Establish TLS connection
    bool connect(const std::string& hostname, int port);

    // Send HTTP request
    bool send_request(const std::string& method, const std::string& path, 
                     const std::unordered_map<std::string, std::string>& headers,
                     const std::string& body = "");

    // Receive response
    std::string receive_response();

    // Close connection
    void close();

    // Get current fingerprint
    TLSFingerprint get_current_fingerprint() const;

    // Rotate fingerprint dynamically
    void rotate_fingerprint();

    // Get JA3 hash
    std::string get_ja3_hash() const;

    // Get JA4 hash  
    std::string get_ja4_hash() const;

    // Enable ML-powered evasion
    void enable_ml_evasion(bool enable);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

// Utility functions
std::vector<uint16_t> get_chrome_cipher_suites(int version = 120);
std::vector<uint16_t> get_firefox_cipher_suites(int version = 115);
std::vector<uint16_t> get_safari_cipher_suites(int version = 17);

TLSFingerprint generate_browser_fingerprint(BrowserProfile profile);
std::string calculate_ja3_hash(const TLSFingerprint& fingerprint);
std::string calculate_ja4_hash(const TLSFingerprint& fingerprint);

} // namespace advanced_tls