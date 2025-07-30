"""
Security and resource monitoring for Kritrima AI CLI.

This module provides comprehensive monitoring of system resources,
security events, and anomaly detection to ensure safe operation.
"""

import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from kritrima_ai.config.app_config import AppConfig
from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceUsage:
    """Represents system resource usage at a point in time."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int  # bytes
    disk_usage: Dict[str, float]  # path -> usage percentage
    network_io: Dict[str, int]  # bytes_sent, bytes_recv
    process_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used": self.memory_used,
            "disk_usage": self.disk_usage,
            "network_io": self.network_io,
            "process_count": self.process_count,
        }


@dataclass
class SecurityEvent:
    """Represents a security-related event."""

    timestamp: datetime
    event_type: str
    severity: str  # low, medium, high, critical
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "details": self.details,
            "source": self.source,
        }


class ResourceMonitor:
    """
    Monitors system resource usage and detects anomalies.

    Tracks CPU, memory, disk, and network usage to detect
    potential security issues or resource exhaustion.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize resource monitor.

        Args:
            config: Application configuration
        """
        self.config = config
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._usage_history: deque = deque(maxlen=1000)  # Keep last 1000 readings
        self._callbacks: List[Callable[[ResourceUsage], None]] = []

        # Thresholds for alerts
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 85.0  # %
        self.disk_threshold = 90.0  # %

        # Monitoring interval
        self.monitor_interval = 5.0  # seconds

        logger.info("Resource monitor initialized")

    def start_monitoring(self) -> None:
        """Start resource monitoring in background thread."""
        if self._monitoring:
            logger.warning("Resource monitoring already started")
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info("Resource monitoring started")

    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)

        logger.info("Resource monitoring stopped")

    def add_callback(self, callback: Callable[[ResourceUsage], None]) -> None:
        """Add callback for resource usage updates."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[ResourceUsage], None]) -> None:
        """Remove callback for resource usage updates."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                usage = self._collect_resource_usage()
                self._usage_history.append(usage)

                # Check for threshold violations
                self._check_thresholds(usage)

                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(usage)
                    except Exception as e:
                        logger.error(f"Error in resource monitor callback: {e}")

                time.sleep(self.monitor_interval)

            except Exception as e:
                logger.error(f"Error in resource monitoring loop: {e}")
                time.sleep(self.monitor_interval)

    def _collect_resource_usage(self) -> ResourceUsage:
        """Collect current resource usage."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used

        # Disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = (usage.used / usage.total) * 100
            except (PermissionError, OSError):
                continue

        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
        }

        # Process count
        process_count = len(psutil.pids())

        return ResourceUsage(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used=memory_used,
            disk_usage=disk_usage,
            network_io=network_io,
            process_count=process_count,
        )

    def _check_thresholds(self, usage: ResourceUsage) -> None:
        """Check if usage exceeds thresholds."""
        if usage.cpu_percent > self.cpu_threshold:
            logger.warning(f"High CPU usage: {usage.cpu_percent:.1f}%")

        if usage.memory_percent > self.memory_threshold:
            logger.warning(f"High memory usage: {usage.memory_percent:.1f}%")

        for mount, percent in usage.disk_usage.items():
            if percent > self.disk_threshold:
                logger.warning(f"High disk usage on {mount}: {percent:.1f}%")

    def get_current_usage(self) -> Optional[ResourceUsage]:
        """Get current resource usage."""
        if not self._usage_history:
            return None
        return self._usage_history[-1]

    def get_usage_history(self, minutes: int = 60) -> List[ResourceUsage]:
        """Get resource usage history for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            usage for usage in self._usage_history if usage.timestamp >= cutoff_time
        ]

    def get_usage_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get usage statistics for the last N minutes."""
        history = self.get_usage_history(minutes)
        if not history:
            return {}

        cpu_values = [usage.cpu_percent for usage in history]
        memory_values = [usage.memory_percent for usage in history]

        return {
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
            },
            "sample_count": len(history),
            "time_range_minutes": minutes,
        }


class SecurityMonitor:
    """
    Monitors security events and detects potential threats.

    Tracks file access, command execution, network activity,
    and other security-relevant events.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize security monitor.

        Args:
            config: Application configuration
        """
        self.config = config
        self._events: deque = deque(maxlen=10000)  # Keep last 10000 events
        self._callbacks: List[Callable[[SecurityEvent], None]] = []
        self._event_counts: Dict[str, int] = {}

        # Rate limiting for events
        self._rate_limits: Dict[str, Dict[str, Any]] = {
            "file_access": {"max_per_minute": 100, "window": deque(maxlen=100)},
            "command_execution": {"max_per_minute": 50, "window": deque(maxlen=50)},
            "network_access": {"max_per_minute": 200, "window": deque(maxlen=200)},
        }

        logger.info("Security monitor initialized")

    def log_event(
        self,
        event_type: str,
        description: str,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
    ) -> None:
        """
        Log a security event.

        Args:
            event_type: Type of event
            description: Event description
            severity: Event severity (low, medium, high, critical)
            details: Additional event details
            source: Event source
        """
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            description=description,
            details=details or {},
            source=source,
        )

        self._events.append(event)
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1

        # Check for rate limiting
        if self._check_rate_limit(event_type):
            logger.warning(f"Rate limit exceeded for event type: {event_type}")
            self.log_event(
                "rate_limit_exceeded",
                f"Rate limit exceeded for {event_type}",
                "high",
                {"original_event_type": event_type},
            )

        # Log based on severity
        if severity == "critical":
            logger.critical(f"Security event: {description}")
        elif severity == "high":
            logger.error(f"Security event: {description}")
        elif severity == "medium":
            logger.warning(f"Security event: {description}")
        else:
            logger.info(f"Security event: {description}")

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in security monitor callback: {e}")

    def _check_rate_limit(self, event_type: str) -> bool:
        """Check if event type is being rate limited."""
        if event_type not in self._rate_limits:
            return False

        rate_limit = self._rate_limits[event_type]
        window = rate_limit["window"]
        max_per_minute = rate_limit["max_per_minute"]

        now = datetime.now()
        window.append(now)

        # Count events in the last minute
        cutoff = now - timedelta(minutes=1)
        recent_events = sum(1 for timestamp in window if timestamp >= cutoff)

        return recent_events > max_per_minute

    def add_callback(self, callback: Callable[[SecurityEvent], None]) -> None:
        """Add callback for security events."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[SecurityEvent], None]) -> None:
        """Remove callback for security events."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        hours: int = 24,
    ) -> List[SecurityEvent]:
        """
        Get security events matching criteria.

        Args:
            event_type: Filter by event type
            severity: Filter by severity
            hours: Hours of history to include

        Returns:
            List of matching events
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        events = [event for event in self._events if event.timestamp >= cutoff_time]

        if event_type:
            events = [event for event in events if event.event_type == event_type]

        if severity:
            events = [event for event in events if event.severity == severity]

        return events

    def get_event_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get security event statistics."""
        events = self.get_events(hours=hours)

        if not events:
            return {"total_events": 0}

        # Count by type
        type_counts = {}
        for event in events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1

        # Count by severity
        severity_counts = {}
        for event in events:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1

        return {
            "total_events": len(events),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "time_range_hours": hours,
        }

    def detect_anomalies(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in security events."""
        events = self.get_events(hours=hours)
        anomalies = []

        # Check for unusual event frequency
        type_counts = {}
        for event in events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1

        # Define normal ranges (these could be learned from historical data)
        normal_ranges = {
            "file_access": (0, 1000),
            "command_execution": (0, 500),
            "network_access": (0, 200),
            "approval_request": (0, 100),
        }

        for event_type, count in type_counts.items():
            if event_type in normal_ranges:
                min_normal, max_normal = normal_ranges[event_type]
                if count > max_normal:
                    anomalies.append(
                        {
                            "type": "high_event_frequency",
                            "event_type": event_type,
                            "count": count,
                            "normal_max": max_normal,
                            "severity": "medium",
                        }
                    )

        # Check for rapid succession of high-severity events
        high_severity_events = [e for e in events if e.severity in ["high", "critical"]]
        if len(high_severity_events) > 10:
            # Check if they occurred within a short time window
            time_windows = []
            for i in range(len(high_severity_events) - 4):
                window_events = high_severity_events[i : i + 5]
                time_span = window_events[-1].timestamp - window_events[0].timestamp
                if time_span.total_seconds() < 300:  # 5 minutes
                    time_windows.append(
                        {
                            "start": window_events[0].timestamp,
                            "end": window_events[-1].timestamp,
                            "event_count": 5,
                        }
                    )

            if time_windows:
                anomalies.append(
                    {
                        "type": "rapid_high_severity_events",
                        "windows": time_windows,
                        "severity": "high",
                    }
                )

        return anomalies

    def export_events(self, file_path: Path, hours: int = 24) -> None:
        """Export security events to file."""
        events = self.get_events(hours=hours)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "total_events": len(events),
            "events": [event.to_dict() for event in events],
        }

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported {len(events)} security events to {file_path}")

    def clear_old_events(self, days: int = 30) -> int:
        """Clear events older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=days)

        original_count = len(self._events)
        self._events = deque(
            (event for event in self._events if event.timestamp >= cutoff_time),
            maxlen=self._events.maxlen,
        )

        cleared_count = original_count - len(self._events)
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} old security events")

        return cleared_count
