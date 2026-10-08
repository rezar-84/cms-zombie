import json
from typing import List, Dict

class RedirectManager:
    """Generates 301 permanent redirect rules to preserve Google SEO rankings across CMS migrations."""

    @classmethod
    def generate_redirect_rules(cls, posts: List[Dict], permalink_style: str = "/%postname%/") -> List[Dict[str, str]]:
        rules = []
        for post in posts:
            slug = post.get("slug")
            date_str = str(post.get("date", ""))
            post_type = post.get("type", "post")

            if not slug:
                continue

            # Target clean modern path
            target_path = f"/{slug}" if post_type == "page" else f"/blog/{slug}"

            # Calculate legacy source path based on standard WordPress permalinks
            date_clean = date_str.split(" ")[0].replace("/", "-")
            if "-" in date_clean and len(date_clean) >= 7:
                parts = date_clean.split("-")
                year, month = (parts[0], parts[1]) if len(parts) >= 2 else ("2020", "01")
            else:
                year, month = "2020", "01"

            legacy_paths = [
                f"/{year}/{month}/{slug}/",
                f"/{year}/{month}/{slug}",
                f"/{slug}/",
                f"/?p={post.get('id')}"
            ]

            for legacy in legacy_paths:
                if legacy != target_path:
                    rules.append({
                        "source": legacy,
                        "destination": target_path,
                        "status": 301
                    })
        return rules

    @classmethod
    def to_astro_redirects(cls, rules: List[Dict[str, str]]) -> Dict[str, str]:
        """Converts to Astro config redirect mapping."""
        return {r["source"]: r["destination"] for r in rules}

    @classmethod
    def to_netlify_redirects(cls, rules: List[Dict[str, str]]) -> str:
        """Converts to Netlify _redirects file format."""
        lines = [f"{r['source']} {r['destination']} 301" for r in rules]
        return "\n".join(lines) + "\n"

    @classmethod
    def to_json(cls, rules: List[Dict[str, str]]) -> str:
        return json.dumps(rules, indent=2)
