"""
Spinner and progress indicator widgets for Kritrima AI CLI.

This module provides various spinner animations and progress indicators for
showing AI thinking states, loading operations, and progress feedback.
"""

import math
import time
from enum import Enum
from typing import List, Optional

from rich.panel import Panel
from rich.text import Text
from textual.containers import Container, Horizontal
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Label

from kritrima_ai.utils.logger import get_logger

logger = get_logger(__name__)


class SpinnerType(Enum):
    """Different types of spinner animations."""

    DOTS = "dots"
    BALL = "ball"
    BOUNCE = "bounce"
    PULSE = "pulse"
    WAVE = "wave"
    ELLIPSIS = "ellipsis"
    CLOCK = "clock"
    ARROW = "arrow"


class ThinkingSpinner(Widget):
    """
    AI thinking spinner with elapsed time display.

    Shows an animated spinner with elapsed time and optional interrupt instructions.
    """

    # Spinner animation patterns
    SPINNER_PATTERNS = {
        SpinnerType.DOTS: ["⢎⠁", "⢎⠁", "⠋⠁", "⠙⠁", "⠸⠁", "⠴⠁", "⠦⠁", "⠧⠁", "⠇⠁", "⠏⠁"],
        SpinnerType.BALL: [
            "( ●    )",
            "(  ●   )",
            "(   ●  )",
            "(    ● )",
            "(     ●)",
            "(    ● )",
            "(   ●  )",
            "(  ●   )",
            "( ●    )",
            "(●     )",
        ],
        SpinnerType.BOUNCE: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        SpinnerType.PULSE: ["◐", "◓", "◑", "◒"],
        SpinnerType.WAVE: ["▁", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃"],
        SpinnerType.ELLIPSIS: ["   ", ".  ", ".. ", "...", " ..", "  .", "   "],
        SpinnerType.CLOCK: [
            "🕐",
            "🕑",
            "🕒",
            "🕓",
            "🕔",
            "🕕",
            "🕖",
            "🕗",
            "🕘",
            "🕙",
            "🕚",
            "🕛",
        ],
        SpinnerType.ARROW: ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    }

    def __init__(
        self,
        spinner_type: SpinnerType = SpinnerType.BALL,
        message: str = "AI is thinking",
        show_elapsed: bool = True,
        show_interrupt: bool = True,
        **kwargs,
    ):
        """
        Initialize thinking spinner.

        Args:
            spinner_type: Type of spinner animation
            message: Message to display
            show_elapsed: Whether to show elapsed time
            show_interrupt: Whether to show interrupt instructions
        """
        super().__init__(**kwargs)
        self.spinner_type = spinner_type
        self.message = message
        self.show_elapsed = show_elapsed
        self.show_interrupt = show_interrupt

        self.start_time = time.time()
        self.current_frame = 0
        self._is_running = False
        self.timer: Optional[Timer] = None

        self.animation_speed = 0.1  # Seconds between frames

    def start(self) -> None:
        """Start the spinner animation."""
        if not self._is_running:
            self._is_running = True
            self.start_time = time.time()
            self.current_frame = 0

            # Start animation timer
            self.timer = self.set_interval(self.animation_speed, self._animate)
            logger.debug("Thinking spinner started")

    def stop(self) -> None:
        """Stop the spinner animation."""
        if self._is_running:
            self._is_running = False
            if self.timer:
                self.timer.stop()
                self.timer = None
            logger.debug("Thinking spinner stopped")

    def _animate(self) -> None:
        """Update animation frame."""
        if self._is_running:
            self.current_frame += 1
            self.refresh()

    def render(self) -> Panel:
        """Render the thinking spinner."""
        pattern = self.SPINNER_PATTERNS[self.spinner_type]
        frame = pattern[self.current_frame % len(pattern)]

        # Calculate elapsed time
        elapsed = time.time() - self.start_time

        content_parts = []

        # Spinner and message
        spinner_text = Text()
        spinner_text.append(frame, style="cyan bold")
        spinner_text.append(f" {self.message}", style="white")
        content_parts.append(spinner_text)

        # Elapsed time
        if self.show_elapsed:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            elapsed_text = Text()
            elapsed_text.append(f"Elapsed: {minutes:02d}:{seconds:02d}", style="dim")
            content_parts.append(elapsed_text)

        # Interrupt instructions
        if self.show_interrupt:
            interrupt_text = Text()
            interrupt_text.append("Press Ctrl+C to interrupt", style="yellow dim")
            content_parts.append(interrupt_text)

        # Combine content
        content = Text("\n").join(content_parts)

        return Panel(
            content, title="[cyan]Thinking[/cyan]", border_style="cyan", padding=(0, 1)
        )


class LoadingSpinner(Widget):
    """
    General-purpose loading spinner.

    Displays a spinner with customizable message and style.
    """

    def __init__(
        self,
        message: str = "Loading...",
        spinner_type: SpinnerType = SpinnerType.DOTS,
        style: str = "blue",
        **kwargs,
    ):
        """
        Initialize loading spinner.

        Args:
            message: Loading message
            spinner_type: Type of spinner animation
            style: Color style for the spinner
        """
        super().__init__(**kwargs)
        self.message = message
        self.spinner_type = spinner_type
        self.style = style

        self.current_frame = 0
        self._is_running = False
        self.timer: Optional[Timer] = None
        self.animation_speed = 0.1

    def start(self) -> None:
        """Start loading animation."""
        if not self._is_running:
            self._is_running = True
            self.current_frame = 0
            self.timer = self.set_interval(self.animation_speed, self._animate)

    def stop(self) -> None:
        """Stop loading animation."""
        if self._is_running:
            self._is_running = False
            if self.timer:
                self.timer.stop()
                self.timer = None

    def _animate(self) -> None:
        """Update animation frame."""
        if self._is_running:
            self.current_frame += 1
            self.refresh()

    def render(self) -> Text:
        """Render the loading spinner."""
        pattern = ThinkingSpinner.SPINNER_PATTERNS[self.spinner_type]
        frame = pattern[self.current_frame % len(pattern)]

        result = Text()
        result.append(frame, style=f"{self.style} bold")
        result.append(f" {self.message}", style="white")

        return result


class ProgressSpinner(Container):
    """
    Progress spinner with percentage and optional ETA.

    Shows progress with both a spinner animation and progress information.
    """

    def __init__(
        self,
        total: int = 100,
        message: str = "Processing...",
        show_percentage: bool = True,
        show_eta: bool = False,
        **kwargs,
    ):
        """
        Initialize progress spinner.

        Args:
            total: Total number of items/operations
            message: Progress message
            show_percentage: Whether to show percentage
            show_eta: Whether to show estimated time to completion
        """
        super().__init__(**kwargs)
        self.total = total
        self.message = message
        self.show_percentage = show_percentage
        self.show_eta = show_eta

        self.current_progress = 0
        self.start_time = time.time()

        # Child widgets
        self.spinner = LoadingSpinner(
            message="", spinner_type=SpinnerType.DOTS, style="green"
        )
        self.progress_label = Label("")

    def compose(self):
        """Compose the progress spinner layout."""
        with Horizontal():
            yield self.spinner
            yield self.progress_label

    def start(self) -> None:
        """Start progress tracking."""
        self.start_time = time.time()
        self.current_progress = 0
        self.spinner.start()
        self._update_display()

    def stop(self) -> None:
        """Stop progress tracking."""
        self.spinner.stop()

    def update_progress(self, current: int, message: Optional[str] = None) -> None:
        """
        Update progress.

        Args:
            current: Current progress value
            message: Optional updated message
        """
        self.current_progress = current
        if message:
            self.message = message

        self._update_display()

    def increment(self, amount: int = 1, message: Optional[str] = None) -> None:
        """
        Increment progress.

        Args:
            amount: Amount to increment
            message: Optional updated message
        """
        self.update_progress(self.current_progress + amount, message)

    def _update_display(self) -> None:
        """Update the progress display."""
        parts = [self.message]

        if self.show_percentage:
            percentage = (
                (self.current_progress / self.total) * 100 if self.total > 0 else 0
            )
            parts.append(f"({percentage:.1f}%)")

        if self.show_eta and self.current_progress > 0:
            elapsed = time.time() - self.start_time
            rate = self.current_progress / elapsed
            remaining = self.total - self.current_progress
            eta_seconds = remaining / rate if rate > 0 else 0

            if eta_seconds > 0:
                eta_minutes = int(eta_seconds // 60)
                eta_seconds = int(eta_seconds % 60)
                parts.append(f"ETA: {eta_minutes:02d}:{eta_seconds:02d}")

        self.progress_label.update(" ".join(parts))


class MultiStageSpinner(Container):
    """
    Multi-stage progress spinner for complex operations.

    Shows progress through multiple stages with individual stage progress.
    """

    def __init__(self, stages: List[str], current_stage: int = 0, **kwargs):
        """
        Initialize multi-stage spinner.

        Args:
            stages: List of stage names
            current_stage: Current active stage index
        """
        super().__init__(**kwargs)
        self.stages = stages
        self.current_stage = current_stage
        self.stage_progress = [0] * len(stages)

        # Child widgets
        self.main_spinner = LoadingSpinner(
            message="", spinner_type=SpinnerType.WAVE, style="cyan"
        )
        self.stage_label = Label("")
        self.overall_label = Label("")

    def compose(self):
        """Compose the multi-stage layout."""
        yield self.main_spinner
        yield self.stage_label
        yield self.overall_label

    def start(self) -> None:
        """Start multi-stage progress."""
        self.main_spinner.start()
        self._update_display()

    def stop(self) -> None:
        """Stop multi-stage progress."""
        self.main_spinner.stop()

    def set_stage(self, stage_index: int, message: Optional[str] = None) -> None:
        """
        Set the current active stage.

        Args:
            stage_index: Index of the current stage
            message: Optional custom message for the stage
        """
        if 0 <= stage_index < len(self.stages):
            self.current_stage = stage_index
            if message:
                self.stages[stage_index] = message
            self._update_display()

    def update_stage_progress(
        self, progress: int, stage_index: Optional[int] = None
    ) -> None:
        """
        Update progress for a specific stage.

        Args:
            progress: Progress value (0-100)
            stage_index: Stage to update (defaults to current stage)
        """
        stage_idx = stage_index if stage_index is not None else self.current_stage
        if 0 <= stage_idx < len(self.stage_progress):
            self.stage_progress[stage_idx] = progress
            self._update_display()

    def complete_stage(self, stage_index: Optional[int] = None) -> None:
        """
        Mark a stage as completed.

        Args:
            stage_index: Stage to complete (defaults to current stage)
        """
        stage_idx = stage_index if stage_index is not None else self.current_stage
        if 0 <= stage_idx < len(self.stage_progress):
            self.stage_progress[stage_idx] = 100
            if stage_idx == self.current_stage and stage_idx < len(self.stages) - 1:
                self.current_stage += 1
            self._update_display()

    def _update_display(self) -> None:
        """Update the display."""
        # Current stage info
        current_stage_name = (
            self.stages[self.current_stage]
            if self.current_stage < len(self.stages)
            else "Complete"
        )
        current_progress = (
            self.stage_progress[self.current_stage]
            if self.current_stage < len(self.stage_progress)
            else 100
        )

        stage_text = (
            f"Stage {self.current_stage + 1}/{len(self.stages)}: {current_stage_name}"
        )
        if current_progress > 0:
            stage_text += f" ({current_progress}%)"

        self.stage_label.update(stage_text)

        # Overall progress
        completed_stages = sum(1 for p in self.stage_progress if p >= 100)
        overall_progress = (completed_stages / len(self.stages)) * 100

        overall_text = f"Overall: {overall_progress:.1f}% ({completed_stages}/{len(self.stages)} stages)"
        self.overall_label.update(overall_text)


class PulseSpinner(Widget):
    """
    Pulsing animation for subtle loading indication.

    Uses opacity/brightness changes instead of character rotation.
    """

    def __init__(
        self, text: str = "●", message: str = "", pulse_speed: float = 1.0, **kwargs
    ):
        """
        Initialize pulse spinner.

        Args:
            text: Text/character to pulse
            message: Optional message to display
            pulse_speed: Speed of pulsing (cycles per second)
        """
        super().__init__(**kwargs)
        self.text = text
        self.message = message
        self.pulse_speed = pulse_speed
        self.current_intensity = 0.5
        self._is_running = False
        self.timer: Optional[Timer] = None

    def start(self) -> None:
        """Start pulse animation."""
        if not self._is_running:
            self._is_running = True
            self.timer = self.set_interval(0.1, self._animate)

    def stop(self) -> None:
        """Stop pulse animation."""
        if self._is_running:
            self._is_running = False
            if self.timer:
                self.timer.stop()
                self.timer = None

    def _animate(self) -> None:
        """Update pulse animation."""
        if self._is_running:
            # Simple sine wave for pulsing effect
            self.current_intensity = (math.sin(time.time() * self.pulse_speed) + 1) / 2
            self.refresh()

    def render(self) -> Text:
        """Render the pulsing text."""
        # Calculate pulse intensity using sine wave
        intensity = self.current_intensity

        # Map intensity to brightness levels
        brightness_levels = ["dim", "dim", "", "bold", "bold"]
        brightness_index = int(intensity * (len(brightness_levels) - 1))
        style = brightness_levels[brightness_index]

        result = Text()
        result.append(self.text, style=f"cyan {style}")

        if self.message:
            result.append(f" {self.message}", style="white")

        return result


class StatusSpinner(Container):
    """
    Status spinner with multiple status lines.

    Shows a spinner with multiple status messages that can be updated independently.
    """

    def __init__(self, max_status_lines: int = 5, **kwargs):
        """
        Initialize status spinner.

        Args:
            max_status_lines: Maximum number of status lines to display
        """
        super().__init__(**kwargs)
        self.max_status_lines = max_status_lines
        self.status_messages: List[str] = []

        # Child widgets
        self.spinner = LoadingSpinner(
            message="", spinner_type=SpinnerType.DOTS, style="blue"
        )
        self.status_labels = [Label("") for _ in range(max_status_lines)]

    def compose(self):
        """Compose the status spinner layout."""
        yield self.spinner
        for label in self.status_labels:
            yield label

    def start(self, initial_message: str = "Starting...") -> None:
        """
        Start status spinner.

        Args:
            initial_message: Initial status message
        """
        self.spinner.start()
        self.add_status(initial_message)

    def stop(self) -> None:
        """Stop status spinner."""
        self.spinner.stop()

    def add_status(self, message: str) -> None:
        """
        Add a new status message.

        Args:
            message: Status message to add
        """
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.status_messages.append(formatted_message)

        # Keep only the most recent messages
        if len(self.status_messages) > self.max_status_lines:
            self.status_messages = self.status_messages[-self.max_status_lines :]

        self._update_display()

    def update_last_status(self, message: str) -> None:
        """
        Update the last status message.

        Args:
            message: New message content
        """
        if self.status_messages:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.status_messages[-1] = formatted_message
            self._update_display()

    def clear_status(self) -> None:
        """Clear all status messages."""
        self.status_messages.clear()
        self._update_display()

    def _update_display(self) -> None:
        """Update the status display."""
        # Clear all labels first
        for label in self.status_labels:
            label.update("")

        # Update labels with current messages
        for i, message in enumerate(self.status_messages):
            if i < len(self.status_labels):
                # Apply fade effect to older messages
                if i == len(self.status_messages) - 1:
                    style = "white"  # Latest message
                elif i == len(self.status_messages) - 2:
                    style = "bright_black"  # Second latest
                else:
                    style = "dim"  # Older messages

                self.status_labels[i].update(f"[{style}]{message}[/{style}]")


# Convenience functions for creating common spinners
def create_thinking_spinner(
    message: str = "AI is thinking", spinner_type: SpinnerType = SpinnerType.BALL
) -> ThinkingSpinner:
    """
    Create a thinking spinner with common settings.

    Args:
        message: Thinking message
        spinner_type: Type of spinner animation

    Returns:
        Configured ThinkingSpinner instance
    """
    return ThinkingSpinner(
        spinner_type=spinner_type,
        message=message,
        show_elapsed=True,
        show_interrupt=True,
    )


def create_loading_spinner(
    message: str = "Loading...", style: str = "blue"
) -> LoadingSpinner:
    """
    Create a simple loading spinner.

    Args:
        message: Loading message
        style: Color style

    Returns:
        Configured LoadingSpinner instance
    """
    return LoadingSpinner(message=message, spinner_type=SpinnerType.DOTS, style=style)


def create_progress_spinner(
    total: int, message: str = "Processing..."
) -> ProgressSpinner:
    """
    Create a progress spinner.

    Args:
        total: Total number of items
        message: Progress message

    Returns:
        Configured ProgressSpinner instance
    """
    return ProgressSpinner(
        total=total, message=message, show_percentage=True, show_eta=True
    )
