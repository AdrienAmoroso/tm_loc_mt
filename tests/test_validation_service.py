"""Tests for ValidationService."""

from validation_service import ValidationService


class TestValidationService:
    """Tests for translation validation."""

    def test_validate_plain_text(self, sample_segment):
        """Plain text without placeholders should validate successfully."""
        translated = "Bem-vindo ao jogo!"

        report = ValidationService.validate_translation(
            segment=sample_segment,
            translated_text=translated,
            placeholder_map={},
        )

        assert report.is_valid is True
        assert report.missing_tokens == []
        assert report.out_of_order is False

    def test_validate_with_preserved_tokens(self, segment_with_var):
        """Translation with all tokens preserved should validate."""
        # Simulate protected text after translation
        translated = "Olá, __VAR0__! Você tem __VAR1__ moedas."
        placeholder_map = {
            "__VAR0__": "{[player_name]}",
            "__VAR1__": "{[coins]}",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_var,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is True

    def test_validate_missing_token(self, segment_with_var):
        """Translation missing a token should fail validation."""
        # Missing __VAR1__ (coins)
        translated = "Olá, __VAR0__! Você tem moedas."
        placeholder_map = {
            "__VAR0__": "{[player_name]}",
            "__VAR1__": "{[coins]}",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_var,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is False
        assert "__VAR1__" in report.missing_tokens

    def test_validate_tokens_out_of_order(self, segment_with_var):
        """Translation with tokens in wrong order should fail."""
        # Tokens swapped: VAR1 before VAR0
        translated = "Você tem __VAR1__ moedas, __VAR0__!"
        placeholder_map = {
            "__VAR0__": "{[player_name]}",
            "__VAR1__": "{[coins]}",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_var,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is False
        assert report.out_of_order is True

    def test_validate_with_tags(self, segment_with_tags):
        """Translation with HTML tags should validate correctly."""
        translated = "Pressione __TAG0__Iniciar__TAG1__ para começar."
        placeholder_map = {
            "__TAG0__": "<b>",
            "__TAG1__": "</b>",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_tags,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is True

    def test_validate_mixed_placeholders(self, segment_with_mixed):
        """Translation with mixed vars and tags should validate."""
        translated = "__TAG0____VAR0____TAG1__ marcou __VAR1__ pontos!"
        placeholder_map = {
            "__VAR0__": "{[player]}",
            "__VAR1__": "{[points]}",
            "__TAG0__": "<player>",
            "__TAG1__": "</player>",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_mixed,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is True

    def test_validate_all_tokens_missing(self, segment_with_var):
        """Translation with all tokens missing should fail."""
        translated = "Olá! Você tem moedas."
        placeholder_map = {
            "__VAR0__": "{[player_name]}",
            "__VAR1__": "{[coins]}",
        }

        report = ValidationService.validate_translation(
            segment=segment_with_var,
            translated_text=translated,
            placeholder_map=placeholder_map,
        )

        assert report.is_valid is False
        assert len(report.missing_tokens) == 2
