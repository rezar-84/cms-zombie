import json
import re
from pathlib import Path
from typing import List, Dict

class CustomCmsScaffolder:
    """
    Scaffolds a modern, self-contained full-stack web application with an embedded blog CMS.
    Features:
    - Zero external headless CMS dependencies (100% self-hosted & open-source).
    - Hybrid data serving: Dynamic API querying with automatic static JSON fallback.
    - Built-in multi-mode rich editor component (Visual, Split, Source, Preview).
    - Database schema & seed generator (Prisma / relational model).
    """

    @classmethod
    def scaffold(cls, target_dir: Path, project_name: str, posts: List[Dict], redirects: Dict[str, str]):
        target_dir = Path(target_dir)
        src_dir = target_dir / "src"
        public_dir = target_dir / "public"
        blog_json_dir = public_dir / "blog"
        components_dir = src_dir / "components"
        admin_components_dir = components_dir / "admin"
        pages_dir = src_dir / "pages"
        lib_dir = src_dir / "lib"
        prisma_dir = target_dir / "prisma"

        for d in [blog_json_dir, admin_components_dir, pages_dir, lib_dir, prisma_dir]:
            d.mkdir(parents=True, exist_ok=True)

        safe_name = project_name.lower().replace(" ", "-")

        # 1. Root package.json
        package_json = {
            "name": safe_name,
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "db:seed": "node --loader ts-node/esm prisma/seed.ts"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "lucide-react": "^0.395.0",
                "dompurify": "^3.1.5",
                "clsx": "^2.1.1",
                "tailwind-merge": "^2.3.0"
            },
            "devDependencies": {
                "@types/react": "^18.3.3",
                "@types/react-dom": "^18.3.0",
                "@types/dompurify": "^3.0.5",
                "@vitejs/plugin-react": "^4.3.1",
                "typescript": "^5.4.5",
                "vite": "^5.3.1",
                "tailwindcss": "^3.4.4",
                "autoprefixer": "^10.4.19",
                "postcss": "^8.4.38"
            }
        }
        (target_dir / "package.json").write_text(json.dumps(package_json, indent=2), encoding="utf-8")

        # 2. Tailwind & Vite configs
        (target_dir / "vite.config.ts").write_text("""import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
""", encoding="utf-8")

        (target_dir / "tailwind.config.js").write_text("""/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};
""", encoding="utf-8")

        # 3. Export Static Fallback JSON (public/blog/index.json and public/blog/{slug}.json)
        summaries = []
        for post in posts:
            slug = post.get("slug", "")
            title = post.get("title", "")
            content = post.get("content", "")
            date = post.get("date", "")
            categories = post.get("categories", [])
            tags = post.get("tags", [])
            
            # Rough word count & reading time
            words = len(re.findall(r'\\w+', content))
            reading_minutes = max(1, round(words / 200)) if words > 0 else 1

            # Excerpt
            clean_text = re.sub(r'<[^>]+>', '', content)
            excerpt = clean_text[:160].strip() + "..." if len(clean_text) > 160 else clean_text

            summary_item = {
                "id": post.get("id", slug),
                "slug": slug,
                "title": title,
                "excerpt": excerpt,
                "publishedAt": date,
                "categories": categories,
                "tags": tags,
                "readingMinutes": reading_minutes,
                "wordCount": words
            }
            summaries.append(summary_item)

            # Individual Article JSON
            article_payload = {
                **summary_item,
                "bodyHtml": content,
                "featuredImage": post.get("featured_image"),
                "seoTitle": post.get("seo_title", title),
                "seoDescription": post.get("seo_description", excerpt)
            }
            (blog_json_dir / f"{slug}.json").write_text(json.dumps(article_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        (blog_json_dir / "index.json").write_text(json.dumps(summaries, indent=2, ensure_ascii=False), encoding="utf-8")

        # 4. Hybrid Client Library (src/lib/blog-api.ts)
        blog_api_code = """// Hybrid Blog Data Client
// Queries live platform API with automatic fallback to static JSON bundles.

export interface ArticleSummary {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  publishedAt: string;
  categories: string[];
  tags: string[];
  readingMinutes: number;
}

export interface ArticleDetail extends ArticleSummary {
  bodyHtml: string;
  featuredImage?: string;
  seoTitle?: string;
  seoDescription?: string;
}

const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\\/$/, '');
const STATIC_BASE = '/blog';

export async function fetchArticles(): Promise<ArticleSummary[]> {
  try {
    const res = await fetch(`${API_BASE}/articles`, { headers: { Accept: 'application/json' } });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.items)) return data.items;
      if (Array.isArray(data)) return data;
    }
  } catch {
    // Dynamic API unavailable, fall through to static fallback
  }

  const staticRes = await fetch(`${STATIC_BASE}/index.json`);
  if (!staticRes.ok) throw new Error('Failed to load blog catalog');
  return staticRes.json();
}

export async function fetchArticleBySlug(slug: string): Promise<ArticleDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/articles/${encodeURIComponent(slug)}`, { headers: { Accept: 'application/json' } });
    if (res.ok) return await res.json();
  } catch {
    // Dynamic API unavailable, fall through to static fallback
  }

  const staticRes = await fetch(`${STATIC_BASE}/${encodeURIComponent(slug)}.json`);
  if (staticRes.status === 404) return null;
  if (!staticRes.ok) throw new Error(`Article not found: ${slug}`);
  return staticRes.json();
}
"""
        (lib_dir / "blog-api.ts").write_text(blog_api_code, encoding="utf-8")

        # 5. Admin Rich Editor Component (src/components/admin/ArticleEditor.tsx)
        editor_code = """import { useState, useRef, useEffect } from 'react';
import DOMPurify from 'dompurify';
import { Bold, Italic, Heading2, Heading3, Link, List, Quote, Code, Eye, Columns } from 'lucide-react';

export type EditorMode = 'visual' | 'split' | 'source' | 'preview';

interface ArticleEditorProps {
  initialValue?: string;
  onChange?: (html: string) => void;
}

export function ArticleEditor({ initialValue = '', onChange }: ArticleEditorProps) {
  const [content, setContent] = useState(initialValue);
  const [mode, setMode] = useState<EditorMode>('split');
  const visualRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (visualRef.current && visualRef.current.innerHTML !== content) {
      visualRef.current.innerHTML = content;
    }
  }, [content]);

  const handleVisualInput = () => {
    if (visualRef.current) {
      const html = visualRef.current.innerHTML;
      setContent(html);
      onChange?.(html);
    }
  };

  const handleSourceChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    onChange?.(val);
  };

  const exec = (command: string, value: string | undefined = undefined) => {
    document.execCommand(command, false, value);
    handleVisualInput();
  };

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2 bg-slate-50">
        <div className="flex items-center space-x-1">
          <button type="button" onClick={() => exec('bold')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Bold">
            <Bold size={16} />
          </button>
          <button type="button" onClick={() => exec('italic')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Italic">
            <Italic size={16} />
          </button>
          <button type="button" onClick={() => exec('formatBlock', '<h2>')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Heading 2">
            <Heading2 size={16} />
          </button>
          <button type="button" onClick={() => exec('formatBlock', '<h3>')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Heading 3">
            <Heading3 size={16} />
          </button>
          <button type="button" onClick={() => exec('insertUnorderedList')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Bullet List">
            <List size={16} />
          </button>
          <button type="button" onClick={() => exec('formatBlock', '<blockquote>')} className="p-1.5 hover:bg-slate-200 rounded text-slate-700" title="Quote">
            <Quote size={16} />
          </button>
        </div>

        <div className="flex items-center border border-slate-300 rounded-lg p-0.5 bg-white text-xs">
          <button
            type="button"
            onClick={() => setMode('visual')}
            className={`px-2.5 py-1 rounded font-medium ${mode === 'visual' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Visual
          </button>
          <button
            type="button"
            onClick={() => setMode('split')}
            className={`px-2.5 py-1 rounded font-medium ${mode === 'split' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Split
          </button>
          <button
            type="button"
            onClick={() => setMode('source')}
            className={`px-2.5 py-1 rounded font-medium ${mode === 'source' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Source
          </button>
          <button
            type="button"
            onClick={() => setMode('preview')}
            className={`px-2.5 py-1 rounded font-medium ${mode === 'preview' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Preview
          </button>
        </div>
      </div>

      <div className="min-h-[380px] p-4">
        {mode === 'visual' && (
          <div
            ref={visualRef}
            contentEditable
            onInput={handleVisualInput}
            className="prose max-w-none focus:outline-none min-h-[350px]"
          />
        )}

        {mode === 'split' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
            <textarea
              value={content}
              onChange={handleSourceChange}
              className="w-full h-full min-h-[350px] font-mono text-xs p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Enter HTML or Markdown markup..."
            />
            <div
              className="prose max-w-none border-l pl-4 overflow-y-auto max-h-[500px]"
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}
            />
          </div>
        )}

        {mode === 'source' && (
          <textarea
            value={content}
            onChange={handleSourceChange}
            className="w-full min-h-[350px] font-mono text-xs p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        )}

        {mode === 'preview' && (
          <div
            className="prose max-w-none p-2"
            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}
          />
        )}
      </div>
    </div>
  );
}
"""
        (admin_components_dir / "ArticleEditor.tsx").write_text(editor_code, encoding="utf-8")

        # 6. Reader UI (src/pages/BlogList.tsx & src/pages/ArticleDetail.tsx)
        blog_list_code = """import { useEffect, useState } from 'react';
import { fetchArticles, type ArticleSummary } from '../lib/blog-api';

export function BlogList() {
  const [articles, setArticles] = useState<ArticleSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchArticles()
      .then(setArticles)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading articles...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <header className="mb-10 text-center">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">Latest Articles</h1>
        <p className="mt-3 text-slate-600">Explore migrated posts, guides, and updates.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((art) => (
          <article key={art.id} className="border border-slate-200 rounded-xl p-5 hover:shadow-md transition-shadow bg-white flex flex-col justify-between">
            <div>
              <div className="text-xs text-indigo-600 font-semibold mb-2">{art.categories?.[0] || 'General'}</div>
              <h2 className="text-lg font-bold text-slate-900 mb-2 leading-snug">
                <a href={`/blog/${art.slug}`} className="hover:text-indigo-600">
                  {art.title}
                </a>
              </h2>
              <p className="text-xs text-slate-600 line-clamp-3 mb-4">{art.excerpt}</p>
            </div>
            <div className="text-[11px] text-slate-400 flex items-center justify-between pt-3 border-t border-slate-100">
              <span>{art.publishedAt?.split(' ')[0] || 'Recently'}</span>
              <span>{art.readingMinutes} min read</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
"""
        (pages_dir / "BlogList.tsx").write_text(blog_list_code, encoding="utf-8")

        article_detail_code = """import { useEffect, useState } from 'react';
import DOMPurify from 'dompurify';
import { fetchArticleBySlug, type ArticleDetail as IArticleDetail } from '../lib/blog-api';

interface Props {
  slug: string;
}

export function ArticleDetail({ slug }: Props) {
  const [article, setArticle] = useState<IArticleDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchArticleBySlug(slug)
      .then(setArticle)
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading article...</div>;
  if (!article) return <div className="p-8 text-center text-slate-500">Article not found.</div>;

  return (
    <article className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-4">{article.title}</h1>
        <div className="flex items-center space-x-3 text-xs text-slate-500">
          <span>{article.publishedAt?.split(' ')[0]}</span>
          <span>•</span>
          <span>{article.readingMinutes} min read</span>
        </div>
      </header>

      {article.featuredImage && (
        <img src={article.featuredImage} alt={article.title} className="w-full rounded-xl mb-8 object-cover max-h-96" />
      )}

      <div
        className="prose max-w-none text-slate-800 leading-relaxed"
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(article.bodyHtml) }}
      />
    </article>
  );
}
"""
        (pages_dir / "ArticleDetail.tsx").write_text(article_detail_code, encoding="utf-8")

        # 7. Database Layer (prisma/schema.prisma & prisma/seed.ts)
        prisma_schema = """datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model ArticleCategory {
  id          String    @id @default(cuid())
  name        String
  slug        String    @unique
  description String?
  articles    Article[]
  createdAt   DateTime  @default(now())
}

model ArticleTag {
  id        String    @id @default(cuid())
  name      String
  slug      String    @unique
  articles  Article[]
  createdAt DateTime  @default(now())
}

model Article {
  id             String           @id @default(cuid())
  slug           String           @unique
  title          String
  excerpt        String?
  bodyHtml       String
  featuredImage  String?
  seoTitle       String?
  seoDescription String?
  readingMinutes Int?             @default(1)
  published      Boolean          @default(true)
  publishedAt    DateTime?        @default(now())
  categoryId     String?
  category       ArticleCategory? @relation(fields: [categoryId], references: [id])
  tags           ArticleTag[]
  createdAt      DateTime         @default(now())
  updatedAt      DateTime         @updatedAt
}
"""
        (prisma_dir / "schema.prisma").write_text(prisma_schema, encoding="utf-8")

        seed_data_json = json.dumps(posts, ensure_ascii=False)
        seed_script = f"""// Database seed script automatically generated by cms-zombie
import {{ PrismaClient }} from '@prisma/client';

const prisma = new PrismaClient();
const posts = {seed_data_json};

async function main() {{
  console.log(`[*] Seeding ${{posts.length}} migrated articles into database...`);

  for (const p of posts) {{
    const slug = p.slug || `post-${{p.id}}`;
    await prisma.article.upsert({{
      where: {{ slug }},
      update: {{
        title: p.title || '',
        bodyHtml: p.content || '',
      }},
      create: {{
        slug,
        title: p.title || '',
        bodyHtml: p.content || '',
        published: true,
      }},
    }});
  }}

  console.log('[+] Seeding completed successfully.');
}}

main()
  .catch((e) => {{
    console.error(e);
    process.exit(1);
  }})
  .finally(async () => {{
    await prisma.$disconnect();
  }});
"""
        (prisma_dir / "seed.ts").write_text(seed_script, encoding="utf-8")
        return True
