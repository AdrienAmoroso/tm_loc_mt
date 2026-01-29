"""Tests for PlaceholderManager utility class."""

import pytest
from utils import PlaceholderManager


class TestPlaceholderProtection:
    """Tests for placeholder protection (extraction)."""

    def test_protect_no_placeholders(self):
        """Text without placeholders should remain unchanged."""
        text = "Hello, welcome to the game!"
        protected, token_map = PlaceholderManager.protect(text)
        
        assert protected == text
        assert token_map == {}

    def test_protect_single_variable(self):
        """Single variable placeholder should be tokenized."""
        text = "Hello, {[player]}!"
        protected, token_map = PlaceholderManager.protect(text)
        
        assert protected == "Hello, __VAR0__!"
        assert token_map == {"__VAR0__": "{[player]}"}

    def test_protect_multiple_variables(self):
        """Multiple variables should be tokenized in order."""
        text = "{[player]} has {[coins]} coins and {[gems]} gems."
        protected, token_map = PlaceholderManager.protect(text)
        
        assert "__VAR0__" in protected
        assert "__VAR1__" in protected
        assert "__VAR2__" in protected
        assert len(token_map) == 3
        assert token_map["__VAR0__"] == "{[player]}"
        assert token_map["__VAR1__"] == "{[coins]}"
        assert token_map["__VAR2__"] == "{[gems]}"

    def test_protect_single_tag(self):
        """Single HTML tag should be tokenized."""
        text = "Press <b>Start</b> to begin."
        protected, token_map = PlaceholderManager.protect(text)
        
        assert "__TAG0__" in protected
        assert "__TAG1__" in protected
        assert token_map["__TAG0__"] == "<b>"
        assert token_map["__TAG1__"] == "</b>"

    def test_protect_mixed_placeholders(self):
        """Mixed variables and tags should both be tokenized."""
        text = "<player>{[name]}</player> scored {[points]} points!"
        protected, token_map = PlaceholderManager.protect(text)
        
        # Variables should be VAR, tags should be TAG
        assert "__VAR0__" in protected  # {[name]}
        assert "__VAR1__" in protected  # {[points]}
        assert "__TAG0__" in protected  # <player>
        assert "__TAG1__" in protected  # </player>
        assert len(token_map) == 4

    def test_protect_nested_content(self):
        """Tags with content inside should work correctly."""
        text = "<color=#FF0000>Warning!</color>"
        protected, token_map = PlaceholderManager.protect(text)
        
        assert "Warning!" in protected
        assert "__TAG0__" in protected
        assert "__TAG1__" in protected


class TestPlaceholderRestoration:
    """Tests for placeholder restoration."""

    def test_restore_single_variable(self):
        """Single variable should be restored correctly."""
        protected = "Olá, __VAR0__!"
        token_map = {"__VAR0__": "{[player]}"}
        
        restored = PlaceholderManager.restore(protected, token_map)
        
        assert restored == "Olá, {[player]}!"

    def test_restore_multiple_variables(self):
        """Multiple variables should be restored in correct positions."""
        protected = "__VAR0__ tem __VAR1__ moedas."
        token_map = {
            "__VAR0__": "{[player]}",
            "__VAR1__": "{[coins]}",
        }
        
        restored = PlaceholderManager.restore(protected, token_map)
        
        assert restored == "{[player]} tem {[coins]} moedas."

    def test_restore_mixed_placeholders(self):
        """Mixed variables and tags should all be restored."""
        protected = "__TAG0____VAR0____TAG1__ marcou __VAR1__ pontos!"
        token_map = {
            "__VAR0__": "{[name]}",
            "__VAR1__": "{[points]}",
            "__TAG0__": "<player>",
            "__TAG1__": "</player>",
        }
        
        restored = PlaceholderManager.restore(protected, token_map)
        
        assert restored == "<player>{[name]}</player> marcou {[points]} pontos!"

    def test_restore_empty_map(self):
        """Empty token map should return text unchanged."""
        text = "Plain text without placeholders."
        
        restored = PlaceholderManager.restore(text, {})
        
        assert restored == text

    def test_roundtrip_protection_restoration(self):
        """Protection followed by restoration should return original text."""
        original = "Hello, {[player]}! Press <b>Start</b> to play."
        
        protected, token_map = PlaceholderManager.protect(original)
        restored = PlaceholderManager.restore(protected, token_map)
        
        assert restored == original


class TestTokenExtraction:
    """Tests for token extraction."""

    def test_extract_no_tokens(self):
        """Text without tokens should return empty list."""
        text = "Plain text without any tokens."
        
        tokens = PlaceholderManager.extract_tokens(text)
        
        assert tokens == []

    def test_extract_var_tokens(self):
        """VAR tokens should be extracted."""
        text = "Hello __VAR0__ and __VAR1__!"
        
        tokens = PlaceholderManager.extract_tokens(text)
        
        assert tokens == ["__VAR0__", "__VAR1__"]

    def test_extract_tag_tokens(self):
        """TAG tokens should be extracted."""
        text = "__TAG0__Bold__TAG1__ text."
        
        tokens = PlaceholderManager.extract_tokens(text)
        
        assert tokens == ["__TAG0__", "__TAG1__"]

    def test_extract_mixed_tokens(self):
        """Mixed VAR and TAG tokens should be extracted."""
        text = "__TAG0____VAR0____TAG1__ has __VAR1__."
        
        tokens = PlaceholderManager.extract_tokens(text)
        
        assert "__VAR0__" in tokens
        assert "__VAR1__" in tokens
        assert "__TAG0__" in tokens
        assert "__TAG1__" in tokens


class TestTokenOrder:
    """Tests for token order validation."""

    def test_tokens_in_order_correct(self):
        """Tokens in correct order should return True."""
        text = "__VAR0__ then __VAR1__ then __VAR2__."
        tokens = ["__VAR0__", "__VAR1__", "__VAR2__"]
        
        assert PlaceholderManager.tokens_in_order(text, tokens) is True

    def test_tokens_in_order_wrong(self):
        """Tokens in wrong order should return False."""
        text = "__VAR1__ then __VAR0__ then __VAR2__."
        tokens = ["__VAR0__", "__VAR1__", "__VAR2__"]
        
        assert PlaceholderManager.tokens_in_order(text, tokens) is False

    def test_tokens_in_order_missing(self):
        """Missing token should return False."""
        text = "__VAR0__ then __VAR2__."
        tokens = ["__VAR0__", "__VAR1__", "__VAR2__"]
        
        assert PlaceholderManager.tokens_in_order(text, tokens) is False

    def test_tokens_in_order_empty(self):
        """Empty token list should return True."""
        text = "No tokens here."
        tokens = []
        
        assert PlaceholderManager.tokens_in_order(text, tokens) is True

    def test_tokens_in_order_single(self):
        """Single token should always be in order."""
        text = "Hello __VAR0__!"
        tokens = ["__VAR0__"]
        
        assert PlaceholderManager.tokens_in_order(text, tokens) is True
