import unittest
from cms_zombie.theme.tokens import ThemeExtractor

class TestTheme(unittest.TestCase):

    def test_extract_colors_and_fonts(self):
        sample_css = """
        body {
            font-family: 'Inter', sans-serif;
            color: #333333;
            background: #FFFFFF;
        }
        h1, h2, h3 {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #10B981;
        }
        .btn-primary {
            background-color: #10B981;
            border-color: #059669;
        }
        .btn-secondary {
            background-color: #06B6D4;
        }
        """
        tokens = ThemeExtractor.extract_from_css(sample_css)
        self.assertIn("#10B981", [tokens["colors"]["primary"], tokens["colors"]["secondary"]])
        self.assertEqual(tokens["fonts"]["heading"], "Plus Jakarta Sans")
        self.assertEqual(tokens["fonts"]["body"], "Inter")

        css = ThemeExtractor.generate_tokens_css(tokens)
        self.assertIn("--color-primary:", css)
        self.assertIn("--font-heading:", css)

if __name__ == "__main__":
    unittest.main()
