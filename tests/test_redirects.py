import unittest
from cms_zombie.seo.redirects import RedirectManager

class TestRedirects(unittest.TestCase):

    def test_redirect_rules_generation(self):
        posts = [
            {"id": 42, "slug": "my-awesome-post", "date": "2022-08-15 10:00:00", "type": "post"},
            {"id": 7, "slug": "about-us", "date": "2021-01-01 00:00:00", "type": "page"}
        ]
        rules = RedirectManager.generate_redirect_rules(posts)
        sources = [r["source"] for r in rules]

        # Post checks
        self.assertIn("/2022/08/my-awesome-post/", sources)
        self.assertIn("/?p=42", sources)

        # Page checks
        self.assertIn("/?p=7", sources)

        # Netlify export check
        netlify = RedirectManager.to_netlify_redirects(rules)
        self.assertIn("301", netlify)

if __name__ == "__main__":
    unittest.main()
