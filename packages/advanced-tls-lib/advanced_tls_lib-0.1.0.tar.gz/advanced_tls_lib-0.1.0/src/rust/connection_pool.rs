use std::sync::Arc;
use std::time::{Duration, Instant};
use std::collections::VecDeque;
use std::net::SocketAddr;

use tokio::sync::{Mutex, Semaphore};
use tokio::time::interval;
use dashmap::DashMap;
use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

use crate::async_io::Connection;

/// Connection pool configuration
#[derive(Clone)]
pub struct PoolConfig {
    pub max_connections_per_host: usize,
    pub max_idle_connections: usize,
    pub idle_timeout: Duration,
    pub connection_timeout: Duration,
    pub max_lifetime: Duration,
    pub health_check_interval: Duration,
}

impl Default for PoolConfig {
    fn default() -> Self {
        Self {
            max_connections_per_host: 100,
            max_idle_connections: 50,
            idle_timeout: Duration::from_secs(90),
            connection_timeout: Duration::from_secs(10),
            max_lifetime: Duration::from_secs(600),
            health_check_interval: Duration::from_secs(30),
        }
    }
}

/// Connection wrapper with metadata
struct PooledConnection {
    conn: Connection,
    created_at: Instant,
    last_used: Instant,
    use_count: u64,
    host: String,
    is_healthy: bool,
}

impl PooledConnection {
    fn new(conn: Connection, host: String) -> Self {
        let now = Instant::now();
        Self {
            conn,
            created_at: now,
            last_used: now,
            use_count: 0,
            host,
            is_healthy: true,
        }
    }

    fn is_expired(&self, max_lifetime: Duration, idle_timeout: Duration) -> bool {
        let now = Instant::now();
        now.duration_since(self.created_at) > max_lifetime ||
        now.duration_since(self.last_used) > idle_timeout
    }

    fn mark_used(&mut self) {
        self.last_used = Instant::now();
        self.use_count += 1;
    }
}

/// High-performance connection pool
#[pyclass]
pub struct ConnectionPool {
    config: Arc<PoolConfig>,
    // Host -> Queue of connections
    connections: Arc<DashMap<String, Arc<Mutex<VecDeque<PooledConnection>>>>>,
    // Semaphore to limit total connections
    semaphore: Arc<Semaphore>,
    // Statistics
    stats: Arc<RwLock<PoolStats>>,
    // Shutdown flag
    shutdown: Arc<RwLock<bool>>,
}

#[derive(Default)]
struct PoolStats {
    total_connections: u64,
    active_connections: u64,
    idle_connections: u64,
    connections_created: u64,
    connections_closed: u64,
    connections_reused: u64,
    health_checks_performed: u64,
    health_check_failures: u64,
}

#[pymethods]
impl ConnectionPool {
    #[new]
    pub fn new(
        max_connections_per_host: Option<usize>,
        max_idle_connections: Option<usize>,
        idle_timeout_secs: Option<u64>,
    ) -> Self {
        let mut config = PoolConfig::default();
        
        if let Some(max) = max_connections_per_host {
            config.max_connections_per_host = max;
        }
        if let Some(max) = max_idle_connections {
            config.max_idle_connections = max;
        }
        if let Some(timeout) = idle_timeout_secs {
            config.idle_timeout = Duration::from_secs(timeout);
        }

        let total_connections = config.max_connections_per_host * 10; // Support 10 hosts
        
        let pool = Self {
            config: Arc::new(config),
            connections: Arc::new(DashMap::new()),
            semaphore: Arc::new(Semaphore::new(total_connections)),
            stats: Arc::new(RwLock::new(PoolStats::default())),
            shutdown: Arc::new(RwLock::new(false)),
        };

        // Start background tasks
        pool.start_maintenance_tasks();

        pool
    }

    pub fn get_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = self.stats.read();
            let dict = pyo3::types::PyDict::new(py);
            
            dict.set_item("total_connections", stats.total_connections)?;
            dict.set_item("active_connections", stats.active_connections)?;
            dict.set_item("idle_connections", stats.idle_connections)?;
            dict.set_item("connections_created", stats.connections_created)?;
            dict.set_item("connections_closed", stats.connections_closed)?;
            dict.set_item("connections_reused", stats.connections_reused)?;
            dict.set_item("health_checks_performed", stats.health_checks_performed)?;
            dict.set_item("health_check_failures", stats.health_check_failures)?;
            
            Ok(dict.into())
        })
    }

    pub fn shutdown(&self) -> PyResult<()> {
        *self.shutdown.write() = true;
        Ok(())
    }
}

impl ConnectionPool {
    fn start_maintenance_tasks(&self) {
        let connections = self.connections.clone();
        let config = self.config.clone();
        let stats = self.stats.clone();
        let shutdown = self.shutdown.clone();

        // Idle connection cleanup task
        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(10));
            
            loop {
                interval.tick().await;
                
                if *shutdown.read() {
                    break;
                }

                let mut total_cleaned = 0;
                
                for mut entry in connections.iter_mut() {
                    let host = entry.key();
                    let queue = entry.value();
                    let mut queue = queue.lock().await;
                    
                    // Remove expired connections
                    let mut new_queue = VecDeque::new();
                    while let Some(conn) = queue.pop_front() {
                        if !conn.is_expired(config.max_lifetime, config.idle_timeout) {
                            new_queue.push_back(conn);
                        } else {
                            total_cleaned += 1;
                        }
                    }
                    
                    *queue = new_queue;
                }
                
                if total_cleaned > 0 {
                    let mut stats = stats.write();
                    stats.connections_closed += total_cleaned;
                    stats.idle_connections -= total_cleaned;
                }
            }
        });

        // Health check task
        let connections = self.connections.clone();
        let config = self.config.clone();
        let stats = self.stats.clone();
        let shutdown = self.shutdown.clone();

        tokio::spawn(async move {
            let mut interval = interval(config.health_check_interval);
            
            loop {
                interval.tick().await;
                
                if *shutdown.read() {
                    break;
                }

                for mut entry in connections.iter_mut() {
                    let queue = entry.value();
                    let mut queue = queue.lock().await;
                    
                    for conn in queue.iter_mut() {
                        // Perform health check (simplified)
                        conn.is_healthy = true; // Would actually test the connection
                        
                        let mut stats = stats.write();
                        stats.health_checks_performed += 1;
                    }
                }
            }
        });
    }

    pub async fn acquire(&self, host: &str, port: u16) -> Result<PooledConnection, String> {
        let key = format!("{}:{}", host, port);
        
        // Try to get an existing connection
        if let Some(queue) = self.connections.get(&key) {
            let mut queue = queue.lock().await;
            
            while let Some(mut conn) = queue.pop_front() {
                if !conn.is_expired(self.config.max_lifetime, self.config.idle_timeout) && conn.is_healthy {
                    conn.mark_used();
                    
                    let mut stats = self.stats.write();
                    stats.connections_reused += 1;
                    stats.idle_connections -= 1;
                    stats.active_connections += 1;
                    
                    return Ok(conn);
                }
            }
        }

        // Need to create a new connection
        let _permit = self.semaphore.acquire().await
            .map_err(|e| format!("Failed to acquire semaphore: {}", e))?;

        // Create new connection (simplified - would use actual connection logic)
        let conn = Connection {
            stream: Box::new(tokio::io::empty()),
            remote_addr: format!("{}:{}", host, port).parse().unwrap(),
        };

        let pooled_conn = PooledConnection::new(conn, key.clone());
        
        let mut stats = self.stats.write();
        stats.connections_created += 1;
        stats.total_connections += 1;
        stats.active_connections += 1;

        Ok(pooled_conn)
    }

    pub async fn release(&self, mut conn: PooledConnection) {
        let key = conn.host.clone();
        
        // Check if connection should be kept
        if conn.is_healthy && !conn.is_expired(self.config.max_lifetime, self.config.idle_timeout) {
            let queue = self.connections.entry(key).or_insert_with(|| {
                Arc::new(Mutex::new(VecDeque::new()))
            });
            
            let mut queue = queue.lock().await;
            
            // Only keep if under idle limit
            if queue.len() < self.config.max_idle_connections {
                queue.push_back(conn);
                
                let mut stats = self.stats.write();
                stats.active_connections -= 1;
                stats.idle_connections += 1;
                
                return;
            }
        }
        
        // Connection will be dropped
        let mut stats = self.stats.write();
        stats.active_connections -= 1;
        stats.connections_closed += 1;
    }
}

/// Circuit breaker for connection resilience
pub struct CircuitBreaker {
    failure_threshold: u32,
    success_threshold: u32,
    timeout: Duration,
    state: Arc<RwLock<CircuitState>>,
    failure_count: Arc<RwLock<u32>>,
    success_count: Arc<RwLock<u32>>,
    last_failure_time: Arc<RwLock<Option<Instant>>>,
}

#[derive(Clone, Copy, PartialEq)]
enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

impl CircuitBreaker {
    pub fn new(failure_threshold: u32, success_threshold: u32, timeout: Duration) -> Self {
        Self {
            failure_threshold,
            success_threshold,
            timeout,
            state: Arc::new(RwLock::new(CircuitState::Closed)),
            failure_count: Arc::new(RwLock::new(0)),
            success_count: Arc::new(RwLock::new(0)),
            last_failure_time: Arc::new(RwLock::new(None)),
        }
    }

    pub fn can_proceed(&self) -> bool {
        let state = *self.state.read();
        
        match state {
            CircuitState::Closed => true,
            CircuitState::Open => {
                // Check if timeout has passed
                if let Some(last_failure) = *self.last_failure_time.read() {
                    if Instant::now().duration_since(last_failure) > self.timeout {
                        *self.state.write() = CircuitState::HalfOpen;
                        true
                    } else {
                        false
                    }
                } else {
                    false
                }
            }
            CircuitState::HalfOpen => true,
        }
    }

    pub fn record_success(&self) {
        let state = *self.state.read();
        
        match state {
            CircuitState::HalfOpen => {
                let mut success_count = self.success_count.write();
                *success_count += 1;
                
                if *success_count >= self.success_threshold {
                    *self.state.write() = CircuitState::Closed;
                    *self.failure_count.write() = 0;
                    *success_count = 0;
                }
            }
            _ => {
                *self.failure_count.write() = 0;
            }
        }
    }

    pub fn record_failure(&self) {
        let mut failure_count = self.failure_count.write();
        *failure_count += 1;
        *self.last_failure_time.write() = Some(Instant::now());
        
        if *failure_count >= self.failure_threshold {
            *self.state.write() = CircuitState::Open;
            *self.success_count.write() = 0;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_connection_pool() {
        let pool = ConnectionPool::new(Some(10), Some(5), Some(60));
        
        // Test acquiring connection
        let conn = pool.acquire("example.com", 443).await.unwrap();
        assert_eq!(conn.host, "example.com:443");
        
        // Test releasing connection
        pool.release(conn).await;
        
        // Check stats
        let stats = pool.stats.read();
        assert_eq!(stats.connections_created, 1);
        assert_eq!(stats.idle_connections, 1);
    }

    #[test]
    fn test_circuit_breaker() {
        let cb = CircuitBreaker::new(3, 2, Duration::from_secs(5));
        
        assert!(cb.can_proceed());
        
        // Record failures to open circuit
        cb.record_failure();
        cb.record_failure();
        cb.record_failure();
        
        assert!(!cb.can_proceed());
    }
}