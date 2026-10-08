---
description: Crawl a live WordPress/Drupal website and resurrect it into modern Astro with optional Scrapling anti-bot stealth bypass.
---

# Crawl Live CMS Website

Crawl a live site by URL, automatically reading its `/sitemap.xml` and extracting articles:

```bash
python3 -m cms_zombie.cli crawl \
  --url https://old-wordpress-site.com \
  --target /path/to/resurrected-site \
  --name "Resurrected Site"
```

### With Cloudflare / Turnstile Stealth Bypass:
If the site is protected by Cloudflare or Wordfence, enable Scrapling stealth mode:

```bash
# Ensure scrapling is installed: pip install 'cms-zombie[crawler]'
python3 -m cms_zombie.cli crawl \
  --url https://old-wordpress-site.com \
  --target /path/to/resurrected-site \
  --stealth
```
