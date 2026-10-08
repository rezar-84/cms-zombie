import unittest
import tempfile
import json
from pathlib import Path
from cms_zombie.generators.custom_cms import CustomCmsScaffolder

class TestCustomCmsGenerator(unittest.TestCase):

    def test_custom_cms_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            sample_posts = [
                {
                    "id": "1",
                    "slug": "hello-world",
                    "title": "Hello World",
                    "content": "<p>Welcome to our modern decoupled blog platform.</p>",
                    "date": "2026-01-01 12:00:00",
                    "categories": ["Engineering", "Product"],
                    "tags": ["cms", "modernization"]
                },
                {
                    "id": "2",
                    "slug": "second-post",
                    "title": "Second Article",
                    "content": "<p>A detailed article exploring edge static generation and dynamic APIs.</p>",
                    "date": "2026-01-02 15:30:00",
                    "categories": ["Architecture"],
                    "tags": ["typescript", "fullstack"]
                }
            ]
            redirects = {"/old-hello": "/blog/hello-world"}

            success = CustomCmsScaffolder.scaffold(
                target_dir=target,
                project_name="Modern Enterprise Hub",
                posts=sample_posts,
                redirects=redirects
            )

            self.assertTrue(success)
            self.assertTrue((target / "package.json").exists())
            self.assertTrue((target / "vite.config.ts").exists())
            self.assertTrue((target / "tailwind.config.js").exists())

            # Static JSON Catalog & Payloads
            index_json_path = target / "public" / "blog" / "index.json"
            self.assertTrue(index_json_path.exists())
            index_data = json.loads(index_json_path.read_text(encoding="utf-8"))
            self.assertEqual(len(index_data), 2)
            self.assertEqual(index_data[0]["slug"], "hello-world")
            self.assertGreaterEqual(index_data[0]["readingMinutes"], 1)

            post_json_path = target / "public" / "blog" / "hello-world.json"
            self.assertTrue(post_json_path.exists())
            post_data = json.loads(post_json_path.read_text(encoding="utf-8"))
            self.assertEqual(post_data["title"], "Hello World")
            self.assertIn("<p>Welcome to our modern decoupled blog platform.</p>", post_data["bodyHtml"])

            # Hybrid API client
            api_client_path = target / "src" / "lib" / "blog-api.ts"
            self.assertTrue(api_client_path.exists())
            api_client_code = api_client_path.read_text(encoding="utf-8")
            self.assertIn("fetchArticles", api_client_code)
            self.assertIn("fetchArticleBySlug", api_client_code)

            # Multi-mode Admin Editor
            editor_path = target / "src" / "components" / "admin" / "ArticleEditor.tsx"
            self.assertTrue(editor_path.exists())
            editor_code = editor_path.read_text(encoding="utf-8")
            self.assertIn("EditorMode", editor_code)
            self.assertIn("visual", editor_code)
            self.assertIn("split", editor_code)
            self.assertIn("DOMPurify", editor_code)

            # Reader UI
            self.assertTrue((target / "src" / "pages" / "BlogList.tsx").exists())
            self.assertTrue((target / "src" / "pages" / "ArticleDetail.tsx").exists())

            # Database Schema & Seed
            schema_path = target / "prisma" / "schema.prisma"
            self.assertTrue(schema_path.exists())
            self.assertIn("model Article", schema_path.read_text(encoding="utf-8"))

            seed_path = target / "prisma" / "seed.ts"
            self.assertTrue(seed_path.exists())
            seed_code = seed_path.read_text(encoding="utf-8")
            self.assertIn("PrismaClient", seed_code)
            self.assertIn("hello-world", seed_code)

if __name__ == "__main__":
    unittest.main()
