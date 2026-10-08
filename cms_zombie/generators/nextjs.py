import json
from pathlib import Path
from typing import List, Dict
from ..sanitizers.html_to_md import HtmlToMarkdown

class NextJsScaffolder:
    """Scaffolds a modern Next.js 14+ (App Router) project with Markdown posts and Tailwind CSS."""

    @classmethod
    def scaffold(cls, target_dir: Path, project_name: str, posts: List[Dict], redirects: Dict[str, str]):
        target_dir = Path(target_dir)
        app_dir = target_dir / "src" / "app"
        content_dir = target_dir / "content"
        blog_dir = content_dir / "blog"
        pages_dir = content_dir / "pages"
        public_dir = target_dir / "public"

        app_dir.mkdir(parents=True, exist_ok=True)
        blog_dir.mkdir(parents=True, exist_ok=True)
        pages_dir.mkdir(parents=True, exist_ok=True)
        public_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write package.json
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.2.0",
                "react": "^18.3.0",
                "react-dom": "^18.3.0",
                "gray-matter": "^4.0.3"
            }
        }
        (target_dir / "package.json").write_text(json.dumps(package_json, indent=2), encoding="utf-8")

        # 2. Write next.config.js with redirect rules
        redirect_list = [
            {"source": k, "destination": v, "permanent": True}
            for k, v in redirects.items()
        ]
        next_config = f"""/** @type {{import('next').NextConfig}} */
const nextConfig = {{
  async redirects() {{
    return {json.dumps(redirect_list, indent=6)};
  }},
}};

module.exports = nextConfig;
"""
        (target_dir / "next.config.js").write_text(next_config, encoding="utf-8")

        # 3. Write basic Next.js Root Layout: src/app/layout.tsx
        layout_tsx = """export const metadata = {
  title: 'Next.js Resurrected App',
  description: 'Migrated by CMS Zombie',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50">
        <header className="border-b px-6 py-4 flex items-center justify-between">
          <div className="font-bold text-lg">Next.js App</div>
          <nav className="flex gap-4">
            <a href="/" className="hover:underline">Home</a>
            <a href="/blog" className="hover:underline">Blog</a>
          </nav>
        </header>
        <main className="max-w-4xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
"""
        (app_dir / "layout.tsx").write_text(layout_tsx, encoding="utf-8")

        # 4. Generate Markdown files for posts and pages
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
