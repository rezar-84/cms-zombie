import json
from pathlib import Path
from typing import List, Dict
from ..sanitizers.html_to_md import HtmlToMarkdown

class AstroScaffolder:
    """Scaffolds a modern Astro project with content collections and extracted markdown posts."""

    @classmethod
    def scaffold(cls, target_dir: Path, project_name: str, posts: List[Dict], redirects: Dict[str, str], enable_headless: bool = False):
        target_dir = Path(target_dir)
        src_dir = target_dir / "src"
        content_dir = src_dir / "content"
        blog_dir = content_dir / "blog"
        pages_dir = content_dir / "pages"
        public_dir = target_dir / "public"

        blog_dir.mkdir(parents=True, exist_ok=True)
        pages_dir.mkdir(parents=True, exist_ok=True)
        public_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "type": "module",
            "version": "0.1.0",
            "scripts": {
                "dev": "astro dev",
                "start": "astro dev",
                "build": "astro build",
                "preview": "astro preview"
            },
            "dependencies": {
                "astro": "^4.0.0"
            }
        }
        (target_dir / "package.json").write_text(json.dumps(package_json, indent=2), encoding="utf-8")

        # 2. Write astro.config.mjs with redirect rules
        redirects_json = json.dumps(redirects, indent=4)
        astro_config = f"""import {{ defineConfig }} from 'astro/config';

// https://astro.build/config
export default defineConfig({{
    site: 'https://example.com',
    redirects: {redirects_json}
}});
"""
        (target_dir / "astro.config.mjs").write_text(astro_config, encoding="utf-8")

        # 3. Write content collections config: src/content/config.ts
        content_config = """import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        slug: z.string().optional(),
        date: z.string().optional(),
        excerpt: z.string().optional(),
        categories: z.array(z.string()).optional(),
        tags: z.array(z.string()).optional()
    })
});

const pages = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        slug: z.string().optional()
    })
});

export const collections = { blog, pages };
"""
        (content_dir / "config.ts").write_text(content_config, encoding="utf-8")

        # 4. If headless CMS requested, write Decap CMS admin dashboard
        if enable_headless:
            admin_dir = public_dir / "admin"
            admin_dir.mkdir(parents=True, exist_ok=True)
            admin_html = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Content Manager — Decap CMS</title>
</head>
<body>
  <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
</body>
</html>
"""
            (admin_dir / "index.html").write_text(admin_html, encoding="utf-8")

            admin_config = """backend:
  name: git-gateway
  branch: main

media_folder: "public/assets"
public_folder: "/assets"

collections:
  - name: "blog"
    label: "Blog Posts"
    folder: "src/content/blog"
    create: true
    slug: "{{slug}}"
    fields:
      - {label: "Title", name: "title", widget: "string"}
      - {label: "Publish Date", name: "date", widget: "datetime"}
      - {label: "Excerpt", name: "excerpt", widget: "string", required: false}
      - {label: "Body", name: "body", widget: "markdown"}

  - name: "pages"
    label: "Pages"
    folder: "src/content/pages"
    create: true
    slug: "{{slug}}"
    fields:
      - {label: "Title", name: "title", widget: "string"}
      - {label: "Body", name: "body", widget: "markdown"}
"""
            (admin_dir / "config.yml").write_text(admin_config, encoding="utf-8")

        # 5. Generate Markdown files for posts and pages
        for p in posts:
            slug = p.get("slug") or f"item-{p.get('id', '0')}"
            post_type = p.get("type", "post")
            dest_folder = pages_dir if post_type == "page" else blog_dir

            meta = {
                "title": p.get("title", ""),
                "slug": slug,
                "date": p.get("date", ""),
                "excerpt": p.get("excerpt", ""),
                "categories": p.get("categories", []),
                "tags": p.get("tags", [])
            }

            md_doc = HtmlToMarkdown.to_markdown_document(p.get("content", ""), meta)
            (dest_folder / f"{slug}.md").write_text(md_doc, encoding="utf-8")
