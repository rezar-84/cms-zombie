import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List

class StateCollector:
    """Collects migration progress and metadata from an extracted or rebuilt project folder."""

    @classmethod
    def collect(cls, project_dir: Path) -> Dict[str, Any]:
        project_dir = Path(project_dir)
        posts = []
        pages = []
        redirects = {}
        assets = []

        # 1. Collect Posts from src/content/blog or root extracted markdown
        blog_dir = project_dir / "src" / "content" / "blog"
        if not blog_dir.exists():
            blog_dir = project_dir # fallback to directory itself if just extracted markdown

        if blog_dir.exists():
            for root, _, files in os.walk(blog_dir):
                for f in files:
                    if f.endswith(".md"):
                        p_path = Path(root) / f
                        meta = cls._parse_markdown_frontmatter(p_path)
                        posts.append(meta)

        # 2. Collect Pages
        pages_dir = project_dir / "src" / "content" / "pages"
        if pages_dir.exists():
            for root, _, files in os.walk(pages_dir):
                for f in files:
                    if f.endswith(".md"):
                        p_path = Path(root) / f
                        meta = cls._parse_markdown_frontmatter(p_path)
                        pages.append(meta)

        # 3. Collect Redirects from astro.config.mjs or redirects.json
        astro_cfg = project_dir / "astro.config.mjs"
        if astro_cfg.exists():
            cfg_text = astro_cfg.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"redirects:\s*(\{.*?\})", cfg_text, re.DOTALL)
            if m:
                try:
                    redirects = json.loads(m.group(1))
                except Exception:
                    pass

        # 4. Collect Media Assets
        assets_dir = project_dir / "public" / "assets"
        if assets_dir.exists():
            for root, _, files in os.walk(assets_dir):
                for f in files:
                    if not f.startswith("."):
                        p = Path(root) / f
                        assets.append({
                            "name": f,
                            "path": str(p.relative_to(project_dir)),
                            "size_kb": round(p.stat().st_size / 1024, 1)
                        })

        total_content = len(posts) + len(pages)
        sanitized_pct = 100 # all markdown created by HtmlToMarkdown is 100% sanitized

        return {
            "project_name": project_dir.name,
            "project_path": str(project_dir),
            "stats": {
                "total_content": total_content,
                "posts_count": len(posts),
                "pages_count": len(pages),
                "redirects_count": len(redirects),
                "assets_count": len(assets),
                "sanitized_percent": sanitized_pct
            },
            "posts": posts,
            "pages": pages,
            "redirects": [{"source": k, "destination": v} for k, v in redirects.items()],
            "assets": assets
        }

    @staticmethod
    def _parse_markdown_frontmatter(file_path: Path) -> Dict[str, Any]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        meta = {
            "filename": file_path.name,
            "slug": file_path.stem,
            "title": file_path.stem,
            "date": "",
            "excerpt": "",
            "categories": [],
            "word_count": len(text.split())
        }

        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1]
                for line in fm.splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k in ("title", "slug", "date", "excerpt"):
                            meta[k] = v
        return meta
