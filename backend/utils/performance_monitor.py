import time
import asyncio
import threading
from typing import Dict, List, Optional, Callable
from functools import wraps
import json
import os
from datetime import datetime
from .constants import PERFORMANCE_CONFIG

class PerformanceMonitor:
    """Performance monitoring utility for tracking execution times and bottlenecks"""
    
    def __init__(self, enabled: bool = None):
        self.enabled = enabled if enabled is not None else PERFORMANCE_CONFIG['ENABLE_PERFORMANCE_MONITORING']
        self.start_time = None
        self.step_times = {}
        self.step_counts = {}
        self.memory_usage = {}
        self.errors = []
        self.thread_local = threading.local()
        
    def start(self):
        """Start performance monitoring"""
        if not self.enabled:
            return
            
        self.start_time = time.time()
        self.step_times = {}
        self.step_counts = {}
        self.errors = []
        print(f"[Performance] Monitoring started at {datetime.now()}")
    
    def log_step(self, step_name: str, duration: float = None):
        """Log a step's execution time"""
        if not self.enabled:
            return
            
        if duration is None:
            duration = time.time() - self.start_time if self.start_time else 0
            
        if step_name not in self.step_times:
            self.step_times[step_name] = []
            self.step_counts[step_name] = 0
            
        self.step_times[step_name].append(duration)
        self.step_counts[step_name] += 1
        
        if PERFORMANCE_CONFIG['LOG_PERFORMANCE']:
            print(f"[Performance] {step_name}: {duration:.2f}s (count: {self.step_counts[step_name]})")
    
    def log_error(self, step_name: str, error: Exception):
        """Log an error during execution"""
        if not self.enabled:
            return
            
        self.errors.append({
            'step': step_name,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        print(f"[Performance] Error in {step_name}: {error}")
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        if not self.enabled or not self.start_time:
            return {}
            
        total_time = time.time() - self.start_time
        
        summary = {
            'total_time': total_time,
            'step_times': {},
            'step_counts': self.step_counts,
            'errors': self.errors,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate averages for each step
        for step_name, times in self.step_times.items():
            if times:
                summary['step_times'][step_name] = {
                    'total': sum(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        return summary
    
    def print_summary(self):
        """Print performance summary"""
        if not self.enabled:
            return
            
        summary = self.get_summary()
        if not summary:
            return
            
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)
        print(f"Total Execution Time: {summary['total_time']:.2f}s")
        print(f"Timestamp: {summary['timestamp']}")
        
        if summary['step_times']:
            print("\nStep Breakdown:")
            for step_name, stats in summary['step_times'].items():
                print(f"  {step_name}:")
                print(f"    Total: {stats['total']:.2f}s")
                print(f"    Average: {stats['average']:.2f}s")
                print(f"    Min: {stats['min']:.2f}s")
                print(f"    Max: {stats['max']:.2f}s")
                print(f"    Count: {stats['count']}")
        
        if summary['errors']:
            print(f"\nErrors ({len(summary['errors'])}):")
            for error in summary['errors']:
                print(f"  {error['step']}: {error['error']}")
        
        print("="*50 + "\n")
    
    def save_report(self, filename: str = None):
        """Save performance report to file"""
        if not self.enabled:
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", filename)
        
        try:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(self.get_summary(), f, indent=2, default=str)
            print(f"[Performance] Report saved to {report_path}")
        except Exception as e:
            print(f"[Performance] Failed to save report: {e}")

def monitor_performance(step_name: str = None):
    """Decorator for monitoring function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = getattr(threading.current_thread(), 'performance_monitor', None)
            if not monitor or not monitor.enabled:
                return func(*args, **kwargs)
            
            step = step_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.log_step(step, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.log_step(step, duration)
                monitor.log_error(step, e)
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = getattr(threading.current_thread(), 'performance_monitor', None)
            if not monitor or not monitor.enabled:
                return await func(*args, **kwargs)
            
            step = step_name or func.__name__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.log_step(step, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.log_step(step, duration)
                monitor.log_error(step, e)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator

class PerformanceContext:
    """Context manager for performance monitoring"""
    
    def __init__(self, step_name: str, monitor: PerformanceMonitor = None):
        self.step_name = step_name
        self.monitor = monitor
        self.start_time = None
    
    def __enter__(self):
        if self.monitor and self.monitor.enabled:
            self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.monitor and self.monitor.enabled and self.start_time:
            duration = time.time() - self.start_time
            self.monitor.log_step(self.step_name, duration)
            if exc_type:
                self.monitor.log_error(self.step_name, exc_val)

# Global performance monitor instance
_global_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

def set_performance_monitor(monitor: PerformanceMonitor):
    """Set the global performance monitor instance"""
    global _global_monitor
    _global_monitor = monitor
    threading.current_thread().performance_monitor = monitor 