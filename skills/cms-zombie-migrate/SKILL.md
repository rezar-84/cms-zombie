---
name: cms-zombie-migrate
description: Resurrect and migrate a legacy CMS website (WordPress, Drupal) into a modern AI-built application (Astro/Next.js). Use when given a CMS backup, SQL dump, or live site URL to modernize.
---

# CMS Zombie Migration & Rebuild Protocol

When migrating a legacy CMS website into a modern AI-developed architecture, follow this strict protocol:

## 1. Non-Destructive Extraction
- Always parse the database offline. Never execute drop or modify statements on production data.
- Extract:
  - Posts and Pages (`post_status = 'publish'`).
  - Slugs, published dates, and author attributes.
  - Taxonomies (categories and tags).
  - SEO metadata (Yoast / RankMath titles and descriptions).
  - Original media from `wp-content/uploads/` while skipping auto-generated thumbnails (`-150x150`, `-300x200`).

## 2. Sanitization Rules
- **Strip Gutenberg comments**: Remove `<!-- wp:... -->` comments while retaining inner semantic HTML.
- **Flatten visual page builder shortcodes**: Elementor, Divi (`[et_pb_*]`), and WPBakery (`[vc_*]`) tags must be converted to semantic tags or plain Markdown without leaving bracket noise.
- **Link Normalization**: Convert absolute internal URLs (`https://old-domain.com/...`) into relative root paths (`/...`).

## 3. SEO Defense (Zero Traffic Loss)
- Every single legacy URL structure (`/%year%/%monthnum%/%postname%/`, `/?p=123`, `/category/*`) must have a corresponding **301 permanent redirect** mapped to the new path.
- Verify redirect map using Nuhut's `sdlc-content-seo` skill.

## 4. Modern Codebase Scaffolding
- Default to **Astro Content Collections** or **Next.js App Router**.
- Ensure content is strictly typed via Zod schemas (`src/content/config.ts`).
- Initialize Nuhut SDLC quality gates: run `./install.sh <target-dir>`.

## 5. Parity & Acceptance Verification
- Check count: Verify that `number of published SQL rows == number of generated Markdown files`.
- Run `sdlc-accessibility-audit` to confirm WCAG 2.2 AA compliance.
- Run Lighthouse to verify 95+ performance score on mobile and desktop.
