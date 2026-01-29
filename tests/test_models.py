"""Tests for data models."""

import pytest
from models import Segment, TranslationResult, ValidationReport


class TestSegment:
    """Tests for the Segment dataclass."""

    def test_segment_creation(self, sample_segment):
        """Test basic segment creation."""
        assert sample_segment.sheet == "UI"
        assert sample_segment.row_idx == 10
        assert sample_segment.key == "welcome_message"
        assert sample_segment.source_text == "Welcome to the game!"
        assert sample_segment.existing_target == ""
        assert sample_segment.donottranslate is False

    def test_needs_translation_empty_source(self):
        """Segment with empty source should not need translation."""
        segment = Segment(sheet="UI", row_idx=1, key="empty", source_text="")
        assert segment.needs_translation() is False

    def test_needs_translation_whitespace_source(self):
        """Segment with whitespace-only source should not need translation."""
        segment = Segment(sheet="UI", row_idx=1, key="whitespace", source_text="   ")
        assert segment.needs_translation() is False

    def test_needs_translation_donottranslate(self, segment_donottranslate):
        """Segment marked donottranslate should not need translation."""
        assert segment_donottranslate.needs_translation() is False

    def test_needs_translation_already_translated(self, segment_already_translated):
        """Segment with existing translation should not need translation."""
        assert segment_already_translated.needs_translation() is False

    def test_needs_translation_valid(self, sample_segment):
        """Valid segment without translation should need translation."""
        assert sample_segment.needs_translation() is True

    def test_needs_translation_with_placeholders(self, segment_with_var):
        """Segment with placeholders should need translation."""
        assert segment_with_var.needs_translation() is True


class TestTranslationResult:
    """Tests for the TranslationResult dataclass."""

    def test_successful_result(self):
        """Test successful translation result."""
        result = TranslationResult(
            key="test_key",
            status="OK",
            translated_text="Texto traduzido",
        )
        assert result.is_successful is True
        assert result.translated_text == "Texto traduzido"

    def test_failed_result_missing_tokens(self):
        """Test failed result with missing tokens."""
        result = TranslationResult(
            key="test_key",
            status="MISSING_TOKENS",
            error_message="Missing: __VAR0__",
        )
        assert result.is_successful is False

    def test_failed_result_out_of_order(self):
        """Test failed result with tokens out of order."""
        result = TranslationResult(
            key="test_key",
            status="TOKENS_OUT_OF_ORDER",
        )
        assert result.is_successful is False

    def test_failed_result_no_translation(self):
        """Test failed result with no translation returned."""
        result = TranslationResult(
            key="test_key",
            status="NO_TRANSLATION",
        )
        assert result.is_successful is False


class TestValidationReport:
    """Tests for the ValidationReport dataclass."""

    def test_valid_report(self):
        """Test valid report with no issues."""
        report = ValidationReport(
            key="test_key",
            source_tokens=["__VAR0__"],
            target_tokens=["__VAR0__"],
        )
        assert report.is_valid is True

    def test_invalid_report_missing_tokens(self):
        """Test invalid report with missing tokens."""
        report = ValidationReport(
            key="test_key",
            source_tokens=["__VAR0__", "__VAR1__"],
            target_tokens=["__VAR0__"],
            missing_tokens=["__VAR1__"],
        )
        assert report.is_valid is False

    def test_invalid_report_out_of_order(self):
        """Test invalid report with tokens out of order."""
        report = ValidationReport(
            key="test_key",
            source_tokens=["__VAR0__", "__VAR1__"],
            target_tokens=["__VAR1__", "__VAR0__"],
            out_of_order=True,
        )
        assert report.is_valid is False

    def test_report_no_tokens(self):
        """Test report with no tokens (plain text)."""
        report = ValidationReport(
            key="test_key",
            source_tokens=[],
            target_tokens=[],
        )
        assert report.is_valid is True
