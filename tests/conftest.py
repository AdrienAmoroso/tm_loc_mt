"""Pytest fixtures for translation tool tests."""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Segment


@pytest.fixture
def sample_segment():
    """Basic segment without placeholders."""
    return Segment(
        sheet="UI",
        row_idx=10,
        key="welcome_message",
        source_text="Welcome to the game!",
    )


@pytest.fixture
def segment_with_var():
    """Segment with variable placeholder."""
    return Segment(
        sheet="UI",
        row_idx=20,
        key="player_greeting",
        source_text="Hello, {[player_name]}! You have {[coins]} coins.",
    )


@pytest.fixture
def segment_with_tags():
    """Segment with HTML-like tags."""
    return Segment(
        sheet="UI",
        row_idx=30,
        key="bold_text",
        source_text="Press <b>Start</b> to begin.",
    )


@pytest.fixture
def segment_with_mixed():
    """Segment with both variables and tags."""
    return Segment(
        sheet="Match",
        row_idx=40,
        key="match_score",
        source_text="<player>{[player]}</player> scored {[points]} points!",
    )


@pytest.fixture
def segment_donottranslate():
    """Segment marked as do not translate."""
    return Segment(
        sheet="UI",
        row_idx=50,
        key="brand_name",
        source_text="Tennis Manager 2025",
        donottranslate=True,
    )


@pytest.fixture
def segment_already_translated():
    """Segment that already has a translation."""
    return Segment(
        sheet="UI",
        row_idx=60,
        key="hello",
        source_text="Hello",
        existing_target="Olá",
    )
