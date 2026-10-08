import unittest
import tempfile
from pathlib import Path
from cms_zombie.generators.nextjs import NextJsScaffolder
from cms_zombie.generators.astro import AstroScaffolder

class TestPathways(unittest.TestCase):

    def test_nextjs_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            posts = [{"title": "Hello Next", "slug": "hello-next", "type": "post", "content": "<p>Content</p>"}]
            redirects = {"/old-slug/": "/hello-next"}

            NextJsScaffolder.scaffold(target, "My Next App", posts, redirects)

            self.assertTrue((target / "package.json").exists())
            self.assertTrue((target / "next.config.js").exists())
            self.assertTrue((target / "src" / "app" / "layout.tsx").exists())
            self.assertTrue((target / "content" / "blog" / "hello-next.md").exists())

    def test_headless_decap_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            posts = [{"title": "Hello Decap", "slug": "hello-decap", "type": "post", "content": "<p>Content</p>"}]
            redirects = {}

            AstroScaffolder.scaffold(target, "My Headless App", posts, redirects, enable_headless=True)

            self.assertTrue((target / "public" / "admin" / "index.html").exists())
            self.assertTrue((target / "public" / "admin" / "config.yml").exists())

if __name__ == "__main__":
    unittest.main()
