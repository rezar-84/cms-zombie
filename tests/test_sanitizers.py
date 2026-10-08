import unittest
from cms_zombie.sanitizers.gutenberg import GutenbergCleaner
from cms_zombie.sanitizers.shortcodes import ShortcodeCleaner
from cms_zombie.sanitizers.html_to_md import HtmlToMarkdown

class TestSanitizers(unittest.TestCase):

    def test_gutenberg_cleaning(self):
        dirty = """<!-- wp:paragraph {"fontSize":"medium"} -->
<p>Hello world from Gutenberg.</p>
<!-- /wp:paragraph -->"""
        clean = GutenbergCleaner.clean(dirty)
        self.assertEqual(clean, "<p>Hello world from Gutenberg.</p>")

    def test_shortcode_cleaning(self):
        dirty = """[vc_row][vc_column][vc_column_text]
<h2>Special Title</h2>
[contact-form-7 id="123" title="Contact"]
<p>Some text here.</p>
[/vc_column_text][/vc_column][/vc_row]"""
        clean = ShortcodeCleaner.clean(dirty)
        self.assertNotIn("[vc_row]", clean)
        self.assertNotIn("contact-form-7", clean)
        self.assertIn("Special Title", clean)
        self.assertIn("Some text here.", clean)

    def test_html_to_markdown_conversion(self):
        html = "<h1>Main Heading</h1><p>This is a <strong>bold</strong> test with a <a href='https://example.com'>link</a>.</p>"
        meta = {"title": "Test Title", "slug": "test-slug"}
        doc = HtmlToMarkdown.to_markdown_document(html, meta)

        self.assertIn('title: "Test Title"', doc)
        self.assertIn('slug: "test-slug"', doc)
        self.assertIn("# Main Heading", doc)
        self.assertIn("**bold**", doc)
        self.assertIn("[link](https://example.com)", doc)

    def test_security_script_stripping_and_image_rewrite(self):
        dirty_html = """
        <p>Real content</p>
        <script>alert('xss');</script>
        <iframe src="evil.com"></iframe>
        <img src="https://oldsite.com/wp-content/uploads/2023/04/photo.jpg" alt="Photo" />
        """
        doc = HtmlToMarkdown.to_markdown_document(dirty_html, {"title": "Secure Post"})
        self.assertNotIn("<script>", doc)
        self.assertNotIn("alert('xss')", doc)
        self.assertNotIn("<iframe", doc)
        self.assertIn("![Photo](/assets/2023/04/photo.jpg)", doc)

if __name__ == "__main__":
    unittest.main()
