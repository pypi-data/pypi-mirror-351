# Installation Guide

## Prerequisites

The Advanced TLS Library requires several development dependencies for full functionality:

### System Requirements
- Python 3.8+
- C++ compiler (GCC/Clang)
- CMake 3.15+
- OpenSSL development headers
- Rust (optional, for performance optimizations)

## Quick Installation

### Option 1: Automatic Dependency Installation

```bash
# Run the dependency installer
./install_deps.sh

# Build the library
python -m build --wheel
pip install dist/*.whl
```

### Option 2: Manual Installation

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y libssl-dev libcrypto++-dev cmake build-essential pkg-config

# Install Rust (optional)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

#### On CentOS/RHEL/Fedora:
```bash
sudo yum install -y openssl-devel cmake gcc-c++ make pkgconfig
# or for newer versions:
sudo dnf install -y openssl-devel cmake gcc-c++ make pkgconfig

# Install Rust (optional)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

#### On macOS:
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install openssl cmake pkg-config

# Install Rust (optional)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

## Building from Source

```bash
# Clone the repository
git clone https://github.com/advanced-tls/advanced-tls-lib.git
cd advanced-tls-lib

# Install Python dependencies
pip install -r requirements.txt

# Build the wheel
python -m build --wheel

# Install the library
pip install dist/*.whl
```

## Feature Matrix

| Component | Requirement | Status |
|-----------|-------------|--------|
| Python API | Python 3.8+ | ✅ Always available |
| C++ Core Engine | OpenSSL dev headers | ⚠️ Optional |
| Rust Performance Layer | Rust toolchain | ⚠️ Optional |
| Browser Fingerprinting | C++ Core Engine | ⚠️ Requires OpenSSL |
| ML Evasion | Rust Performance Layer | ⚠️ Requires Rust |

## Troubleshooting

### OpenSSL Headers Not Found

If you get compilation errors about missing OpenSSL headers:

1. **Ubuntu/Debian**: `sudo apt install libssl-dev`
2. **CentOS/RHEL**: `sudo yum install openssl-devel`
3. **macOS**: `brew install openssl` and add to PATH
4. **Manual build**: Run `./install_deps.sh` for local installation

### Rust Not Found

If Rust features are disabled:

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustup default stable

# Rebuild the library
python -m build --wheel --no-isolation
```

### Permission Issues

If you can't install system packages:

```bash
# Use the automatic installer which handles local builds
./install_deps.sh

# Or install to user directory
pip install --user -e .
```

## Verification

After installation, verify all features are working:

```python
import advanced_tls

# Check feature availability
features = advanced_tls.check_extensions()
print(f"C++ Extensions: {features['cpp']}")
print(f"Rust Extensions: {features['rust']}")

# Test basic functionality
client = advanced_tls.Client(browser='chrome')
response = client.get('https://httpbin.org/get')
print(f"Status: {response.status_code}")
```

## Development Setup

For development work:

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run benchmarks
pytest benchmarks/ --benchmark-only
```