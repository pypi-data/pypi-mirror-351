#include "tls_engine.h"
#include <openssl/crypto.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <sstream>
#include <iomanip>
#include <chrono>
#include <algorithm>
#include <random>

namespace advanced_tls {

// Chrome cipher suites in order
static const std::vector<uint16_t> CHROME_120_CIPHERS = {
    0x1301, // TLS_AES_128_GCM_SHA256
    0x1302, // TLS_AES_256_GCM_SHA384
    0x1303, // TLS_CHACHA20_POLY1305_SHA256
    0xc02b, // TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
    0xc02f, // TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    0xc02c, // TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
    0xc030, // TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    0xcca9, // TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
    0xcca8, // TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
    0xc013, // TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
    0xc014, // TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
    0x009c, // TLS_RSA_WITH_AES_128_GCM_SHA256
    0x009d, // TLS_RSA_WITH_AES_256_GCM_SHA384
    0x002f, // TLS_RSA_WITH_AES_128_CBC_SHA
    0x0035  // TLS_RSA_WITH_AES_256_CBC_SHA
};

// Firefox cipher suites  
static const std::vector<uint16_t> FIREFOX_115_CIPHERS = {
    0x1301, // TLS_AES_128_GCM_SHA256
    0x1303, // TLS_CHACHA20_POLY1305_SHA256
    0x1302, // TLS_AES_256_GCM_SHA384
    0xcca9, // TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
    0xcca8, // TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
    0xc02b, // TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
    0xc02f, // TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
    0xc02c, // TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
    0xc030, // TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    0xc009, // TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA
    0xc013, // TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
    0xc00a, // TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA
    0xc014  // TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
};

// GREASE values for extensions
static const std::vector<uint16_t> GREASE_VALUES = {
    0x0a0a, 0x1a1a, 0x2a2a, 0x3a3a,
    0x4a4a, 0x5a5a, 0x6a6a, 0x7a7a,
    0x8a8a, 0x9a9a, 0xaaaa, 0xbaba,
    0xcaca, 0xdada, 0xeaea, 0xfafa
};

class TLSEngine::Impl {
public:
    SSL_CTX* ctx = nullptr;
    SSL* ssl = nullptr;
    BIO* bio = nullptr;
    
    BrowserProfile current_profile;
    TLSFingerprint current_fingerprint;
    ConnectionOptions conn_options;
    EvasionLevel evasion_level;
    bool ml_evasion_enabled = false;
    
    std::mt19937 rng{std::chrono::steady_clock::now().time_since_epoch().count()};

    Impl() {
        SSL_library_init();
        SSL_load_error_strings();
        OpenSSL_add_all_algorithms();
    }

    ~Impl() {
        cleanup();
    }

    void cleanup() {
        if (ssl) {
            SSL_shutdown(ssl);
            SSL_free(ssl);
            ssl = nullptr;
        }
        if (ctx) {
            SSL_CTX_free(ctx);
            ctx = nullptr;
        }
        if (bio) {
            BIO_free_all(bio);
            bio = nullptr;
        }
    }

    bool setup_context(const TLSFingerprint& fingerprint) {
        ctx = SSL_CTX_new(TLS_client_method());
        if (!ctx) {
            return false;
        }

        // Set minimum and maximum TLS versions
        SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);
        SSL_CTX_set_max_proto_version(ctx, TLS1_3_VERSION);

        // Configure cipher suites
        if (!configure_ciphers(fingerprint.cipher_suites)) {
            return false;
        }

        // Configure extensions
        if (!configure_extensions(fingerprint)) {
            return false;
        }

        // Set options for evasion
        configure_evasion_options();

        return true;
    }

    bool configure_ciphers(const std::vector<uint16_t>& cipher_suites) {
        std::stringstream cipher_string;
        
        // Convert cipher suite IDs to OpenSSL format
        for (size_t i = 0; i < cipher_suites.size(); ++i) {
            if (i > 0) cipher_string << ":";
            
            // Map cipher suite IDs to OpenSSL names
            switch (cipher_suites[i]) {
                case 0x1301: cipher_string << "TLS_AES_128_GCM_SHA256"; break;
                case 0x1302: cipher_string << "TLS_AES_256_GCM_SHA384"; break;
                case 0x1303: cipher_string << "TLS_CHACHA20_POLY1305_SHA256"; break;
                case 0xc02b: cipher_string << "ECDHE-ECDSA-AES128-GCM-SHA256"; break;
                case 0xc02f: cipher_string << "ECDHE-RSA-AES128-GCM-SHA256"; break;
                case 0xc02c: cipher_string << "ECDHE-ECDSA-AES256-GCM-SHA384"; break;
                case 0xc030: cipher_string << "ECDHE-RSA-AES256-GCM-SHA384"; break;
                case 0xcca9: cipher_string << "ECDHE-ECDSA-CHACHA20-POLY1305"; break;
                case 0xcca8: cipher_string << "ECDHE-RSA-CHACHA20-POLY1305"; break;
                case 0xc013: cipher_string << "ECDHE-RSA-AES128-SHA"; break;
                case 0xc014: cipher_string << "ECDHE-RSA-AES256-SHA"; break;
                case 0x009c: cipher_string << "AES128-GCM-SHA256"; break;
                case 0x009d: cipher_string << "AES256-GCM-SHA384"; break;
                case 0x002f: cipher_string << "AES128-SHA"; break;
                case 0x0035: cipher_string << "AES256-SHA"; break;
                default: continue;
            }
        }

        return SSL_CTX_set_cipher_list(ctx, cipher_string.str().c_str()) == 1;
    }

    bool configure_extensions(const TLSFingerprint& fingerprint) {
        // Configure supported groups (curves)
        if (!fingerprint.supported_groups.empty()) {
            // Implementation would require custom OpenSSL configuration
        }

        // Configure signature algorithms
        if (!fingerprint.signature_algorithms.empty()) {
            // Implementation would require custom OpenSSL configuration
        }

        return true;
    }

    void configure_evasion_options() {
        long options = SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | SSL_OP_NO_COMPRESSION;
        
        if (evasion_level >= EvasionLevel::ADVANCED) {
            // Mimic browser behavior more closely
            options |= SSL_OP_NO_TICKET;
            options |= SSL_OP_SAFARI_ECDHE_ECDSA_BUG;
        }

        SSL_CTX_set_options(ctx, options);
    }

    uint16_t get_random_grease_value() {
        std::uniform_int_distribution<size_t> dist(0, GREASE_VALUES.size() - 1);
        return GREASE_VALUES[dist(rng)];
    }

    void inject_grease_values(TLSFingerprint& fingerprint) {
        if (!fingerprint.enable_grease) return;

        // Insert GREASE values at random positions
        std::uniform_int_distribution<size_t> pos_dist(0, fingerprint.cipher_suites.size());
        
        // Add GREASE cipher suite
        auto grease_cipher = get_random_grease_value();
        auto pos = pos_dist(rng);
        fingerprint.cipher_suites.insert(fingerprint.cipher_suites.begin() + pos, grease_cipher);

        // Add GREASE extension
        auto grease_ext = get_random_grease_value();
        pos = std::uniform_int_distribution<size_t>(0, fingerprint.extensions.size())(rng);
        fingerprint.extensions.insert(fingerprint.extensions.begin() + pos, grease_ext);
    }
};

TLSEngine::TLSEngine() : pImpl(std::make_unique<Impl>()) {}

TLSEngine::~TLSEngine() = default;

bool TLSEngine::initialize(BrowserProfile profile, EvasionLevel evasion_level) {
    pImpl->current_profile = profile;
    pImpl->evasion_level = evasion_level;
    pImpl->current_fingerprint = generate_browser_fingerprint(profile);
    
    if (evasion_level >= EvasionLevel::ADVANCED) {
        pImpl->inject_grease_values(pImpl->current_fingerprint);
    }
    
    return pImpl->setup_context(pImpl->current_fingerprint);
}

bool TLSEngine::initialize(const TLSFingerprint& fingerprint) {
    pImpl->current_fingerprint = fingerprint;
    return pImpl->setup_context(fingerprint);
}

void TLSEngine::set_connection_options(const ConnectionOptions& options) {
    pImpl->conn_options = options;
}

bool TLSEngine::connect(const std::string& hostname, int port) {
    pImpl->cleanup();
    
    if (!pImpl->ctx && !initialize(pImpl->current_profile, pImpl->evasion_level)) {
        return false;
    }

    // Create BIO chain
    pImpl->bio = BIO_new_ssl_connect(pImpl->ctx);
    if (!pImpl->bio) {
        return false;
    }

    // Get SSL pointer
    BIO_get_ssl(pImpl->bio, &pImpl->ssl);
    if (!pImpl->ssl) {
        return false;
    }

    // Set SNI
    SSL_set_tlsext_host_name(pImpl->ssl, hostname.c_str());

    // Set connection string
    std::string conn_str = hostname + ":" + std::to_string(port);
    BIO_set_conn_hostname(pImpl->bio, conn_str.c_str());

    // Set non-blocking mode for timeout support
    BIO_set_nbio(pImpl->bio, 1);

    // Attempt connection
    if (BIO_do_connect(pImpl->bio) <= 0) {
        if (!BIO_should_retry(pImpl->bio)) {
            return false;
        }
        // Would need to implement timeout logic here
    }

    // Perform handshake
    if (BIO_do_handshake(pImpl->bio) <= 0) {
        return false;
    }

    return true;
}

bool TLSEngine::send_request(const std::string& method, const std::string& path,
                            const std::unordered_map<std::string, std::string>& headers,
                            const std::string& body) {
    if (!pImpl->bio || !pImpl->ssl) {
        return false;
    }

    std::stringstream request;
    request << method << " " << path << " HTTP/1.1\r\n";
    
    for (const auto& [key, value] : headers) {
        request << key << ": " << value << "\r\n";
    }
    
    if (!body.empty()) {
        request << "Content-Length: " << body.length() << "\r\n";
    }
    
    request << "\r\n";
    
    if (!body.empty()) {
        request << body;
    }

    std::string request_str = request.str();
    int written = BIO_write(pImpl->bio, request_str.c_str(), request_str.length());
    
    return written == static_cast<int>(request_str.length());
}

std::string TLSEngine::receive_response() {
    if (!pImpl->bio || !pImpl->ssl) {
        return "";
    }

    std::string response;
    char buffer[4096];
    
    while (true) {
        int read = BIO_read(pImpl->bio, buffer, sizeof(buffer) - 1);
        if (read <= 0) {
            if (BIO_should_retry(pImpl->bio)) {
                continue;
            }
            break;
        }
        buffer[read] = '\0';
        response += buffer;
    }
    
    return response;
}

void TLSEngine::close() {
    pImpl->cleanup();
}

TLSFingerprint TLSEngine::get_current_fingerprint() const {
    return pImpl->current_fingerprint;
}

void TLSEngine::rotate_fingerprint() {
    // Rotate to a different browser profile
    std::vector<BrowserProfile> profiles = {
        BrowserProfile::CHROME_LATEST,
        BrowserProfile::FIREFOX_LATEST,
        BrowserProfile::SAFARI_17,
        BrowserProfile::EDGE_LATEST
    };
    
    std::uniform_int_distribution<size_t> dist(0, profiles.size() - 1);
    BrowserProfile new_profile = profiles[dist(pImpl->rng)];
    
    while (new_profile == pImpl->current_profile) {
        new_profile = profiles[dist(pImpl->rng)];
    }
    
    initialize(new_profile, pImpl->evasion_level);
}

std::string TLSEngine::get_ja3_hash() const {
    return calculate_ja3_hash(pImpl->current_fingerprint);
}

std::string TLSEngine::get_ja4_hash() const {
    return calculate_ja4_hash(pImpl->current_fingerprint);
}

void TLSEngine::enable_ml_evasion(bool enable) {
    pImpl->ml_evasion_enabled = enable;
}

// Utility functions implementation
std::vector<uint16_t> get_chrome_cipher_suites(int version) {
    if (version >= 120) {
        return CHROME_120_CIPHERS;
    }
    // Return default Chrome ciphers
    return CHROME_120_CIPHERS;
}

std::vector<uint16_t> get_firefox_cipher_suites(int version) {
    if (version >= 115) {
        return FIREFOX_115_CIPHERS;
    }
    return FIREFOX_115_CIPHERS;
}

std::vector<uint16_t> get_safari_cipher_suites(int version) {
    // Safari cipher suites similar to Chrome but with different ordering
    std::vector<uint16_t> safari_ciphers = CHROME_120_CIPHERS;
    std::shuffle(safari_ciphers.begin() + 3, safari_ciphers.end(), 
                 std::mt19937(std::random_device{}()));
    return safari_ciphers;
}

TLSFingerprint generate_browser_fingerprint(BrowserProfile profile) {
    TLSFingerprint fingerprint;
    
    switch (profile) {
        case BrowserProfile::CHROME_LATEST:
        case BrowserProfile::CHROME_120:
            fingerprint.cipher_suites = get_chrome_cipher_suites(120);
            fingerprint.extensions = {
                0x0000, // server_name
                0x0017, // extended_master_secret
                0x0001, // max_fragment_length
                0x0005, // status_request
                0x0012, // signed_certificate_timestamp
                0x0023, // session_ticket
                0x002b, // supported_versions
                0x002d, // psk_key_exchange_modes
                0x0033  // key_share
            };
            fingerprint.compression_methods = {0x00}; // No compression
            fingerprint.supported_groups = {"x25519", "secp256r1", "secp384r1"};
            fingerprint.signature_algorithms = {
                "ecdsa_secp256r1_sha256",
                "rsa_pss_rsae_sha256",
                "rsa_pkcs1_sha256",
                "ecdsa_secp384r1_sha384",
                "rsa_pss_rsae_sha384",
                "rsa_pkcs1_sha384",
                "rsa_pss_rsae_sha512",
                "rsa_pkcs1_sha512"
            };
            break;
            
        case BrowserProfile::FIREFOX_LATEST:
        case BrowserProfile::FIREFOX_115:
            fingerprint.cipher_suites = get_firefox_cipher_suites(115);
            fingerprint.extensions = {
                0x0000, // server_name
                0x0017, // extended_master_secret
                0x0005, // status_request
                0x0023, // session_ticket
                0x0010, // application_layer_protocol_negotiation
                0x002b, // supported_versions
                0x002d, // psk_key_exchange_modes
                0x0033  // key_share
            };
            fingerprint.compression_methods = {0x00};
            fingerprint.supported_groups = {"x25519", "secp256r1", "secp384r1", "secp521r1"};
            break;
            
        case BrowserProfile::SAFARI_17:
        case BrowserProfile::SAFARI_16:
            fingerprint.cipher_suites = get_safari_cipher_suites(17);
            fingerprint.extensions = {
                0x0000, // server_name
                0x0017, // extended_master_secret
                0x0010, // application_layer_protocol_negotiation
                0x0005, // status_request
                0x0023, // session_ticket
                0x002b, // supported_versions
                0x0033  // key_share
            };
            fingerprint.compression_methods = {0x00};
            fingerprint.supported_groups = {"x25519", "secp256r1", "secp384r1"};
            break;
            
        case BrowserProfile::EDGE_LATEST:
            // Edge uses same as Chrome
            fingerprint = generate_browser_fingerprint(BrowserProfile::CHROME_LATEST);
            break;
            
        case BrowserProfile::CHROME_MOBILE:
            fingerprint = generate_browser_fingerprint(BrowserProfile::CHROME_LATEST);
            // Adjust for mobile
            fingerprint.extensions.erase(
                std::remove(fingerprint.extensions.begin(), fingerprint.extensions.end(), 0x0001),
                fingerprint.extensions.end()
            );
            break;
            
        case BrowserProfile::SAFARI_IOS:
            fingerprint = generate_browser_fingerprint(BrowserProfile::SAFARI_17);
            // iOS specific adjustments
            fingerprint.supported_groups = {"x25519", "secp256r1"};
            break;
            
        default:
            // Return Chrome as default
            fingerprint = generate_browser_fingerprint(BrowserProfile::CHROME_LATEST);
    }
    
    fingerprint.enable_grease = true;
    return fingerprint;
}

std::string calculate_ja3_hash(const TLSFingerprint& fingerprint) {
    std::stringstream ja3;
    
    // TLS Version
    ja3 << "771,";
    
    // Cipher Suites
    for (size_t i = 0; i < fingerprint.cipher_suites.size(); ++i) {
        if (i > 0) ja3 << "-";
        ja3 << fingerprint.cipher_suites[i];
    }
    ja3 << ",";
    
    // Extensions
    for (size_t i = 0; i < fingerprint.extensions.size(); ++i) {
        if (i > 0) ja3 << "-";
        ja3 << fingerprint.extensions[i];
    }
    ja3 << ",";
    
    // Supported Groups
    for (size_t i = 0; i < fingerprint.supported_groups.size(); ++i) {
        if (i > 0) ja3 << "-";
        // Convert group names to IDs
        if (fingerprint.supported_groups[i] == "x25519") ja3 << "29";
        else if (fingerprint.supported_groups[i] == "secp256r1") ja3 << "23";
        else if (fingerprint.supported_groups[i] == "secp384r1") ja3 << "24";
        else if (fingerprint.supported_groups[i] == "secp521r1") ja3 << "25";
    }
    ja3 << ",";
    
    // Point Formats (always 0 for uncompressed)
    ja3 << "0";
    
    // Calculate MD5 hash of the JA3 string
    std::string ja3_string = ja3.str();
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(mdctx, EVP_md5(), nullptr);
    EVP_DigestUpdate(mdctx, ja3_string.c_str(), ja3_string.length());
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    EVP_MD_CTX_free(mdctx);
    
    // Convert to hex string
    std::stringstream hex_hash;
    for (unsigned int i = 0; i < hash_len; ++i) {
        hex_hash << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
    }
    
    return hex_hash.str();
}

std::string calculate_ja4_hash(const TLSFingerprint& fingerprint) {
    // JA4 is a more complex fingerprint format
    // This is a simplified implementation
    std::stringstream ja4;
    
    // Protocol version
    ja4 << "t13";
    
    // SNI (d for domain)
    ja4 << "d";
    
    // Number of ciphers
    ja4 << std::setw(2) << std::setfill('0') << fingerprint.cipher_suites.size();
    
    // Number of extensions
    ja4 << std::setw(2) << std::setfill('0') << fingerprint.extensions.size();
    
    // ALPN
    ja4 << "h2";
    
    // First cipher suite
    if (!fingerprint.cipher_suites.empty()) {
        ja4 << "_" << std::hex << fingerprint.cipher_suites[0];
    }
    
    // Hash the extensions
    std::string ext_hash = calculate_ja3_hash(fingerprint).substr(0, 12);
    ja4 << "_" << ext_hash;
    
    return ja4.str();
}

} // namespace advanced_tls