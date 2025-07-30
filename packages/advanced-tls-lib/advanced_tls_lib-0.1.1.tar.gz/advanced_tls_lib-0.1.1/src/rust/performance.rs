use std::sync::Arc;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::time::{Duration, Instant};
use parking_lot::RwLock;

/// Performance monitoring and optimization utilities
pub struct PerformanceMonitor {
    request_count: AtomicU64,
    bytes_sent: AtomicU64,
    bytes_received: AtomicU64,
    connection_count: AtomicUsize,
    error_count: AtomicU64,
    start_time: Instant,
    latencies: Arc<RwLock<Vec<Duration>>>,
}

impl PerformanceMonitor {
    pub fn new() -> Self {
        Self {
            request_count: AtomicU64::new(0),
            bytes_sent: AtomicU64::new(0),
            bytes_received: AtomicU64::new(0),
            connection_count: AtomicUsize::new(0),
            error_count: AtomicU64::new(0),
            start_time: Instant::now(),
            latencies: Arc::new(RwLock::new(Vec::with_capacity(1000))),
        }
    }

    pub fn record_request(&self, bytes_sent: u64, bytes_received: u64, latency: Duration) {
        self.request_count.fetch_add(1, Ordering::Relaxed);
        self.bytes_sent.fetch_add(bytes_sent, Ordering::Relaxed);
        self.bytes_received.fetch_add(bytes_received, Ordering::Relaxed);
        
        let mut latencies = self.latencies.write();
        latencies.push(latency);
        
        // Keep only last 1000 latencies to prevent memory growth
        if latencies.len() > 1000 {
            latencies.remove(0);
        }
    }

    pub fn record_error(&self) {
        self.error_count.fetch_add(1, Ordering::Relaxed);
    }

    pub fn add_connection(&self) {
        self.connection_count.fetch_add(1, Ordering::Relaxed);
    }

    pub fn remove_connection(&self) {
        self.connection_count.fetch_sub(1, Ordering::Relaxed);
    }

    pub fn get_stats(&self) -> PerformanceStats {
        let request_count = self.request_count.load(Ordering::Relaxed);
        let bytes_sent = self.bytes_sent.load(Ordering::Relaxed);
        let bytes_received = self.bytes_received.load(Ordering::Relaxed);
        let connection_count = self.connection_count.load(Ordering::Relaxed);
        let error_count = self.error_count.load(Ordering::Relaxed);
        let uptime = self.start_time.elapsed();
        
        let latencies = self.latencies.read();
        let avg_latency = if !latencies.is_empty() {
            let sum: Duration = latencies.iter().sum();
            sum / latencies.len() as u32
        } else {
            Duration::ZERO
        };
        
        let p99_latency = if !latencies.is_empty() {
            let mut sorted = latencies.clone();
            sorted.sort();
            let idx = (sorted.len() as f64 * 0.99) as usize;
            sorted[idx.min(sorted.len() - 1)]
        } else {
            Duration::ZERO
        };
        
        let requests_per_second = if uptime.as_secs() > 0 {
            request_count as f64 / uptime.as_secs_f64()
        } else {
            0.0
        };
        
        PerformanceStats {
            request_count,
            bytes_sent,
            bytes_received,
            connection_count,
            error_count,
            uptime,
            avg_latency,
            p99_latency,
            requests_per_second,
        }
    }
}

#[derive(Debug, Clone)]
pub struct PerformanceStats {
    pub request_count: u64,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub connection_count: usize,
    pub error_count: u64,
    pub uptime: Duration,
    pub avg_latency: Duration,
    pub p99_latency: Duration,
    pub requests_per_second: f64,
}

/// Memory pool for zero-allocation operations
pub struct MemoryPool<T> {
    pool: Arc<RwLock<Vec<T>>>,
    factory: Arc<dyn Fn() -> T + Send + Sync>,
    max_size: usize,
}

impl<T> MemoryPool<T> {
    pub fn new<F>(max_size: usize, factory: F) -> Self
    where
        F: Fn() -> T + Send + Sync + 'static,
    {
        Self {
            pool: Arc::new(RwLock::new(Vec::with_capacity(max_size))),
            factory: Arc::new(factory),
            max_size,
        }
    }

    pub fn acquire(&self) -> PooledItem<T> {
        let item = {
            let mut pool = self.pool.write();
            pool.pop()
        };

        let item = item.unwrap_or_else(|| (self.factory)());

        PooledItem {
            item: Some(item),
            pool: self.pool.clone(),
            max_size: self.max_size,
        }
    }
}

pub struct PooledItem<T> {
    item: Option<T>,
    pool: Arc<RwLock<Vec<T>>>,
    max_size: usize,
}

impl<T> Drop for PooledItem<T> {
    fn drop(&mut self) {
        if let Some(item) = self.item.take() {
            let mut pool = self.pool.write();
            if pool.len() < self.max_size {
                pool.push(item);
            }
        }
    }
}

impl<T> std::ops::Deref for PooledItem<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        self.item.as_ref().unwrap()
    }
}

impl<T> std::ops::DerefMut for PooledItem<T> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        self.item.as_mut().unwrap()
    }
}

/// Fast ring buffer for streaming data
pub struct RingBuffer {
    buffer: Vec<u8>,
    capacity: usize,
    read_pos: usize,
    write_pos: usize,
    size: usize,
}

impl RingBuffer {
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: vec![0; capacity],
            capacity,
            read_pos: 0,
            write_pos: 0,
            size: 0,
        }
    }

    pub fn write(&mut self, data: &[u8]) -> usize {
        let available = self.capacity - self.size;
        let to_write = data.len().min(available);
        
        for i in 0..to_write {
            self.buffer[self.write_pos] = data[i];
            self.write_pos = (self.write_pos + 1) % self.capacity;
        }
        
        self.size += to_write;
        to_write
    }

    pub fn read(&mut self, buf: &mut [u8]) -> usize {
        let to_read = buf.len().min(self.size);
        
        for i in 0..to_read {
            buf[i] = self.buffer[self.read_pos];
            self.read_pos = (self.read_pos + 1) % self.capacity;
        }
        
        self.size -= to_read;
        to_read
    }

    pub fn available(&self) -> usize {
        self.size
    }

    pub fn capacity(&self) -> usize {
        self.capacity
    }
}

/// CPU affinity optimization
#[cfg(target_os = "linux")]
pub fn set_thread_affinity(cpu_id: usize) -> std::io::Result<()> {
    use std::os::raw::c_int;
    
    extern "C" {
        fn sched_setaffinity(pid: c_int, cpusetsize: usize, mask: *const u64) -> c_int;
    }
    
    let mut cpuset: u64 = 0;
    cpuset |= 1 << cpu_id;
    
    let result = unsafe {
        sched_setaffinity(0, std::mem::size_of::<u64>(), &cpuset as *const u64)
    };
    
    if result == 0 {
        Ok(())
    } else {
        Err(std::io::Error::last_os_error())
    }
}

#[cfg(not(target_os = "linux"))]
pub fn set_thread_affinity(_cpu_id: usize) -> std::io::Result<()> {
    Ok(()) // No-op on non-Linux platforms
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_performance_monitor() {
        let monitor = PerformanceMonitor::new();
        
        monitor.record_request(1024, 2048, Duration::from_millis(50));
        monitor.record_request(512, 1024, Duration::from_millis(100));
        monitor.record_error();
        
        let stats = monitor.get_stats();
        assert_eq!(stats.request_count, 2);
        assert_eq!(stats.bytes_sent, 1536);
        assert_eq!(stats.bytes_received, 3072);
        assert_eq!(stats.error_count, 1);
    }

    #[test]
    fn test_memory_pool() {
        let pool = MemoryPool::new(10, || vec![0u8; 1024]);
        
        let mut item1 = pool.acquire();
        item1[0] = 42;
        assert_eq!(item1[0], 42);
        
        drop(item1);
        
        let item2 = pool.acquire();
        // Should reuse the same allocation
        assert_eq!(item2.capacity(), 1024);
    }

    #[test]
    fn test_ring_buffer() {
        let mut buffer = RingBuffer::new(10);
        
        let written = buffer.write(b"Hello");
        assert_eq!(written, 5);
        assert_eq!(buffer.available(), 5);
        
        let mut read_buf = vec![0; 10];
        let read = buffer.read(&mut read_buf);
        assert_eq!(read, 5);
        assert_eq!(&read_buf[..5], b"Hello");
        
        // Test wrap-around
        buffer.write(b"World123");
        assert_eq!(buffer.available(), 8);
    }
}