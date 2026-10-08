import re

class ShortcodeCleaner:
    """Strips and normalizes legacy visual page builders and WordPress shortcodes.
    Handles Elementor, Divi (et_pb_*), WPBakery / Visual Composer (vc_*), and standard WP shortcodes.
    """

    # Builder wrappers that enclose content we want to keep
    CONTENT_WRAPPERS = [
        "vc_row", "vc_column", "vc_column_text", "vc_section",
        "et_pb_section", "et_pb_row", "et_pb_column", "et_pb_text",
        "fusion_builder_container", "fusion_builder_row", "fusion_builder_column", "fusion_text",
        "elementor-element"
    ]

    # Standalone widget shortcodes that should either be removed or converted
    REMOVE_SHORTCODES = [
        "contact-form-7", "rev_slider", "layerslider", "vc_empty_space",
        "vc_separator", "et_pb_divider", "et_pb_button", "wp_bigname"
    ]

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        res = text

        # 1. Strip unwanted standalone shortcodes: [code attr="val"] or [code]
        for sc in cls.REMOVE_SHORTCODES:
            pattern = re.compile(rf"\[{sc}[^\]]*\]", re.IGNORECASE)
            res = pattern.sub("", res)

        # 2. Strip wrapper opening and closing tags, leaving inner content intact
        for sc in cls.CONTENT_WRAPPERS:
            open_pat = re.compile(rf"\[{sc}[^\]]*\]", re.IGNORECASE)
            close_pat = re.compile(rf"\[/{sc}\]", re.IGNORECASE)
            res = open_pat.sub("", res)
            res = close_pat.sub("", res)

        # 3. Clean any remaining general self-closing or empty shortcodes [any_tag]
        # preserving markdown bracket links like [link text](url)
        # A shortcode starts with a word, followed optionally by spaces/attributes, closed by ]
        general_sc_pat = re.compile(r"\[([a-zA-Z0-9_\-]+)(?:\s+[^\]]*)?\](.*?)\[/\1\]", re.DOTALL)
        # Expand double shortcodes to inner content
        for _ in range(3): # handle nesting
            res = general_sc_pat.sub(r"\2", res)

        # Strip remaining isolated single tags [tag attr="..."]
        single_sc_pat = re.compile(r"\[[a-zA-Z0-9_\-]+(?:\s+[^\]]*)?/?\]")
        # Ensure we don't accidentally match markdown tasks [ ] or [x]
        def remove_if_not_task(match):
            m = match.group(0)
            if m in ("[ ]", "[x]", "[X]"):
                return m
            return ""

        res = single_sc_pat.sub(remove_if_not_task, res)

        # Normalize whitespace
        res = re.sub(r"\n{3,}", "\n\n", res)
        return res.strip()
