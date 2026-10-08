import unittest
from cms_zombie.extractors.wordpress_sql import WordPressSqlParser

class TestWordPressSql(unittest.TestCase):

    def test_parse_sql_values(self):
        row_sql = "(1, 'Hello World', NULL, 42, 'escaped \\'quote\\' test')"
        vals = WordPressSqlParser.parse_sql_values(row_sql)
        self.assertEqual(vals[0], 1)
        self.assertEqual(vals[1], "Hello World")
        self.assertIsNone(vals[2])
        self.assertEqual(vals[3], 42)
        self.assertIn("escaped 'quote' test", vals[4])

    def test_parse_posts(self):
        sample_sql = """
INSERT INTO `wp_posts` (`ID`, `post_author`, `post_date`, `post_date_gmt`, `post_content`, `post_title`, `post_excerpt`, `post_status`, `comment_status`, `ping_status`, `post_password`, `post_name`, `to_ping`, `pinged`, `post_modified`, `post_modified_gmt`, `post_content_filtered`, `post_parent`, `guid`, `menu_order`, `post_type`, `post_mime_type`, `comment_count`) VALUES
(10, 1, '2023-05-10 12:00:00', '2023-05-10 12:00:00', '<p>Sample blog post content</p>', 'First Post', '', 'publish', 'open', 'open', '', 'first-post', '', '', '2023-05-10 12:00:00', '2023-05-10 12:00:00', '', 0, 'http://example.com/?p=10', 0, 'post', '', 0),
(11, 1, '2023-05-11 12:00:00', '2023-05-11 12:00:00', '<p>Draft post</p>', 'Draft Post', '', 'draft', 'open', 'open', '', 'draft-post', '', '', '2023-05-11 12:00:00', '2023-05-11 12:00:00', '', 0, 'http://example.com/?p=11', 0, 'post', '', 0);
"""
        posts = WordPressSqlParser.parse_posts(sample_sql)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], 10)
        self.assertEqual(posts[0]["title"], "First Post")
        self.assertEqual(posts[0]["slug"], "first-post")
        self.assertEqual(posts[0]["status"], "publish")

    def test_parse_sql_file_with_meta(self):
        import tempfile
        from pathlib import Path
        sample_sql = """
INSERT INTO `wp_posts` (`ID`, `post_author`, `post_date`, `post_date_gmt`, `post_content`, `post_title`, `post_excerpt`, `post_status`, `comment_status`, `ping_status`, `post_password`, `post_name`, `to_ping`, `pinged`, `post_modified`, `post_modified_gmt`, `post_content_filtered`, `post_parent`, `guid`, `menu_order`, `post_type`, `post_mime_type`, `comment_count`) VALUES
(25, 1, '2023-01-01 00:00:00', '2023-01-01 00:00:00', '<p>Hello</p>', 'Post 25', '', 'publish', 'open', 'open', '', 'post-25', '', '', '2023-01-01 00:00:00', '2023-01-01 00:00:00', '', 0, 'http://example.com/?p=25', 0, 'post', '', 0);

INSERT INTO `wp_postmeta` (`meta_id`, `post_id`, `meta_key`, `meta_value`) VALUES
(101, 25, '_yoast_wpseo_title', 'Custom SEO Title for Post 25'),
(102, 25, '_yoast_wpseo_metadesc', 'Meta description for Google search');
"""
        with tempfile.NamedTemporaryFile("w+", suffix=".sql") as tf:
            tf.write(sample_sql)
            tf.flush()
            posts = WordPressSqlParser.parse_sql_file(tf.name, extract_meta=True)
            self.assertEqual(len(posts), 1)
            self.assertEqual(posts[0]["meta_title"], "Custom SEO Title for Post 25")
            self.assertEqual(posts[0]["excerpt"], "Meta description for Google search")

if __name__ == "__main__":
    unittest.main()
