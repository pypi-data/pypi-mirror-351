#!/bin/bash

# Install OpenSSL development headers without requiring sudo
echo "Setting up development dependencies for Advanced TLS Library..."

# Create a local installation directory
mkdir -p ~/.local/include ~/.local/lib ~/.local/bin

# Check if we can install system packages
if command -v apt &> /dev/null && [ "$EUID" -eq 0 ]; then
    echo "Installing system packages..."
    apt update
    apt install -y libssl-dev libcrypto++-dev cmake build-essential pkg-config
elif command -v apt &> /dev/null; then
    echo "No sudo access - using alternative approach..."
    
    # Download and compile OpenSSL from source
    cd /tmp
    wget -q https://www.openssl.org/source/openssl-3.0.13.tar.gz
    tar -xzf openssl-3.0.13.tar.gz
    cd openssl-3.0.13
    
    ./Configure --prefix=$HOME/.local linux-x86_64 shared
    make -j$(nproc)
    make install_sw
    
    # Add to environment
    export PKG_CONFIG_PATH=$HOME/.local/lib/pkgconfig:$PKG_CONFIG_PATH
    export LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH
    export CPPFLAGS="-I$HOME/.local/include $CPPFLAGS"
    export LDFLAGS="-L$HOME/.local/lib $LDFLAGS"
    
    echo "export PKG_CONFIG_PATH=$HOME/.local/lib/pkgconfig:\$PKG_CONFIG_PATH" >> ~/.bashrc
    echo "export LD_LIBRARY_PATH=$HOME/.local/lib:\$LD_LIBRARY_PATH" >> ~/.bashrc
    echo "export CPPFLAGS=\"-I$HOME/.local/include \$CPPFLAGS\"" >> ~/.bashrc
    echo "export LDFLAGS=\"-L$HOME/.local/lib \$LDFLAGS\"" >> ~/.bashrc
fi

# Install Rust if not present
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    rustup default stable
fi

echo "Development dependencies setup complete!"
echo "You may need to reload your shell: source ~/.bashrc"