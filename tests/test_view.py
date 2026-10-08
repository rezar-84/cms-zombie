import unittest
import tempfile
from pathlib import Path
from cms_zombie.view.collector import StateCollector
from cms_zombie.view.server import ViewServer

class TestView(unittest.TestCase):

    def test_state_collector_and_report_rendering(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            blog_dir = project_path / "src" / "content" / "blog"
            blog_dir.mkdir(parents=True, exist_ok=True)

            # Write synthetic post
            post_md = """---
title: "Dashboard Test Article"
slug: "dashboard-test"
date: "2023-01-01"
---
# Heading
This is article text for testing word count.
"""
            (blog_dir / "dashboard-test.md").write_text(post_md, encoding="utf-8")

            # Collect state
            state = StateCollector.collect(project_path)
            self.assertEqual(state["stats"]["total_content"], 1)
            self.assertEqual(state["stats"]["posts_count"], 1)
            self.assertEqual(state["posts"][0]["title"], "Dashboard Test Article")

            # Render HTML
            html = ViewServer.render_html(project_path)
            self.assertIn("CMS Zombie View", html)
            self.assertIn("Dashboard Test Article", html)

            # Static file generation
            report_file = ViewServer.write_static_report(project_path)
            self.assertTrue(report_file.exists())

if __name__ == "__main__":
    unittest.main()
