pub mod async_io;
pub mod connection_pool;
pub mod crypto_ops;
pub mod http2_engine;
pub mod performance;
pub mod python_bindings;

use pyo3::prelude::*;

#[pymodule]
fn advanced_tls_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<connection_pool::ConnectionPool>()?;
    m.add_class::<async_io::AsyncClient>()?;
    m.add_function(wrap_pyfunction!(crypto_ops::generate_random_bytes, m)?)?;
    Ok(())
}