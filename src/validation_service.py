"""Validation service for translation quality checks."""

import logging

from models import Segment, ValidationReport
from utils import PlaceholderManager

logger = logging.getLogger(__name__)


class ValidationService:
    """Validates translated text for placeholder preservation and correctness."""

    @staticmethod
    def validate_translation(
        segment: Segment, translated_text: str, placeholder_map: dict
    ) -> ValidationReport:
        """
        Validate that a translation preserves placeholders correctly.

        Returns:
            ValidationReport with status and any issues found
        """
        # Extract tokens from source
        protected_source, _ = PlaceholderManager.protect(segment.source_text)
        source_tokens = PlaceholderManager.extract_tokens(protected_source)

        # Extract tokens from translation
        target_tokens = PlaceholderManager.extract_tokens(translated_text)

        report = ValidationReport(
            key=segment.key,
            source_tokens=source_tokens,
            target_tokens=target_tokens,
        )

        # Check for missing tokens
        missing = [tok for tok in source_tokens if tok not in translated_text]
        if missing:
            report.missing_tokens = missing
            logger.warning(f"[Validation] Missing tokens for key={segment.key}: {missing}")
            return report

        # Check token order
        if source_tokens and not PlaceholderManager.tokens_in_order(translated_text, source_tokens):
            report.out_of_order = True
            logger.warning(f"[Validation] Tokens out of order for key={segment.key}")
            return report

        return report
