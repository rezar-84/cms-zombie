import os
import re
from pathlib import Path
from typing import Dict, List, Any

class ThemeExtractor:
    """Extracts branding colors, font families, and layout dimensions from WordPress theme stylesheets."""

    COLOR_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")
    FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;]+);", re.IGNORECASE)

    @classmethod
    def extract_from_css(cls, css_text: str) -> Dict[str, Any]:
        # Extract colors and count frequency
        colors = cls.COLOR_HEX_RE.findall(css_text)
        color_counts = {}
        for c in colors:
            c_norm = c.upper()
            if len(c_norm) == 4: # #FFF -> #FFFFFF
                c_norm = "#" + "".join([ch * 2 for ch in c_norm[1:]])
            color_counts[c_norm] = color_counts.get(c_norm, 0) + 1

        # Sort colors by frequency, filtering out pure white and pure black for branding accents
        brand_colors = [c for c, _ in sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
                        if c not in ("#FFFFFF", "#000000", "#111111", "#F5F5F5", "#E5E5E5")]

        primary = brand_colors[0] if len(brand_colors) > 0 else "#10B981"
        secondary = brand_colors[1] if len(brand_colors) > 1 else "#06B6D4"
        accent = brand_colors[2] if len(brand_colors) > 2 else "#F59E0B"

        # Extract font families, checking specifically for heading selectors vs body
        h_match = re.search(r"(?:h1|h2|h3|heading)[^{]*\{[^}]*font-family\s*:\s*([^;]+);", css_text, re.IGNORECASE)
        b_match = re.search(r"(?:body|p|html)[^{]*\{[^}]*font-family\s*:\s*([^;]+);", css_text, re.IGNORECASE)

        font_heading = h_match.group(1).split(",")[0].strip().strip('"').strip("'") if h_match else None
        font_body = b_match.group(1).split(",")[0].strip().strip('"').strip("'") if b_match else None

        # Fallback to general list
        if not font_heading or not font_body:
            fonts = []
            for m in cls.FONT_FAMILY_RE.finditer(css_text):
                font = m.group(1).split(",")[0].strip().strip('"').strip("'")
                if font and font.lower() not in ("inherit", "initial", "sans-serif", "serif", "monospace"):
                    if font not in fonts:
                        fonts.append(font)
            if not font_heading:
                font_heading = fonts[0] if fonts else "ui-sans-serif, system-ui, sans-serif"
            if not font_body:
                font_body = fonts[1] if len(fonts) > 1 else font_heading

        return {
            "colors": {
                "primary": primary,
                "secondary": secondary,
                "accent": accent,
                "surface": "#F8FAFC",
                "text": "#0F172A"
            },
            "fonts": {
                "heading": font_heading,
                "body": font_body
            }
        }

    @classmethod
    def generate_tokens_css(cls, tokens: Dict[str, Any]) -> str:
        colors = tokens.get("colors", {})
        fonts = tokens.get("fonts", {})
        return f""":root {{
  --color-primary: {colors.get('primary', '#10B981')};
  --color-secondary: {colors.get('secondary', '#06B6D4')};
  --color-accent: {colors.get('accent', '#F59E0B')};
  --color-surface: {colors.get('surface', '#F8FAFC')};
  --color-text: {colors.get('text', '#0F172A')};
  --font-heading: {fonts.get('heading', 'sans-serif')};
  --font-body: {fonts.get('body', 'sans-serif')};
}}
"""

    @classmethod
    def find_and_extract(cls, theme_dir: Path) -> Dict[str, Any]:
        theme_dir = Path(theme_dir)
        css_texts = []
        for root, _, files in os.walk(theme_dir):
            for f in files:
                if f.endswith(".css"):
                    p = Path(root) / f
                    try:
                        css_texts.append(p.read_text(encoding="utf-8", errors="ignore"))
                    except Exception:
                        pass
        full_css = "\n".join(css_texts)
        return cls.extract_from_css(full_css)
