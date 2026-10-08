---
description: Open or serve the visual migration reporting and progress tracker dashboard for an extracted or rebuilt project.
---

# CMS Zombie View — Migration Dashboard

Open the self-contained migration reporting dashboard to inspect extracted content, SEO 301 redirects, media status, and sanitization health:

```bash
# Generate static HTML report and open in browser
python3 -m cms_zombie.cli view /path/to/migrated-project

# Start real-time local server
python3 -m cms_zombie.cli view /path/to/migrated-project --serve
```
