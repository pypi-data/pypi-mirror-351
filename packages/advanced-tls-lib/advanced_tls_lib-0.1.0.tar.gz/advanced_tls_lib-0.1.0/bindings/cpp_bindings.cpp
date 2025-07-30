#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <future>
#include <thread>
#include "src/core/tls_engine.h"
#include "src/core/fingerprint_gen.h"
#include "src/core/browser_profiles.h"
#include "src/core/detection_evasion.h"

namespace py = pybind11;
using namespace advanced_tls;

// Python wrapper for TLSEngine with GIL management
class PyTLSEngine {
private:
    std::unique_ptr<TLSEngine> engine;
    
public:
    PyTLSEngine() : engine(std::make_unique<TLSEngine>()) {}
    
    bool initialize(BrowserProfile profile, EvasionLevel evasion_level = EvasionLevel::ADVANCED) {
        py::gil_scoped_release release;
        return engine->initialize(profile, evasion_level);
    }
    
    bool initialize_custom(const TLSFingerprint& fingerprint) {
        py::gil_scoped_release release;
        return engine->initialize(fingerprint);
    }
    
    void set_connection_options(const ConnectionOptions& options) {
        engine->set_connection_options(options);
    }
    
    bool connect(const std::string& hostname, int port) {
        py::gil_scoped_release release;
        return engine->connect(hostname, port);
    }
    
    bool send_request(const std::string& method, const std::string& path,
                     const std::unordered_map<std::string, std::string>& headers,
                     const std::string& body = "") {
        py::gil_scoped_release release;
        return engine->send_request(method, path, headers, body);
    }
    
    std::string receive_response() {
        py::gil_scoped_release release;
        return engine->receive_response();
    }
    
    void close() {
        py::gil_scoped_release release;
        engine->close();
    }
    
    TLSFingerprint get_current_fingerprint() const {
        return engine->get_current_fingerprint();
    }
    
    void rotate_fingerprint() {
        py::gil_scoped_release release;
        engine->rotate_fingerprint();
    }
    
    std::string get_ja3_hash() const {
        return engine->get_ja3_hash();
    }
    
    std::string get_ja4_hash() const {
        return engine->get_ja4_hash();
    }
    
    void enable_ml_evasion(bool enable) {
        engine->enable_ml_evasion(enable);
    }
};

// Python wrapper for async operations
class PyAsyncTLSEngine {
private:
    std::unique_ptr<TLSEngine> engine;
    std::future<bool> connect_future;
    std::future<std::string> response_future;
    
public:
    PyAsyncTLSEngine() : engine(std::make_unique<TLSEngine>()) {}
    
    void connect_async(const std::string& hostname, int port) {
        connect_future = std::async(std::launch::async, [this, hostname, port]() {
            return engine->connect(hostname, port);
        });
    }
    
    bool is_connected() {
        if (connect_future.valid()) {
            return connect_future.wait_for(std::chrono::milliseconds(0)) == std::future_status::ready;
        }
        return false;
    }
    
    bool get_connect_result() {
        if (connect_future.valid()) {
            return connect_future.get();
        }
        return false;
    }
    
    void send_request_async(const std::string& method, const std::string& path,
                           const std::unordered_map<std::string, std::string>& headers,
                           const std::string& body = "") {
        response_future = std::async(std::launch::async, [this, method, path, headers, body]() {
            if (engine->send_request(method, path, headers, body)) {
                return engine->receive_response();
            }
            return std::string("");
        });
    }
    
    bool has_response() {
        if (response_future.valid()) {
            return response_future.wait_for(std::chrono::milliseconds(0)) == std::future_status::ready;
        }
        return false;
    }
    
    std::string get_response() {
        if (response_future.valid()) {
            return response_future.get();
        }
        return "";
    }
};

PYBIND11_MODULE(advanced_tls_cpp, m) {
    m.doc() = "Advanced TLS Library - C++ Core Bindings";
    
    // Enums
    py::enum_<BrowserProfile>(m, "BrowserProfile")
        .value("CHROME_LATEST", BrowserProfile::CHROME_LATEST)
        .value("CHROME_120", BrowserProfile::CHROME_120)
        .value("CHROME_110", BrowserProfile::CHROME_110)
        .value("FIREFOX_LATEST", BrowserProfile::FIREFOX_LATEST)
        .value("FIREFOX_115", BrowserProfile::FIREFOX_115)
        .value("SAFARI_17", BrowserProfile::SAFARI_17)
        .value("SAFARI_16", BrowserProfile::SAFARI_16)
        .value("EDGE_LATEST", BrowserProfile::EDGE_LATEST)
        .value("CHROME_MOBILE", BrowserProfile::CHROME_MOBILE)
        .value("SAFARI_IOS", BrowserProfile::SAFARI_IOS)
        .value("CUSTOM", BrowserProfile::CUSTOM);
    
    py::enum_<EvasionLevel>(m, "EvasionLevel")
        .value("BASIC", EvasionLevel::BASIC)
        .value("ADVANCED", EvasionLevel::ADVANCED)
        .value("MAXIMUM", EvasionLevel::MAXIMUM);
    
    py::enum_<DetectionSystem>(m, "DetectionSystem")
        .value("CLOUDFLARE", DetectionSystem::CLOUDFLARE)
        .value("AKAMAI", DetectionSystem::AKAMAI)
        .value("IMPERVA", DetectionSystem::IMPERVA)
        .value("DATADOME", DetectionSystem::DATADOME)
        .value("PERIMETERX", DetectionSystem::PERIMETERX)
        .value("SHAPE_SECURITY", DetectionSystem::SHAPE_SECURITY)
        .value("KASADA", DetectionSystem::KASADA)
        .value("GENERIC", DetectionSystem::GENERIC);
    
    // TLSFingerprint
    py::class_<TLSFingerprint>(m, "TLSFingerprint")
        .def(py::init<>())
        .def_readwrite("cipher_suites", &TLSFingerprint::cipher_suites)
        .def_readwrite("extensions", &TLSFingerprint::extensions)
        .def_readwrite("compression_methods", &TLSFingerprint::compression_methods)
        .def_readwrite("supported_groups", &TLSFingerprint::supported_groups)
        .def_readwrite("signature_algorithms", &TLSFingerprint::signature_algorithms)
        .def_readwrite("enable_grease", &TLSFingerprint::enable_grease)
        .def_readwrite("ja3_string", &TLSFingerprint::ja3_string)
        .def_readwrite("ja4_string", &TLSFingerprint::ja4_string);
    
    // ConnectionOptions
    py::class_<ConnectionOptions>(m, "ConnectionOptions")
        .def(py::init<>())
        .def_readwrite("proxy_url", &ConnectionOptions::proxy_url)
        .def_readwrite("timeout_ms", &ConnectionOptions::timeout_ms)
        .def_readwrite("verify_ssl", &ConnectionOptions::verify_ssl)
        .def_readwrite("custom_ca_path", &ConnectionOptions::custom_ca_path)
        .def_readwrite("max_redirects", &ConnectionOptions::max_redirects)
        .def_readwrite("enable_http2", &ConnectionOptions::enable_http2)
        .def_readwrite("enable_http3", &ConnectionOptions::enable_http3);
    
    // TLSEngine
    py::class_<PyTLSEngine>(m, "TLSEngine")
        .def(py::init<>())
        .def("initialize", &PyTLSEngine::initialize, 
             py::arg("profile"), 
             py::arg("evasion_level") = EvasionLevel::ADVANCED)
        .def("initialize_custom", &PyTLSEngine::initialize_custom)
        .def("set_connection_options", &PyTLSEngine::set_connection_options)
        .def("connect", &PyTLSEngine::connect)
        .def("send_request", &PyTLSEngine::send_request,
             py::arg("method"),
             py::arg("path"),
             py::arg("headers"),
             py::arg("body") = "")
        .def("receive_response", &PyTLSEngine::receive_response)
        .def("close", &PyTLSEngine::close)
        .def("get_current_fingerprint", &PyTLSEngine::get_current_fingerprint)
        .def("rotate_fingerprint", &PyTLSEngine::rotate_fingerprint)
        .def("get_ja3_hash", &PyTLSEngine::get_ja3_hash)
        .def("get_ja4_hash", &PyTLSEngine::get_ja4_hash)
        .def("enable_ml_evasion", &PyTLSEngine::enable_ml_evasion);
    
    // AsyncTLSEngine
    py::class_<PyAsyncTLSEngine>(m, "AsyncTLSEngine")
        .def(py::init<>())
        .def("connect_async", &PyAsyncTLSEngine::connect_async)
        .def("is_connected", &PyAsyncTLSEngine::is_connected)
        .def("get_connect_result", &PyAsyncTLSEngine::get_connect_result)
        .def("send_request_async", &PyAsyncTLSEngine::send_request_async,
             py::arg("method"),
             py::arg("path"),
             py::arg("headers"),
             py::arg("body") = "")
        .def("has_response", &PyAsyncTLSEngine::has_response)
        .def("get_response", &PyAsyncTLSEngine::get_response);
    
    // FingerprintGenerator
    py::class_<FingerprintGenerator>(m, "FingerprintGenerator")
        .def(py::init<>())
        .def("generate", &FingerprintGenerator::generate)
        .def("generate_adaptive", &FingerprintGenerator::generate_adaptive)
        .def("generate_weighted", &FingerprintGenerator::generate_weighted)
        .def("validate", &FingerprintGenerator::validate)
        .def("mutate", &FingerprintGenerator::mutate)
        .def("get_stats", &FingerprintGenerator::get_stats);
    
    // FingerprintGenerator::Builder
    py::class_<FingerprintGenerator::Builder>(m, "FingerprintBuilder")
        .def("with_cipher_suites", &FingerprintGenerator::Builder::with_cipher_suites)
        .def("with_extensions", &FingerprintGenerator::Builder::with_extensions)
        .def("with_compression_methods", &FingerprintGenerator::Builder::with_compression_methods)
        .def("with_supported_groups", &FingerprintGenerator::Builder::with_supported_groups)
        .def("with_signature_algorithms", &FingerprintGenerator::Builder::with_signature_algorithms)
        .def("enable_grease", &FingerprintGenerator::Builder::enable_grease,
             py::arg("enable") = true)
        .def("randomize_order", &FingerprintGenerator::Builder::randomize_order)
        .def("build", &FingerprintGenerator::Builder::build);
    
    // Static builder method
    m.def("fingerprint_builder", &FingerprintGenerator::builder);
    
    // BrowserCharacteristics
    py::class_<BrowserCharacteristics>(m, "BrowserCharacteristics")
        .def(py::init<>())
        .def_readwrite("user_agent", &BrowserCharacteristics::user_agent)
        .def_readwrite("accept_headers", &BrowserCharacteristics::accept_headers)
        .def_readwrite("accept_languages", &BrowserCharacteristics::accept_languages)
        .def_readwrite("accept_encodings", &BrowserCharacteristics::accept_encodings)
        .def_readwrite("sec_ch_ua", &BrowserCharacteristics::sec_ch_ua)
        .def_readwrite("sec_ch_ua_mobile", &BrowserCharacteristics::sec_ch_ua_mobile)
        .def_readwrite("sec_ch_ua_platform", &BrowserCharacteristics::sec_ch_ua_platform)
        .def_readwrite("supports_http2", &BrowserCharacteristics::supports_http2)
        .def_readwrite("supports_http3", &BrowserCharacteristics::supports_http3)
        .def_readwrite("supports_brotli", &BrowserCharacteristics::supports_brotli)
        .def_readwrite("additional_headers", &BrowserCharacteristics::additional_headers);
    
    // BrowserProfileManager
    py::class_<BrowserProfileManager>(m, "BrowserProfileManager")
        .def(py::init<>())
        .def("get_profile", &BrowserProfileManager::get_profile)
        .def("get_chrome_profile", &BrowserProfileManager::get_chrome_profile)
        .def("get_firefox_profile", &BrowserProfileManager::get_firefox_profile)
        .def("get_safari_profile", &BrowserProfileManager::get_safari_profile)
        .def("get_chrome_mobile_profile", &BrowserProfileManager::get_chrome_mobile_profile)
        .def("validate_profile", &BrowserProfileManager::validate_profile)
        .def("generate_user_agent", &BrowserProfileManager::generate_user_agent,
             py::arg("profile"),
             py::arg("os") = "")
        .def("get_http2_settings", &BrowserProfileManager::get_http2_settings)
        .def("get_client_hints", &BrowserProfileManager::get_client_hints);
    
    // CompleteProfile
    py::class_<BrowserProfileManager::CompleteProfile>(m, "CompleteProfile")
        .def_readwrite("tls_fingerprint", &BrowserProfileManager::CompleteProfile::tls_fingerprint)
        .def_readwrite("characteristics", &BrowserProfileManager::CompleteProfile::characteristics)
        .def_readwrite("http2_fingerprint", &BrowserProfileManager::CompleteProfile::http2_fingerprint);
    
    // HTTP2Settings
    py::class_<BrowserProfileManager::HTTP2Settings>(m, "HTTP2Settings")
        .def(py::init<>())
        .def_readwrite("header_table_size", &BrowserProfileManager::HTTP2Settings::header_table_size)
        .def_readwrite("enable_push", &BrowserProfileManager::HTTP2Settings::enable_push)
        .def_readwrite("max_concurrent_streams", &BrowserProfileManager::HTTP2Settings::max_concurrent_streams)
        .def_readwrite("initial_window_size", &BrowserProfileManager::HTTP2Settings::initial_window_size)
        .def_readwrite("max_frame_size", &BrowserProfileManager::HTTP2Settings::max_frame_size)
        .def_readwrite("max_header_list_size", &BrowserProfileManager::HTTP2Settings::max_header_list_size)
        .def_readwrite("settings_order", &BrowserProfileManager::HTTP2Settings::settings_order)
        .def_readwrite("window_update_increment", &BrowserProfileManager::HTTP2Settings::window_update_increment)
        .def_readwrite("pseudo_header_order", &BrowserProfileManager::HTTP2Settings::pseudo_header_order);
    
    // EvasionEngine
    py::class_<EvasionEngine>(m, "EvasionEngine")
        .def(py::init<>())
        .def("configure_for_target", &EvasionEngine::configure_for_target)
        .def("apply_evasion", &EvasionEngine::apply_evasion)
        .def("apply_header_evasion", &EvasionEngine::apply_header_evasion)
        .def("get_timing_strategy", &EvasionEngine::get_timing_strategy)
        .def("get_request_pattern", &EvasionEngine::get_request_pattern)
        .def("get_anti_fingerprinting_config", &EvasionEngine::get_anti_fingerprinting_config)
        .def("apply_cipher_stunting_protection", &EvasionEngine::apply_cipher_stunting_protection)
        .def("randomize_ja3", &EvasionEngine::randomize_ja3)
        .def("randomize_ja4", &EvasionEngine::randomize_ja4)
        .def("apply_http2_evasion", &EvasionEngine::apply_http2_evasion)
        .def("get_cookie_strategy", &EvasionEngine::get_cookie_strategy)
        .def("get_js_challenge_config", &EvasionEngine::get_js_challenge_config)
        .def("get_ml_evasion", &EvasionEngine::get_ml_evasion,
             py::return_value_policy::reference);
    
    // TimingStrategy
    py::class_<EvasionEngine::TimingStrategy>(m, "TimingStrategy")
        .def(py::init<>())
        .def_readwrite("min_request_interval_ms", &EvasionEngine::TimingStrategy::min_request_interval_ms)
        .def_readwrite("max_request_interval_ms", &EvasionEngine::TimingStrategy::max_request_interval_ms)
        .def_readwrite("use_exponential_backoff", &EvasionEngine::TimingStrategy::use_exponential_backoff)
        .def_readwrite("simulate_human_timing", &EvasionEngine::TimingStrategy::simulate_human_timing)
        .def_readwrite("jitter_factor", &EvasionEngine::TimingStrategy::jitter_factor);
    
    // Utility functions
    m.def("generate_browser_fingerprint", &generate_browser_fingerprint);
    m.def("calculate_ja3_hash", &calculate_ja3_hash);
    m.def("calculate_ja4_hash", &calculate_ja4_hash);
    m.def("get_chrome_cipher_suites", &get_chrome_cipher_suites,
          py::arg("version") = 120);
    m.def("get_firefox_cipher_suites", &get_firefox_cipher_suites,
          py::arg("version") = 115);
    m.def("get_safari_cipher_suites", &get_safari_cipher_suites,
          py::arg("version") = 17);
    
    // Fingerprint utilities
    py::module fingerprint_utils = m.def_submodule("fingerprint_utils");
    fingerprint_utils.def("is_suspicious", &fingerprint_utils::is_suspicious);
    fingerprint_utils.def("apply_time_variation", &fingerprint_utils::apply_time_variation);
    fingerprint_utils.def("apply_geo_variation", &fingerprint_utils::apply_geo_variation);
    fingerprint_utils.def("mix_fingerprints", &fingerprint_utils::mix_fingerprints,
                         py::arg("fp1"),
                         py::arg("fp2"),
                         py::arg("weight") = 0.5);
    fingerprint_utils.def("to_mobile_variant", &fingerprint_utils::to_mobile_variant);
    fingerprint_utils.def("apply_anti_stunting", &fingerprint_utils::apply_anti_stunting);
    
    // Evasion utilities
    py::module evasion_utils = m.def_submodule("evasion_utils");
    evasion_utils.def("is_blocked_response", &evasion_utils::is_blocked_response);
    evasion_utils.def("generate_referrer_chain", &evasion_utils::generate_referrer_chain);
    evasion_utils.def("calculate_human_delay", &evasion_utils::calculate_human_delay);
    evasion_utils.def("contains_fingerprinting_js", &evasion_utils::contains_fingerprinting_js);
    evasion_utils.def("extract_challenge", &evasion_utils::extract_challenge);
    evasion_utils.def("solve_challenge", &evasion_utils::solve_challenge);
    
    // Browser behavior functions
    m.def("generate_human_mouse_pattern", &BrowserBehavior::generate_human_mouse_pattern);
    m.def("generate_human_typing_pattern", &BrowserBehavior::generate_human_typing_pattern);
    m.def("get_browser_timing_pattern", &BrowserBehavior::get_browser_timing_pattern);
    m.def("get_page_load_behavior", &BrowserBehavior::get_page_load_behavior);
    
    // Version info
    m.attr("__version__") = "0.1.0";
    m.attr("__author__") = "Advanced TLS Team";
}