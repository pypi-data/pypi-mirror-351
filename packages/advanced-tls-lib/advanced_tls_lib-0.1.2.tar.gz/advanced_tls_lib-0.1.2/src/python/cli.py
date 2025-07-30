"""Command line interface for Advanced TLS Library."""

import argparse
import sys
from typing import Optional

from . import __version__, Client, BrowserProfile
from .utils import setup_logging


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="advanced-tls",
        description="Advanced TLS Library CLI"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test TLS connection")
    test_parser.add_argument("url", help="URL to test")
    test_parser.add_argument(
        "--browser", "-b",
        choices=["chrome", "firefox", "safari", "edge"],
        default="chrome",
        help="Browser profile to use"
    )
    
    # Benchmark command
    bench_parser = subparsers.add_parser("benchmark", help="Run performance benchmarks")
    bench_parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=10,
        help="Number of iterations"
    )
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.verbose:
        setup_logging(debug=True)
    
    if parsed_args.command == "test":
        return test_connection(parsed_args.url, parsed_args.browser)
    elif parsed_args.command == "benchmark":
        return run_benchmark(parsed_args.iterations)
    else:
        parser.print_help()
        return 1


def test_connection(url: str, browser: str) -> int:
    """Test TLS connection to a URL."""
    try:
        client = Client(browser=browser)
        response = client.get(url)
        
        print(f"✅ Connection successful!")
        print(f"Status: {response.status_code}")
        print(f"TLS Version: {response.tls_version}")
        print(f"Cipher: {response.cipher}")
        
        return 0
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1


def run_benchmark(iterations: int) -> int:
    """Run performance benchmarks."""
    import time
    from statistics import mean, stdev
    
    print(f"Running benchmark with {iterations} iterations...")
    
    times = []
    client = Client()
    
    for i in range(iterations):
        start = time.time()
        try:
            response = client.get("https://httpbin.org/get")
            if response.status_code == 200:
                times.append(time.time() - start)
        except Exception:
            pass
        
        print(f"Progress: {i+1}/{iterations}", end="\r")
    
    if times:
        print(f"\n📊 Benchmark Results:")
        print(f"Mean: {mean(times):.3f}s")
        print(f"Std Dev: {stdev(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")
        return 0
    else:
        print("\n❌ Benchmark failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())