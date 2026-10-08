import unittest
from cms_zombie.navigation.menus import NavigationBuilder
from cms_zombie.forms.converter import FormConverter

class TestNavigationAndForms(unittest.TestCase):

    def test_build_navigation(self):
        posts = [
            {"title": "About Us", "slug": "about-us", "type": "page"},
            {"title": "Services", "slug": "services", "type": "page"},
            {"title": "Contact", "slug": "contact", "type": "page"},
            {"title": "Privacy Policy", "slug": "privacy-policy", "type": "page"},
            {"title": "First Blog Post", "slug": "first-post", "type": "post"}
        ]
        nav = NavigationBuilder.build_navigation(posts)
        header_urls = [i["url"] for i in nav["header"]]
        self.assertIn("/", header_urls)
        self.assertIn("/about-us", header_urls)
        self.assertIn("/blog", header_urls)

        footer_urls = [i["url"] for i in nav["footer"]]
        self.assertIn("/privacy-policy", footer_urls)

    def test_form_conversion(self):
        content_with_form = "<p>Contact us below:</p>[contact-form-7 id='42' title='Main Contact']"
        converted = FormConverter.convert_forms(content_with_form)
        self.assertNotIn("contact-form-7", converted)
        self.assertIn("<form", converted)
        self.assertIn("Submit Message", converted)

if __name__ == "__main__":
    unittest.main()
