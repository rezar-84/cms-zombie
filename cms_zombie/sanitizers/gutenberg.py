import re

class GutenbergCleaner:
    """Strips Gutenberg HTML block comments while preserving the inner semantic markup."""

    BLOCK_COMMENT_RE = re.compile(r"<!--\s*/?wp:[a-zA-Z0-9_\-\/]+(?:\s+\{.*?\})?\s*-->", re.DOTALL)

    @classmethod
    def clean(cls, html_content: str) -> str:
        if not html_content:
            return ""
        # Remove block comments
        cleaned = cls.BLOCK_COMMENT_RE.sub("", html_content)
        # Clean consecutive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()
