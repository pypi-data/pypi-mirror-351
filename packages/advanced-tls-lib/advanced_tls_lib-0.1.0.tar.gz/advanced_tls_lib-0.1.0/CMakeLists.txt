cmake_minimum_required(VERSION 3.15)
project(advanced_tls_lib VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set build type default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /bigobj")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /DNDEBUG")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
endif()

# Find required packages
find_package(PkgConfig REQUIRED)

# Find OpenSSL (BoringSSL preferred)
find_package(OpenSSL REQUIRED)
if(OpenSSL_FOUND)
    message(STATUS "Found OpenSSL ${OPENSSL_VERSION}")
endif()

# Find pybind11
find_package(pybind11 REQUIRED)
if(pybind11_FOUND)
    message(STATUS "Found pybind11 ${pybind11_VERSION}")
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${OPENSSL_INCLUDE_DIR})

# Source files
set(CORE_SOURCES
    src/core/tls_engine.cpp
    src/core/fingerprint_gen.cpp
    src/core/browser_profiles.cpp
    src/core/detection_evasion.cpp
)

# Create core library
add_library(advanced_tls_core STATIC ${CORE_SOURCES})
target_link_libraries(advanced_tls_core ${OPENSSL_LIBRARIES})

# Set library properties
set_target_properties(advanced_tls_core PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

# Create Python module
pybind11_add_module(advanced_tls_cpp
    bindings/cpp_bindings.cpp
)

target_link_libraries(advanced_tls_cpp PRIVATE 
    advanced_tls_core
    ${OPENSSL_LIBRARIES}
)

# Set module properties
set_target_properties(advanced_tls_cpp PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    INTERPROCEDURAL_OPTIMIZATION TRUE
)

# Compiler-specific optimizations
target_compile_definitions(advanced_tls_cpp PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

# Platform-specific settings
if(WIN32)
    target_compile_definitions(advanced_tls_core PRIVATE WIN32_LEAN_AND_MEAN NOMINMAX)
    target_link_libraries(advanced_tls_core ws2_32 crypt32)
elseif(APPLE)
    target_link_libraries(advanced_tls_core "-framework Security" "-framework SystemConfiguration")
else()
    target_link_libraries(advanced_tls_core pthread)
endif()

# Optional features
option(BUILD_TESTS "Build tests" OFF)
option(BUILD_BENCHMARKS "Build benchmarks" OFF)
option(BUILD_EXAMPLES "Build examples" OFF)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

if(BUILD_BENCHMARKS)
    add_subdirectory(benchmarks)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Install rules
install(TARGETS advanced_tls_core
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY src/core/
    DESTINATION include/advanced_tls
    FILES_MATCHING PATTERN "*.h"
)

# CPack configuration
set(CPACK_PACKAGE_NAME "advanced-tls-lib")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION "Advanced TLS Library for Python")
set(CPACK_PACKAGE_CONTACT "advanced-tls-team@example.com")

if(WIN32)
    set(CPACK_GENERATOR "ZIP")
elseif(APPLE)
    set(CPACK_GENERATOR "DragNDrop")
else()
    set(CPACK_GENERATOR "TGZ")
endif()

include(CPack)