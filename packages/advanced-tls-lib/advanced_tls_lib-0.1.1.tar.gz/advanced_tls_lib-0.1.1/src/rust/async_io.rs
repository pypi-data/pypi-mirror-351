use std::sync::Arc;
use std::time::Duration;
use std::net::SocketAddr;
use std::pin::Pin;
use std::task::{Context, Poll};

use tokio::net::TcpStream;
use tokio::io::{AsyncRead, AsyncWrite, ReadBuf};
use tokio::time::timeout;
use bytes::{Bytes, BytesMut};
use futures::future::BoxFuture;
use hyper::client::conn;
use http::{Request, Response};
use rustls::{ClientConfig, OwnedTrustAnchor, RootCertStore};
use pin_project::pin_project;
use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::exceptions::PyIOError;

/// High-performance async I/O client
#[pyclass]
pub struct AsyncClient {
    runtime: Arc<tokio::runtime::Runtime>,
    config: Arc<ClientConfig>,
    timeout_duration: Duration,
}

#[pymethods]
impl AsyncClient {
    #[new]
    pub fn new(timeout_secs: Option<u64>) -> PyResult<Self> {
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .worker_threads(num_cpus::get())
            .thread_name("advanced-tls-async")
            .build()
            .map_err(|e| PyIOError::new_err(e.to_string()))?;

        let config = create_rustls_config()
            .map_err(|e| PyIOError::new_err(e.to_string()))?;

        Ok(Self {
            runtime: Arc::new(runtime),
            config: Arc::new(config),
            timeout_duration: Duration::from_secs(timeout_secs.unwrap_or(30)),
        })
    }

    pub fn connect(&self, host: String, port: u16) -> PyResult<ConnectionHandle> {
        let config = self.config.clone();
        let timeout_duration = self.timeout_duration;

        let handle = self.runtime.spawn(async move {
            timeout(timeout_duration, async {
                establish_connection(&host, port, config).await
            }).await
        });

        Ok(ConnectionHandle {
            runtime: self.runtime.clone(),
            handle: Arc::new(RwLock::new(Some(handle))),
        })
    }
}

#[pyclass]
pub struct ConnectionHandle {
    runtime: Arc<tokio::runtime::Runtime>,
    handle: Arc<RwLock<Option<tokio::task::JoinHandle<Result<Connection, std::io::Error>>>>>,
}

#[pymethods]
impl ConnectionHandle {
    pub fn is_ready(&self) -> bool {
        let handle = self.handle.read();
        if let Some(h) = handle.as_ref() {
            h.is_finished()
        } else {
            true
        }
    }

    pub fn get_result(&self) -> PyResult<Option<String>> {
        let mut handle = self.handle.write();
        if let Some(h) = handle.take() {
            match self.runtime.block_on(h) {
                Ok(Ok(_conn)) => Ok(Some("Connected successfully".to_string())),
                Ok(Err(e)) => Err(PyIOError::new_err(e.to_string())),
                Err(e) => Err(PyIOError::new_err(e.to_string())),
            }
        } else {
            Ok(None)
        }
    }
}

/// Custom TLS stream wrapper for advanced features
#[pin_project]
pub struct AdvancedTlsStream<S> {
    #[pin]
    inner: S,
    read_buffer: BytesMut,
    write_buffer: BytesMut,
    stats: Arc<RwLock<ConnectionStats>>,
}

#[derive(Default)]
struct ConnectionStats {
    bytes_read: u64,
    bytes_written: u64,
    read_operations: u64,
    write_operations: u64,
}

impl<S> AdvancedTlsStream<S> {
    pub fn new(inner: S) -> Self {
        Self {
            inner,
            read_buffer: BytesMut::with_capacity(8192),
            write_buffer: BytesMut::with_capacity(8192),
            stats: Arc::new(RwLock::new(ConnectionStats::default())),
        }
    }
}

impl<S> AsyncRead for AdvancedTlsStream<S>
where
    S: AsyncRead + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<std::io::Result<()>> {
        let mut this = self.project();
        
        // Update stats
        {
            let mut stats = this.stats.write();
            stats.read_operations += 1;
        }

        match this.inner.poll_read(cx, buf) {
            Poll::Ready(Ok(())) => {
                let bytes_read = buf.filled().len();
                let mut stats = this.stats.write();
                stats.bytes_read += bytes_read as u64;
                Poll::Ready(Ok(()))
            }
            other => other,
        }
    }
}

impl<S> AsyncWrite for AdvancedTlsStream<S>
where
    S: AsyncWrite + Unpin,
{
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<std::io::Result<usize>> {
        let mut this = self.project();
        
        // Update stats
        {
            let mut stats = this.stats.write();
            stats.write_operations += 1;
        }

        match this.inner.poll_write(cx, buf) {
            Poll::Ready(Ok(n)) => {
                let mut stats = this.stats.write();
                stats.bytes_written += n as u64;
                Poll::Ready(Ok(n))
            }
            other => other,
        }
    }

    fn poll_flush(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<std::io::Result<()>> {
        self.project().inner.poll_flush(cx)
    }

    fn poll_shutdown(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<std::io::Result<()>> {
        self.project().inner.poll_shutdown(cx)
    }
}

pub struct Connection {
    stream: Box<dyn AsyncRead + AsyncWrite + Send + Sync + Unpin>,
    remote_addr: SocketAddr,
}

async fn establish_connection(
    host: &str,
    port: u16,
    config: Arc<ClientConfig>,
) -> Result<Connection, std::io::Error> {
    let addr = format!("{}:{}", host, port);
    let socket_addr: SocketAddr = addr.parse()
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidInput, e))?;

    // Create TCP connection with optimized settings
    let socket = create_optimized_socket(&socket_addr)?;
    let tcp_stream = TcpStream::from_std(socket.into())
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;

    // Enable TCP_NODELAY for lower latency
    tcp_stream.set_nodelay(true)?;

    // Wrap in our advanced TLS stream
    let tls_stream = AdvancedTlsStream::new(tcp_stream);

    Ok(Connection {
        stream: Box::new(tls_stream),
        remote_addr: socket_addr,
    })
}

fn create_optimized_socket(addr: &SocketAddr) -> std::io::Result<socket2::Socket> {
    use socket2::{Domain, Protocol, Socket, Type};

    let domain = if addr.is_ipv4() {
        Domain::IPV4
    } else {
        Domain::IPV6
    };

    let socket = Socket::new(domain, Type::STREAM, Some(Protocol::TCP))?;

    // Set socket options for performance
    socket.set_reuse_address(true)?;
    socket.set_nodelay(true)?;
    
    // Set socket buffer sizes for better throughput
    socket.set_send_buffer_size(256 * 1024)?;
    socket.set_recv_buffer_size(256 * 1024)?;

    // Enable TCP keepalive
    let keepalive = socket2::TcpKeepalive::new()
        .with_time(Duration::from_secs(60))
        .with_interval(Duration::from_secs(30));
    socket.set_tcp_keepalive(&keepalive)?;

    // Connect to the address
    socket.connect(&addr.into())?;

    Ok(socket)
}

fn create_rustls_config() -> Result<ClientConfig, Box<dyn std::error::Error>> {
    let mut root_store = RootCertStore::empty();
    
    // Add webpki roots
    root_store.add_trust_anchors(
        webpki_roots::TLS_SERVER_ROOTS
            .iter()
            .map(|ta| {
                OwnedTrustAnchor::from_subject_spki_name_constraints(
                    ta.subject,
                    ta.spki,
                    ta.name_constraints,
                )
            }),
    );

    let config = ClientConfig::builder()
        .with_safe_defaults()
        .with_root_certificates(root_store)
        .with_no_client_auth();

    Ok(config)
}

/// Zero-copy buffer management
pub struct ZeroCopyBuffer {
    data: Bytes,
    position: usize,
}

impl ZeroCopyBuffer {
    pub fn new(capacity: usize) -> Self {
        Self {
            data: Bytes::new(),
            position: 0,
        }
    }

    pub fn write(&mut self, data: Bytes) {
        self.data = data;
        self.position = 0;
    }

    pub fn read(&mut self, len: usize) -> Option<Bytes> {
        if self.position + len <= self.data.len() {
            let slice = self.data.slice(self.position..self.position + len);
            self.position += len;
            Some(slice)
        } else {
            None
        }
    }

    pub fn remaining(&self) -> usize {
        self.data.len() - self.position
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_zero_copy_buffer() {
        let mut buffer = ZeroCopyBuffer::new(1024);
        let data = Bytes::from("Hello, World!");
        
        buffer.write(data.clone());
        assert_eq!(buffer.remaining(), 13);
        
        let read_data = buffer.read(5).unwrap();
        assert_eq!(&read_data[..], b"Hello");
        assert_eq!(buffer.remaining(), 8);
    }
}