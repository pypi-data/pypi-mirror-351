use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use pyo3_asyncio::tokio::future_into_py;

use crate::connection_pool::{ConnectionPool, PoolConfig};
use crate::async_io::AsyncClient;
use crate::crypto_ops::{generate_random_bytes, generate_grease_values, shuffle_list};
use crate::performance::{PerformanceMonitor, PerformanceStats};

/// Python wrapper for ConnectionPool
#[pyclass(name = "RustConnectionPool")]
pub struct PyConnectionPool {
    pool: ConnectionPool,
}

#[pymethods]
impl PyConnectionPool {
    #[new]
    fn new(
        max_connections_per_host: Option<usize>,
        max_idle_connections: Option<usize>,
        idle_timeout_secs: Option<u64>,
    ) -> Self {
        Self {
            pool: ConnectionPool::new(
                max_connections_per_host,
                max_idle_connections,
                idle_timeout_secs,
            ),
        }
    }

    fn get_stats(&self) -> PyResult<PyObject> {
        self.pool.get_stats()
    }

    fn shutdown(&self) -> PyResult<()> {
        self.pool.shutdown()
    }
}

/// Python wrapper for AsyncClient
#[pyclass(name = "RustAsyncClient")]
pub struct PyAsyncClient {
    client: AsyncClient,
}

#[pymethods]
impl PyAsyncClient {
    #[new]
    fn new(timeout_secs: Option<u64>) -> PyResult<Self> {
        Ok(Self {
            client: AsyncClient::new(timeout_secs)?,
        })
    }

    fn connect(&self, host: String, port: u16) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let handle = self.client.connect(host, port)?;
            Ok(handle.into_py(py))
        })
    }
}

/// Python wrapper for PerformanceMonitor
#[pyclass(name = "RustPerformanceMonitor")]
pub struct PyPerformanceMonitor {
    monitor: PerformanceMonitor,
}

#[pymethods]
impl PyPerformanceMonitor {
    #[new]
    fn new() -> Self {
        Self {
            monitor: PerformanceMonitor::new(),
        }
    }

    fn record_request(&self, bytes_sent: u64, bytes_received: u64, latency_ms: u64) {
        use std::time::Duration;
        self.monitor.record_request(
            bytes_sent,
            bytes_received,
            Duration::from_millis(latency_ms),
        );
    }

    fn record_error(&self) {
        self.monitor.record_error();
    }

    fn add_connection(&self) {
        self.monitor.add_connection();
    }

    fn remove_connection(&self) {
        self.monitor.remove_connection();
    }

    fn get_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = self.monitor.get_stats();
            let dict = PyDict::new(py);
            
            dict.set_item("request_count", stats.request_count)?;
            dict.set_item("bytes_sent", stats.bytes_sent)?;
            dict.set_item("bytes_received", stats.bytes_received)?;
            dict.set_item("connection_count", stats.connection_count)?;
            dict.set_item("error_count", stats.error_count)?;
            dict.set_item("uptime_seconds", stats.uptime.as_secs())?;
            dict.set_item("avg_latency_ms", stats.avg_latency.as_millis())?;
            dict.set_item("p99_latency_ms", stats.p99_latency.as_millis())?;
            dict.set_item("requests_per_second", stats.requests_per_second)?;
            
            Ok(dict.into())
        })
    }
}

/// Async function wrapper for Python
#[pyfunction]
fn rust_async_request(py: Python, url: String, timeout_secs: Option<u64>) -> PyResult<&PyAny> {
    future_into_py(py, async move {
        // Simplified async request implementation
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        Ok(format!("Response from {}", url))
    })
}

/// Fast cipher suite shuffling
#[pyfunction]
fn rust_shuffle_ciphers(ciphers: Vec<u16>) -> Vec<u16> {
    shuffle_list(ciphers)
}

/// Generate browser fingerprint
#[pyfunction]
fn rust_generate_fingerprint(browser: &str) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let dict = PyDict::new(py);
        
        match browser {
            "chrome" => {
                dict.set_item("name", "Chrome")?;
                dict.set_item("version", "120")?;
                dict.set_item("ciphers", vec![
                    0x1301, 0x1302, 0x1303, 0xc02b, 0xc02f, 0xc02c, 0xc030
                ])?;
                dict.set_item("extensions", vec![
                    0x0000, 0x0017, 0x0001, 0x0005, 0x0012, 0x0023, 0x002b, 0x002d, 0x0033
                ])?;
            }
            "firefox" => {
                dict.set_item("name", "Firefox")?;
                dict.set_item("version", "115")?;
                dict.set_item("ciphers", vec![
                    0x1301, 0x1303, 0x1302, 0xcca9, 0xcca8, 0xc02b, 0xc02f
                ])?;
                dict.set_item("extensions", vec![
                    0x0000, 0x0017, 0x0005, 0x0023, 0x0010, 0x002b, 0x002d, 0x0033
                ])?;
            }
            _ => {
                return Err(PyValueError::new_err("Unknown browser"));
            }
        }
        
        Ok(dict.into())
    })
}

/// Fast hash computation
#[pyfunction]
fn rust_compute_ja3_hash(py: Python, fingerprint_str: &str) -> PyResult<&PyBytes> {
    use crate::crypto_ops::hash::xxhash64;
    
    let hash = xxhash64(fingerprint_str.as_bytes(), 0);
    let hash_bytes = hash.to_le_bytes();
    
    Ok(PyBytes::new(py, &hash_bytes))
}

/// Module initialization
pub fn init_python_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyConnectionPool>()?;
    m.add_class::<PyAsyncClient>()?;
    m.add_class::<PyPerformanceMonitor>()?;
    
    m.add_function(wrap_pyfunction!(rust_async_request, m)?)?;
    m.add_function(wrap_pyfunction!(rust_shuffle_ciphers, m)?)?;
    m.add_function(wrap_pyfunction!(rust_generate_fingerprint, m)?)?;
    m.add_function(wrap_pyfunction!(rust_compute_ja3_hash, m)?)?;
    
    // Re-export crypto functions
    m.add_function(wrap_pyfunction!(generate_random_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(generate_grease_values, m)?)?;
    
    Ok(())
}