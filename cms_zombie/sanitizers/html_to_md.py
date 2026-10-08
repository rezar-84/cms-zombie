import re
from html import unescape
from typing import Dict, Any
from .gutenberg import GutenbergCleaner
from .shortcodes import ShortcodeCleaner

class HtmlToMarkdown:
    """Converts sanitized HTML content into clean Markdown with YAML frontmatter."""

    @classmethod
    def convert_html_elements(cls, html: str) -> str:
        text = html

        # Headings: <h1> to <h6>
        for i in range(6, 0, -1):
            pattern = re.compile(rf"<h{i}[^>]*>(.*?)</h{i}>", re.IGNORECASE | re.DOTALL)
            prefix = "#" * i
            text = pattern.sub(rf"\n\n{prefix} \1\n\n", text)

        # Paragraphs
        text = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\n\1\n\n", text, flags=re.IGNORECASE | re.DOTALL)

        # Strong / Bold
        text = re.sub(r"<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>", r"**\1**", text, flags=re.IGNORECASE | re.DOTALL)

        # Emphasis / Italic
        text = re.sub(r"<(?:em|i)[^>]*>(.*?)</(?:em|i)>", r"*\1*", text, flags=re.IGNORECASE | re.DOTALL)

        # Line breaks
        text = re.sub(r"<br\s*/?>", r"\n", text, flags=re.IGNORECASE)

        # Blockquotes
        text = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>", r"\n\n> \1\n\n", text, flags=re.IGNORECASE | re.DOTALL)

        # Links: <a href="url">text</a> -> [text](url)
        link_pat = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
        text = link_pat.sub(r"[\2](\1)", text)

        # Images: <img src="url" alt="alt" ...> -> ![alt](url)
        def replace_img(match):
            tag = match.group(0)
            src_m = re.search(r'src=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            alt_m = re.search(r'alt=["\']([^"\']*)["\']', tag, re.IGNORECASE)
            src = src_m.group(1) if src_m else ""
            alt = alt_m.group(1) if alt_m else ""
            return f"![{alt}]({src})"

        text = re.sub(r"<img\s+[^>]*>", replace_img, text, flags=re.IGNORECASE)

        # Unordered list items: <li> -> -
        text = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"</?[ou]l[^>]*>", r"\n", text, flags=re.IGNORECASE)

        # Code blocks: <pre><code>...</code></pre>
        text = re.sub(r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", r"\n```\n\1\n```\n", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.IGNORECASE | re.DOTALL)

        # Strip remaining tags
        text = re.sub(r"<[^>]+>", "", text)

        # Unescape HTML entities (&amp;, &quot;, &#8217;, etc.)
        text = unescape(text)

        # Clean multiple spaces and blank lines
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def to_markdown_document(cls, html_body: str, metadata: Dict[str, Any]) -> str:
        # Step 1: Clean Gutenberg
        clean_step1 = GutenbergCleaner.clean(html_body or "")
        # Step 2: Clean Shortcodes
        clean_step2 = ShortcodeCleaner.clean(clean_step1)
        # Step 3: Convert HTML to Markdown
        md_body = cls.convert_html_elements(clean_step2)

        # Step 4: Build YAML Frontmatter
        frontmatter_lines = ["---"]
        for k, v in metadata.items():
            if v is None:
                continue
            if isinstance(v, (list, tuple)):
                if not v:
                    continue
                frontmatter_lines.append(f"{k}:")
                for item in v:
                    safe_item = str(item).replace('"', '\\"')
                    frontmatter_lines.append(f'  - "{safe_item}"')
            elif isinstance(v, bool):
                frontmatter_lines.append(f"{k}: {'true' if v else 'false'}")
            elif isinstance(v, (int, float)):
                frontmatter_lines.append(f"{k}: {v}")
            else:
                clean_str = str(v).replace('"', '\\"').replace("\n", " ").strip()
                frontmatter_lines.append(f'{k}: "{clean_str}"')
        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        return "\n".join(frontmatter_lines) + md_body + "\n"
