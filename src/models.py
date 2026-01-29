"""Data models for the translation pipeline."""

from dataclasses import dataclass, field


@dataclass
class Segment:
    """A single translatable segment from Excel."""

    sheet: str
    row_idx: int
    key: str
    source_text: str
    existing_target: str = ""
    comment: str = ""
    donottranslate: bool = False

    def needs_translation(self) -> bool:
        """Check if this segment should be translated."""
        if not self.source_text or not self.source_text.strip():
            return False
        if self.donottranslate:
            return False
        return not (self.existing_target and self.existing_target.strip())


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    key: str
    status: str  # "OK", "MISSING_TOKENS", "TOKENS_OUT_OF_ORDER", "NO_TRANSLATION"
    translated_text: str = ""
    error_message: str = ""

    @property
    def is_successful(self) -> bool:
        return self.status == "OK"


@dataclass
class ValidationReport:
    """Report of validation checks on translated text."""

    key: str
    source_tokens: list = field(default_factory=list)
    target_tokens: list = field(default_factory=list)
    missing_tokens: list = field(default_factory=list)
    out_of_order: bool = False

    @property
    def is_valid(self) -> bool:
        return not self.missing_tokens and not self.out_of_order
