import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from html import unescape
from typing import List, Dict, Any, Optional

class LiveCrawler:
    """Crawls live CMS websites via sitemaps or direct HTTP requests,
    with an optional pluggable stealth mode using Scrapling for anti-bot bypass.
    """

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    @classmethod
    def fetch_url(cls, url: str, use_stealth: bool = False, timeout: int = 15) -> str:
        """Fetches HTML from URL. Uses standard library by default; switches to Scrapling if requested."""
        if use_stealth:
            return cls._fetch_with_scrapling(url)

        req = urllib.request.Request(url, headers=cls.DEFAULT_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="ignore")
        except urllib.error.HTTPError as e:
            if e.code in (403, 503) and not use_stealth:
                # Potential Cloudflare / Wordfence challenge
                try:
                    return cls._fetch_with_scrapling(url)
                except ImportError:
                    raise RuntimeError(
                        f"HTTP {e.code} received from {url} (anti-bot or Cloudflare challenge). "
                        "Install Scrapling to enable stealth bypass: pip install 'cms-zombie[crawler]'"
                    )
            raise

    @classmethod
    def _fetch_with_scrapling(cls, url: str) -> str:
        """Uses Scrapling StealthyFetcher for anti-bot bypass."""
        try:
            from scrapling.fetchers import StealthyFetcher
            page = StealthyFetcher.fetch(url)
            return page.html
        except ImportError:
            raise ImportError(
                "Scrapling is not installed. To use stealth crawl mode, install it via: pip install 'scrapling[all]'"
            )

    @classmethod
    def parse_sitemap(cls, sitemap_xml: str) -> List[str]:
        """Extracts article and page URLs from sitemap.xml."""
        urls = []
        try:
            root = ET.fromstring(sitemap_xml)
            # Handle XML namespaces: {http://www.sitemaps.org/schemas/sitemap/0.9}loc
            for elem in root.iter():
                if elem.tag.endswith("loc") and elem.text:
                    url = elem.text.strip()
                    # Filter out static resource URLs if present in sitemap
                    if not re.search(r"\.(jpg|jpeg|png|gif|pdf|zip|css|js)$", url, re.IGNORECASE):
                        urls.append(url)
        except Exception:
            # Fallback regex extraction if XML malformed
            for match in re.finditer(r"<loc>(https?://[^<]+)</loc>", sitemap_xml, re.IGNORECASE):
                urls.append(match.group(1).strip())
        return list(dict.fromkeys(urls)) # deduplicate

    @classmethod
    def extract_article_content(cls, html: str, page_url: str) -> Dict[str, Any]:
        """Extracts title, body HTML, description, and slug from a live page."""
        # 1. Title: <title> or <meta property="og:title">
        title = ""
        og_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_title:
            title = og_title.group(1).strip()
        else:
            t_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if t_m:
                title = re.sub(r"\s*[-|].*$", "", t_m.group(1).strip()) # strip sitename suffix

        # 2. Meta description
        desc = ""
        og_desc = re.search(r'<meta[^>]*(?:name=["\']description["\']|property=["\']og:description["\'])[^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_desc:
            desc = og_desc.group(1).strip()

        # 3. Main article body extraction
        # Searches for standard article containers
        body_html = ""
        body_patterns = [
            r"<article[^>]*>(.*?)</article>",
            r'<div[^>]*class=["\'][^"\']*(?:entry-content|post-content|article-content|main-content)[^"\']*["\'][^>]*>(.*?)</div>',
            r"<main[^>]*>(.*?)</main>"
        ]
        for pat in body_patterns:
            m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
            if m:
                body_html = m.group(1).strip()
                break

        if not body_html:
            # Fallback to body tag
            m = re.search(r"<body[^>]*>(.*?)</body>", html, re.IGNORECASE | re.DOTALL)
            body_html = m.group(1).strip() if m else html

        # Compute slug from URL path
        parsed = urllib.parse.urlparse(page_url)
        path = parsed.path.strip("/")
        slug = path.split("/")[-1] if path else "index"

        return {
            "title": unescape(title),
            "description": unescape(desc),
            "content": body_html,
            "slug": slug,
            "url": page_url
        }
