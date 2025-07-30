"""
Sophisticated async logging system for Kritrima AI CLI.

This module provides a comprehensive logging infrastructure with:
- Async logging with queue-based processing
- Platform-specific log file locations
- Performance monitoring and timing
- FPS (Frames Per Second) debugging capabilities
- Rich console output formatting
- Memory usage tracking
- Log rotation and compression
"""

import asyncio
import logging
import logging.handlers
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, ContextManager, Dict, Optional

import platformdirs
from rich.console import Console
from rich.logging import RichHandler

# Global logger instances
_loggers: Dict[str, logging.Logger] = {}
_log_queue: Optional[asyncio.Queue] = None
_log_processor_task: Optional[asyncio.Task] = None
_shutdown_event: Optional[asyncio.Event] = None
_performance_timers: Dict[str, float] = {}
_fps_counter = {"frames": 0, "start_time": time.time()}

console = Console()


@dataclass
class LogConfig:
    """Logging configuration."""

    level: str = "INFO"
    file_logging: bool = True
    console_logging: bool = False
    max_file_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    async_logging: bool = True
    performance_logging: bool = True


def get_log_directory() -> Path:
    """Get platform-specific log directory."""
    log_dir = Path(platformdirs.user_log_dir("kritrima-ai"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    debug: bool = False,
    verbose: bool = False,
    file_logging: bool = True,
    console_logging: bool = False,
) -> None:
    """
    Setup the logging system.

    Args:
        debug: Enable debug logging
        verbose: Enable verbose logging
        file_logging: Enable file logging
        console_logging: Enable console logging
    """
    global _log_queue, _log_processor_task, _shutdown_event

    # Determine log level
    if debug:
        level = "DEBUG"
    elif verbose:
        level = "INFO"
    else:
        level = "WARNING"

    config = LogConfig(
        level=level,
        file_logging=file_logging,
        console_logging=console_logging or debug,
        async_logging=True,
        performance_logging=debug,
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Setup file logging
    if config.file_logging:
        log_dir = get_log_directory()
        log_file = log_dir / "kritrima-ai.log"

        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding="utf-8",
        )

        file_formatter = logging.Formatter(config.format_string)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Setup console logging
    if config.console_logging:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=debug,
            rich_tracebacks=True,
        )
        console_handler.setLevel(getattr(logging, config.level))
        root_logger.addHandler(console_handler)

    # Setup async logging
    if config.async_logging:
        _log_queue = asyncio.Queue()
        _shutdown_event = asyncio.Event()

        try:
            loop = asyncio.get_running_loop()
            _log_processor_task = loop.create_task(_process_log_queue())
        except RuntimeError:
            # No running loop, will be started later
            pass

    # Setup performance logging
    if config.performance_logging:
        setup_performance_logging()

    logger = get_logger(__name__)
    logger.info(f"Logging system initialized - Level: {config.level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger

    return _loggers[name]


async def _process_log_queue() -> None:
    """Process log messages from the async queue."""
    while True:
        try:
            # Wait for either a log record or shutdown event
            log_task = asyncio.create_task(_log_queue.get())
            shutdown_task = asyncio.create_task(_shutdown_event.wait())

            done, pending = await asyncio.wait(
                [log_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()

            # Check if shutdown was requested
            if shutdown_task in done:
                # Process remaining logs
                while not _log_queue.empty():
                    try:
                        record = _log_queue.get_nowait()
                        _process_log_record(record)
                    except asyncio.QueueEmpty:
                        break
                break

            # Process the log record
            if log_task in done:
                record = await log_task
                _process_log_record(record)
                _log_queue.task_done()

        except Exception as e:
            # Fallback to stderr for logging errors
            print(f"Error in log processor: {e}", file=sys.stderr)


def _process_log_record(record: logging.LogRecord) -> None:
    """Process a single log record."""
    try:
        logger = logging.getLogger(record.name)
        logger.handle(record)
    except Exception as e:
        print(f"Error processing log record: {e}", file=sys.stderr)


async def log_async(
    logger: logging.Logger, level: int, message: str, *args, **kwargs
) -> None:
    """
    Log a message asynchronously.

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        *args: Message formatting arguments
        **kwargs: Additional logging arguments
    """
    if _log_queue is None:
        # Fallback to synchronous logging
        logger.log(level, message, *args, **kwargs)
        return

    # Create log record
    record = logger.makeRecord(logger.name, level, "", 0, message, args, None, **kwargs)

    try:
        await _log_queue.put(record)
    except Exception:
        # Fallback to synchronous logging
        logger.log(level, message, *args, **kwargs)


def setup_performance_logging() -> None:
    """Setup performance monitoring logging."""
    global _fps_counter
    _fps_counter = {"frames": 0, "start_time": time.time()}


@contextmanager
def performance_timer(
    operation: str, logger: Optional[logging.Logger] = None
) -> ContextManager[None]:
    """
    Context manager for timing operations.

    Args:
        operation: Name of the operation being timed
        logger: Logger to use for output (optional)

    Example:
        with performance_timer("file_processing", logger):
            process_file()
    """
    start_time = time.time()
    _performance_timers[operation] = start_time

    if logger:
        logger.debug(f"Started timing: {operation}")

    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time

        if operation in _performance_timers:
            del _performance_timers[operation]

        if logger:
            logger.info(f"Performance: {operation} took {duration:.3f}s")

        # Also track in global performance stats
        _track_performance_metric(operation, duration)


def _track_performance_metric(operation: str, duration: float) -> None:
    """Track performance metrics globally."""
    # This could be extended to store metrics in a database or send to monitoring


def log_fps_frame() -> None:
    """Log a frame for FPS calculation."""
    global _fps_counter
    _fps_counter["frames"] += 1


def get_fps() -> float:
    """
    Get current FPS (frames per second).

    Returns:
        Current FPS value
    """
    global _fps_counter
    current_time = time.time()
    elapsed = current_time - _fps_counter["start_time"]

    if elapsed > 0:
        return _fps_counter["frames"] / elapsed
    return 0.0


def reset_fps_counter() -> None:
    """Reset the FPS counter."""
    global _fps_counter
    _fps_counter = {"frames": 0, "start_time": time.time()}


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary with memory usage information
    """
    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
        }
    except ImportError:
        return {"error": "psutil not available"}
    except Exception as e:
        return {"error": str(e)}


def log_system_info(logger: logging.Logger) -> None:
    """
    Log system information for debugging.

    Args:
        logger: Logger to use for output
    """
    import platform

    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"Processor: {platform.processor()}")

    # Memory usage
    memory_info = get_memory_usage()
    if "error" not in memory_info:
        logger.info(
            f"Memory usage: {memory_info['rss_mb']:.1f}MB ({memory_info['percent']:.1f}%)"
        )


async def shutdown_logging() -> None:
    """Shutdown the logging system gracefully."""
    global _log_processor_task, _shutdown_event

    logger = get_logger(__name__)
    logger.info("Shutting down logging system...")

    if _shutdown_event:
        _shutdown_event.set()

    if _log_processor_task:
        try:
            await asyncio.wait_for(_log_processor_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Log processor shutdown timed out")
            _log_processor_task.cancel()

    # Shutdown all loggers
    logging.shutdown()


class AsyncLoggerAdapter:
    """Adapter to provide async logging methods."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message asynchronously."""
        await log_async(self.logger, logging.DEBUG, message, *args, **kwargs)

    async def info(self, message: str, *args, **kwargs) -> None:
        """Log info message asynchronously."""
        await log_async(self.logger, logging.INFO, message, *args, **kwargs)

    async def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message asynchronously."""
        await log_async(self.logger, logging.WARNING, message, *args, **kwargs)

    async def error(self, message: str, *args, **kwargs) -> None:
        """Log error message asynchronously."""
        await log_async(self.logger, logging.ERROR, message, *args, **kwargs)

    async def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message asynchronously."""
        await log_async(self.logger, logging.CRITICAL, message, *args, **kwargs)


def get_async_logger(name: str) -> AsyncLoggerAdapter:
    """
    Get an async logger adapter.

    Args:
        name: Logger name

    Returns:
        AsyncLoggerAdapter instance
    """
    logger = get_logger(name)
    return AsyncLoggerAdapter(logger)


class StructuredLogger:
    """Logger with structured logging capabilities."""

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def log_structured(self, level: int, message: str, **structured_data) -> None:
        """
        Log with structured data.

        Args:
            level: Log level
            message: Log message
            **structured_data: Structured data to include
        """
        extra_data = {
            "structured": structured_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.log(level, message, extra=extra_data)

    def info_structured(self, message: str, **data) -> None:
        """Log info with structured data."""
        self.log_structured(logging.INFO, message, **data)

    def error_structured(self, message: str, **data) -> None:
        """Log error with structured data."""
        self.log_structured(logging.ERROR, message, **data)


def create_performance_logger(name: str) -> StructuredLogger:
    """
    Create a performance-focused structured logger.

    Args:
        name: Logger name

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(f"perf.{name}")


# Performance monitoring decorators
def log_performance(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function performance.

    Args:
        logger: Logger to use (optional)
    """

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            operation_name = f"{func.__module__}.{func.__name__}"
            with performance_timer(operation_name, logger):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            operation_name = f"{func.__module__}.{func.__name__}"
            with performance_timer(operation_name, logger):
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
