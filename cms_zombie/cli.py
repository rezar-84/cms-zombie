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
    extract_parser = subparsers.add_parser("extract", help="Extract posts, pages, and metadata from SQL dump or WXR")
    extract_parser.add_argument("--sql", type=str, help="Path to database.sql dump")
    extract_parser.add_argument("--wxr", type=str, help="Path to WordPress WXR XML export")
    extract_parser.add_argument("--uploads", type=str, help="Path to wp-content/uploads directory")
    extract_parser.add_argument("--out", type=str, required=True, help="Target output directory for extracted markdown")

    # Command: rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Scaffold modern Astro project and initialize Nuhut SDLC gates")
    rebuild_parser.add_argument("--sql", type=str, help="Path to database.sql dump")
    rebuild_parser.add_argument("--wxr", type=str, help="Path to WordPress WXR XML export")
    rebuild_parser.add_argument("--uploads", type=str, help="Path to wp-content/uploads directory")
    rebuild_parser.add_argument("--target", type=str, required=True, help="Target directory for the new project")
    rebuild_parser.add_argument("--name", type=str, default="Resurrected App", help="Project name")
    rebuild_parser.add_argument("--no-sdlc", action="store_true", help="Skip initializing Nuhut SDLC quality gates")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command in ("extract", "rebuild"):
        posts = []
        if args.sql:
            sql_path = Path(args.sql)
            if not sql_path.exists():
                sys.stderr.write(f"Error: SQL file {args.sql} not found.\n")
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
            sys.stderr.write("Error: Please provide either --sql or --wxr input.\n")
            sys.exit(1)

        # Generate redirects
        redirect_rules = RedirectManager.generate_redirect_rules(posts)
        astro_redirects = RedirectManager.to_astro_redirects(redirect_rules)
        print(f"[+] Generated {len(redirect_rules)} SEO redirect mappings.")

        if args.command == "rebuild":
            target_path = Path(args.target)
            print(f"[*] Scaffolding modern Astro project in {target_path}...")
            AstroScaffolder.scaffold(target_path, args.name, posts, astro_redirects)

            if args.uploads:
                uploads_path = Path(args.uploads)
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

if __name__ == "__main__":
    main()
