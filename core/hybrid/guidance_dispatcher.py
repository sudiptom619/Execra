import logging
from datetime import datetime
from typing import Callable, Literal
from pydantic import BaseModel
from plyer import notification

logger = logging.getLogger(__name__)

class GuidanceInstruction(BaseModel):
    instruction: str              
    confidence: float             
    source: list[str]             
    reasoning: str                
    mode: Literal["safe", "expert"]
    step: int                     
    total_steps: int              
    generated_at: datetime

class GuidanceDispatcher:
    """Dispatches GuidanceInstruction objects to all registered output channels."""

    def __init__(self):
        self._channels: list[Callable[[GuidanceInstruction], None]] = []

    def register_channel(self, channel: Callable[[GuidanceInstruction], None]) -> None:
        """Register a callback function to receive dispatched instructions."""
        self._channels.append(channel)

    def dispatch(self, instruction: GuidanceInstruction) -> None:
        """Route instruction to all registered channels and log at INFO level."""

        logger.info(f"Dispatching instruction: {instruction.instruction}")

        for channel in self._channels:
            channel(instruction)

    def dispatch_error_alert(self, message: str, severity: str, confidence: float) -> None:
        """Convenience method to format and dispatch an error alert."""

        error_instruction = GuidanceInstruction(
            instruction=message,
            confidence=confidence,
            source=["error_detector"],
            reasoning=f"Error alert with severity: {severity}",
            mode="safe",
            step=0,
            total_steps=0,
            generated_at=datetime.now()
        )

        self.dispatch(error_instruction)

    def os_notification_channel(self, instruction: GuidanceInstruction) -> None:
        """Built-in channel: sends OS-level desktop notifications."""

        notification.notify(
            title="Execra Guidance",
            message=instruction.instruction,
            timeout=5
        )

# Shared instance 
guidance_dispatcher = GuidanceDispatcher()