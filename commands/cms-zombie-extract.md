---
description: Extract posts, pages, metadata, and media from a legacy CMS backup (SQL or WXR) into clean Markdown and assets.
---

# Extract Legacy CMS

Run the `cms-zombie` extraction engine to parse the backup offline without needing a MySQL server:

```bash
python3 -m cms_zombie.cli extract --sql /path/to/database.sql --uploads /path/to/wp-content/uploads --out ./extracted
```

Or using a WordPress WXR XML export:
```bash
python3 -m cms_zombie.cli extract --wxr /path/to/export.xml --out ./extracted
```
