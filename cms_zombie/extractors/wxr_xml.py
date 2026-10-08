import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class WxrXmlParser:
    """Parses WordPress eXtended RSS (WXR) XML export dumps."""

    WP_NS = {
        "content": "http://purl.org/rss/1.0/modules/content/",
        "excerpt": "http://wordpress.org/export/1.2/excerpt/",
        "wp": "http://wordpress.org/export/1.2/"
    }

    @classmethod
    def parse(cls, xml_text: str) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return []

        items = []
        for item in channel.findall("item"):
            post_type_elem = item.find("wp:post_type", cls.WP_NS)
            post_type = post_type_elem.text if post_type_elem is not None else "post"
            status_elem = item.find("wp:status", cls.WP_NS)
            status = status_elem.text if status_elem is not None else "publish"

            if status != "publish" or post_type not in ("post", "page"):
                continue

            title_elem = item.find("title")
            title = title_elem.text if title_elem is not None and title_elem.text else ""

            slug_elem = item.find("wp:post_name", cls.WP_NS)
            slug = slug_elem.text if slug_elem is not None and slug_elem.text else ""

            date_elem = item.find("wp:post_date", cls.WP_NS)
            date = date_elem.text if date_elem is not None and date_elem.text else ""

            content_elem = item.find("content:encoded", cls.WP_NS)
            content = content_elem.text if content_elem is not None and content_elem.text else ""

            excerpt_elem = item.find("excerpt:encoded", cls.WP_NS)
            excerpt = excerpt_elem.text if excerpt_elem is not None and excerpt_elem.text else ""

            categories = []
            tags = []
            for cat in item.findall("category"):
                domain = cat.attrib.get("domain")
                if domain == "category" and cat.text:
                    categories.append(cat.text)
                elif domain == "post_tag" and cat.text:
                    tags.append(cat.text)

            items.append({
                "title": title,
                "slug": slug,
                "date": date,
                "content": content,
                "excerpt": excerpt,
                "type": post_type,
                "status": status,
                "categories": categories,
                "tags": tags,
                "meta": {}
            })
        return items
