import unittest
from cms_zombie.extractors.live_crawler import LiveCrawler

class TestCrawler(unittest.TestCase):

    def test_parse_sitemap(self):
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>https://example.com/blog/my-first-post</loc>
   </url>
   <url>
      <loc>https://example.com/about-us</loc>
   </url>
   <url>
      <loc>https://example.com/logo.png</loc>
   </url>
</urlset>"""
        urls = LiveCrawler.parse_sitemap(sitemap_xml)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://example.com/blog/my-first-post", urls)
        self.assertIn("https://example.com/about-us", urls)
        self.assertNotIn("https://example.com/logo.png", urls)

    def test_extract_article_content(self):
        html = """
        <html>
        <head>
            <title>My Awesome Post - Old WordPress Site</title>
            <meta name="description" content="A great summary of this article">
        </head>
        <body>
            <article>
                <h1>My Awesome Post</h1>
                <p>Here is the content of the article.</p>
            </article>
        </body>
        </html>
        """
        data = LiveCrawler.extract_article_content(html, "https://example.com/posts/my-awesome-post")
        self.assertEqual(data["title"], "My Awesome Post")
        self.assertEqual(data["description"], "A great summary of this article")
        self.assertEqual(data["slug"], "my-awesome-post")
        self.assertIn("Here is the content", data["content"])

if __name__ == "__main__":
    unittest.main()
