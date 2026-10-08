import json
from typing import List, Dict, Any

class NavigationBuilder:
    """Builds clean navigation menus (Header & Footer) from extracted posts and pages."""

    @classmethod
    def build_navigation(cls, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        header_items = []
        footer_items = []

        # Collect published pages as primary navigation candidates
        pages = [p for p in posts if p.get("type") == "page"]
        
        # Priority order for standard pages
        priority_slugs = ["home", "about", "about-us", "services", "blog", "contact", "contact-us"]
        
        # Sort pages by priority order
        def page_sort_key(p):
            slug = (p.get("slug") or "").lower()
            if slug in priority_slugs:
                return priority_slugs.index(slug)
            return 99

        pages.sort(key=page_sort_key)

        # Build Header items
        header_items.append({"title": "Home", "url": "/"})
        for page in pages[:5]:
            slug = page.get("slug")
            if slug not in ("home", "index"):
                header_items.append({
                    "title": page.get("title") or slug.replace("-", " ").title(),
                    "url": f"/{slug}"
                })

        # Add Blog to header if we have posts
        has_posts = any(p.get("type") == "post" for p in posts)
        if has_posts and not any(i["title"].lower() == "blog" for i in header_items):
            header_items.append({"title": "Blog", "url": "/blog"})

        # Build Footer items
        footer_items = list(header_items)
        # Add Privacy / Terms if available
        legal_pages = [p for p in pages if p.get("slug") in ("privacy", "privacy-policy", "terms", "terms-of-service")]
        for lp in legal_pages:
            footer_items.append({
                "title": lp.get("title") or lp.get("slug").replace("-", " ").title(),
                "url": f"/{lp.get('slug')}"
            })

        return {
            "header": header_items,
            "footer": footer_items
        }

    @classmethod
    def to_json(cls, nav_data: Dict[str, Any]) -> str:
        return json.dumps(nav_data, indent=2)
