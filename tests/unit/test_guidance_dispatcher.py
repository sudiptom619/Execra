import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from core.hybrid.guidance_dispatcher import GuidanceDispatcher, GuidanceInstruction


@pytest.fixture
def dispatcher():
    """Fresh dispatcher for each test."""
    return GuidanceDispatcher()


@pytest.fixture
def sample_instruction():
    """Sample GuidanceInstruction for testing."""
    return GuidanceInstruction(
        instruction="Add a null check on line 42",
        confidence=0.87,
        source=["llm", "rule_engine"],
        reasoning="Variable could be None",
        mode="safe",
        step=4,
        total_steps=9,
        generated_at=datetime.now()
    )

def test_register_channel_adds_to_list(dispatcher):
    def my_channel(instruction):
        pass

    dispatcher.register_channel(my_channel)
    assert len(dispatcher._channels) == 1
    assert dispatcher._channels[0] == my_channel

def test_dispatch_calls_all_channels(dispatcher, sample_instruction):
    mock_channel = MagicMock()
    dispatcher.register_channel(mock_channel)

    dispatcher.dispatch(sample_instruction)

    mock_channel.assert_called_once_with(sample_instruction)

def test_dispatch_calls_multiple_channels(dispatcher, sample_instruction):
    channel_one = MagicMock()
    channel_two = MagicMock()

    dispatcher.register_channel(channel_one)
    dispatcher.register_channel(channel_two)

    dispatcher.dispatch(sample_instruction)

    channel_one.assert_called_once_with(sample_instruction)
    channel_two.assert_called_once_with(sample_instruction)

def test_dispatch_with_no_channels_no_error(dispatcher, sample_instruction):

    dispatcher.dispatch(sample_instruction)


def test_dispatch_error_alert_calls_channels(dispatcher):
    mock_channel = MagicMock()
    dispatcher.register_channel(mock_channel)

    dispatcher.dispatch_error_alert(
        message="Infinite loop detected",
        severity="high",
        confidence=0.95
    )

    mock_channel.assert_called_once()

    instruction = mock_channel.call_args[0][0]
    assert instruction.instruction == "Infinite loop detected"
    assert instruction.confidence == 0.95
    assert "high" in instruction.reasoning


def test_os_notification_channel_calls_plyer(dispatcher, sample_instruction):
    with patch("core.hybrid.guidance_dispatcher.notification") as mock_notification:
        dispatcher.os_notification_channel(sample_instruction)

        mock_notification.notify.assert_called_once()

        call_kwargs = mock_notification.notify.call_args.kwargs
        assert call_kwargs["title"] == "Execra Guidance"
        assert call_kwargs["message"] == sample_instruction.instruction