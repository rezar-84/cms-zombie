import argparse
import sys
from pathlib import Path
from .extractors.wordpress_sql import WordPressSqlParser
from .extractors.wxr_xml import WxrXmlParser
from .media.assets import MediaAssetManager
from .seo.redirects import RedirectManager
from .generators.astro import AstroScaffolder
from .generators.nuhut_init import NuhutInitializer

def main():
    parser = argparse.ArgumentParser(
        prog="cms-zombie",
        description="Resurrect legacy CMS websites into high-performance modern AI code."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extract posts, pages, and metadata from SQL dump, WXR, or archive")
    extract_parser.add_argument("--archive", type=str, help="Path to cPanel/WP Engine/Plesk backup archive (.tar.gz, .zip, .tar)")
    extract_parser.add_argument("--sql", type=str, help="Path to database.sql dump")
    extract_parser.add_argument("--wxr", type=str, help="Path to WordPress WXR XML export")
    extract_parser.add_argument("--uploads", type=str, help="Path to wp-content/uploads directory")
    extract_parser.add_argument("--out", type=str, required=True, help="Target output directory for extracted markdown")

    # Command: rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Scaffold modern Astro project and initialize Nuhut SDLC gates")
    rebuild_parser.add_argument("--archive", type=str, help="Path to cPanel/WP Engine/Plesk backup archive (.tar.gz, .zip, .tar)")
    rebuild_parser.add_argument("--sql", type=str, help="Path to database.sql dump")
    rebuild_parser.add_argument("--wxr", type=str, help="Path to WordPress WXR XML export")
    rebuild_parser.add_argument("--uploads", type=str, help="Path to wp-content/uploads directory")
    rebuild_parser.add_argument("--target", type=str, required=True, help="Target directory for the new project")
    rebuild_parser.add_argument("--name", type=str, default="Resurrected App", help="Project name")
    rebuild_parser.add_argument("--no-sdlc", action="store_true", help="Skip initializing Nuhut SDLC quality gates")

    # Command: crawl
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a live CMS site via sitemap/URL with optional stealth bypass")
    crawl_parser.add_argument("--url", type=str, required=True, help="Target website base URL (e.g. https://oldsite.com)")
    crawl_parser.add_argument("--target", type=str, required=True, help="Target directory for the new project")
    crawl_parser.add_argument("--name", type=str, default="Resurrected Site", help="Project name")
    crawl_parser.add_argument("--stealth", action="store_true", help="Enable Scrapling stealth mode to bypass Cloudflare/Turnstile")
    crawl_parser.add_argument("--no-sdlc", action="store_true", help="Skip initializing Nuhut SDLC quality gates")

    # Command: view
    view_parser = subparsers.add_parser("view", help="View migration reporting and progress tracker dashboard")
    view_parser.add_argument("project", type=str, help="Path to migrated or extracted project directory")
    view_parser.add_argument("--serve", action="store_true", help="Start local real-time server")
    view_parser.add_argument("--port", type=int, default=8765, help="Server port (default: 8765)")
    view_parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    temp_dir_obj = None
    if args.command in ("extract", "rebuild"):
        sql_target = args.sql
        uploads_target = args.uploads

        if args.archive:
            archive_path = Path(args.archive)
            if not archive_path.exists():
                sys.stderr.write(f"Error: Archive {args.archive} not found.\n")
                sys.exit(1)
            import tempfile
            temp_dir_obj = tempfile.TemporaryDirectory()
            work_dir = Path(temp_dir_obj.name)
            print(f"[*] Unpacking and inspecting archive: {archive_path.name}...")
            from .adapters.archives import ArchiveInspector
            detected = ArchiveInspector.inspect(archive_path, work_dir)
            if detected["sql"]:
                sql_target = str(detected["sql"])
                print(f"[+] Detected SQL dump: {detected['sql'].name}")
            if detected["uploads"]:
                uploads_target = str(detected["uploads"])
                print(f"[+] Detected uploads directory: {detected['uploads']}")

        posts = []
        if sql_target:
            sql_path = Path(sql_target)
            if not sql_path.exists():
                sys.stderr.write(f"Error: SQL file {sql_target} not found.\n")
                sys.exit(1)
            print(f"[*] Parsing SQL dump: {sql_path.name}...")
            content = sql_path.read_text(encoding="utf-8", errors="ignore")
            posts = WordPressSqlParser.parse_posts(content)
            print(f"[+] Found {len(posts)} published posts & pages.")
        elif args.wxr:
            wxr_path = Path(args.wxr)
            if not wxr_path.exists():
                sys.stderr.write(f"Error: WXR file {args.wxr} not found.\n")
                sys.exit(1)
            print(f"[*] Parsing WXR export: {wxr_path.name}...")
            content = wxr_path.read_text(encoding="utf-8", errors="ignore")
            posts = WxrXmlParser.parse(content)
            print(f"[+] Found {len(posts)} published posts & pages.")
        else:
            sys.stderr.write("Error: Please provide --archive, --sql, or --wxr input.\n")
            sys.exit(1)

        # Generate redirects
        redirect_rules = RedirectManager.generate_redirect_rules(posts)
        astro_redirects = RedirectManager.to_astro_redirects(redirect_rules)
        print(f"[+] Generated {len(redirect_rules)} SEO redirect mappings.")

        if args.command == "rebuild":
            target_path = Path(args.target)
            print(f"[*] Scaffolding modern Astro project in {target_path}...")
            AstroScaffolder.scaffold(target_path, args.name, posts, astro_redirects)

            if uploads_target:
                uploads_path = Path(uploads_target)
                if uploads_path.exists():
                    print(f"[*] Copying and filtering media from {uploads_path}...")
                    copied = MediaAssetManager.copy_original_assets(uploads_path, target_path / "public" / "assets")
                    print(f"[+] Copied {len(copied)} original assets (skipped auto-generated thumbnails).")

            if not args.no_sdlc:
                print("[*] Initializing Nuhut SDLC quality gates...")
                ok = NuhutInitializer.initialize_nuhut(target_path)
                if ok:
                    print("[+] Nuhut SDLC governance successfully installed.")
                else:
                    print("[!] Note: Could not auto-run Nuhut installer (run ./install.sh manually).")

            print(f"\n[✓] Project successfully resurrected at {target_path}!")

        elif args.command == "extract":
            out_path = Path(args.out)
            out_path.mkdir(parents=True, exist_ok=True)
            from .sanitizers.html_to_md import HtmlToMarkdown
            for p in posts:
                slug = p.get("slug") or f"item-{p.get('id', '0')}"
                md_doc = HtmlToMarkdown.to_markdown_document(p.get("content", ""), p)
                (out_path / f"{slug}.md").write_text(md_doc, encoding="utf-8")
            print(f"\n[✓] Extracted {len(posts)} items to {out_path}!")

    elif args.command == "crawl":
        from .extractors.live_crawler import LiveCrawler
        base_url = args.url.rstrip("/")
        sitemap_url = f"{base_url}/sitemap.xml"
        print(f"[*] Fetching sitemap from {sitemap_url}...")
        try:
            sitemap_xml = LiveCrawler.fetch_url(sitemap_url, use_stealth=args.stealth)
            urls = LiveCrawler.parse_sitemap(sitemap_xml)
            print(f"[+] Discovered {len(urls)} URLs in sitemap.")
        except Exception as e:
            print(f"[!] Could not read sitemap ({e}). Crawling base URL...")
            urls = [base_url]

        posts = []
        for u in urls[:50]: # initial crawl batch
            try:
                print(f"[*] Crawling {u}...")
                page_html = LiveCrawler.fetch_url(u, use_stealth=args.stealth)
                art = LiveCrawler.extract_article_content(page_html, u)
                if art["title"]:
                    posts.append({
                        "title": art["title"],
                        "slug": art["slug"],
                        "date": "",
                        "excerpt": art["description"],
                        "content": art["content"],
                        "type": "post"
                    })
            except Exception as e:
                print(f"[!] Failed to fetch {u}: {e}")

        redirect_rules = RedirectManager.generate_redirect_rules(posts)
        astro_redirects = RedirectManager.to_astro_redirects(redirect_rules)

        target_path = Path(args.target)
        print(f"[*] Scaffolding modern Astro project in {target_path}...")
        AstroScaffolder.scaffold(target_path, args.name, posts, astro_redirects)

        if not args.no_sdlc:
            NuhutInitializer.initialize_nuhut(target_path)

        print(f"\n[✓] Live site successfully crawled & resurrected at {target_path}!")

    elif args.command == "view":
        project_path = Path(args.project)
        if not project_path.exists():
            sys.stderr.write(f"Error: Project path '{args.project}' does not exist.\n")
            sys.exit(1)

        from .view.server import ViewServer
        if args.serve:
            ViewServer.serve(project_path, port=args.port, open_browser=not args.no_browser)
        else:
            report_file = ViewServer.write_static_report(project_path)
            print(f"[✓] Migration report generated at: {report_file}")
            if not args.no_browser:
                import webbrowser
                webbrowser.open(f"file://{report_file.resolve()}")

if __name__ == "__main__":
    main()
