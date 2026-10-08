---
description: Rebuild a legacy CMS website into a modern Astro application governed by Nuhut SDLC quality gates.
---

# Rebuild Legacy CMS into AI Modern Codebase

Execute an end-to-end resurrection:
1. Parse the backup (SQL dump + media uploads).
2. Clean Gutenberg blocks and visual builder shortcodes.
3. Scaffold an Astro application with typed Content Collections.
4. Auto-generate 301 SEO redirects to prevent ranking loss.
5. Initialize Nuhut SDLC quality gates (`sdlc-content-seo`, `accessibility`, `ux-designer`).

```bash
python3 -m cms_zombie.cli rebuild \
  --sql /path/to/database.sql \
  --uploads /path/to/wp-content/uploads \
  --target /path/to/new-project \
  --name "My Resurrected Site"
```
