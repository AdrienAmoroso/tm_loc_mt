"""Utility functions for placeholder handling and text processing."""

import re


class PlaceholderManager:
    """Manages protection and restoration of placeholder tokens in text."""

    PLACEHOLDER_PATTERN_TAG = re.compile(r"<[^>]+>")
    PLACEHOLDER_PATTERN_VAR = re.compile(r"{\[[^}]+\]}")
    TOKEN_PATTERN = re.compile(r"__(?:VAR|TAG)\d+__")

    @staticmethod
    def protect(text: str) -> tuple[str, dict[str, str]]:
        """
        Replace placeholders with safe tokens.

        Returns:
            Tuple of (protected_text, token_to_original_map)
        """
        placeholder_map: dict[str, str] = {}

        def replace_with_tokens(pattern, prefix, input_text):
            matches = list(pattern.finditer(input_text))
            if not matches:
                return input_text

            out = []
            last = 0
            for i, m in enumerate(matches):
                out.append(input_text[last : m.start()])
                original = m.group(0)
                token = f"__{prefix}{i}__"
                placeholder_map[token] = original
                out.append(token)
                last = m.end()
            out.append(input_text[last:])
            return "".join(out)

        protected = replace_with_tokens(PlaceholderManager.PLACEHOLDER_PATTERN_VAR, "VAR", text)
        protected = replace_with_tokens(
            PlaceholderManager.PLACEHOLDER_PATTERN_TAG, "TAG", protected
        )
        return protected, placeholder_map

    @staticmethod
    def restore(text: str, placeholder_map: dict[str, str]) -> str:
        """Restore original placeholders from tokens."""
        restored = text
        # Sort tokens to ensure deterministic replacement order
        for token in sorted(placeholder_map.keys()):
            original = placeholder_map[token]
            restored = restored.replace(token, original)
        return restored

    @staticmethod
    def extract_tokens(text: str) -> list:
        """Extract all placeholder tokens from text."""
        return PlaceholderManager.TOKEN_PATTERN.findall(text)

    @staticmethod
    def tokens_in_order(text: str, tokens: list) -> bool:
        """Check if tokens appear in the same order in text."""
        pos = -1
        for token in tokens:
            new_pos = text.find(token, pos + 1)
            if new_pos == -1:
                return False
            pos = new_pos
        return True
