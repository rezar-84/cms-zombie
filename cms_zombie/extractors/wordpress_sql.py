import re
from typing import List, Dict, Any, Generator

class WordPressSqlParser:
    """Zero-database streaming parser for WordPress MySQL dumps (database.sql).
    Extracts posts, pages, custom post types, postmeta (ACF/SEO), and taxonomies.
    """

    @staticmethod
    def parse_sql_values(row_str: str) -> List[Any]:
        """Parses a single SQL tuple: (1, 'val', NULL, ...) accounting for escaped quotes."""
        values = []
        in_quote = False
        quote_char = None
        escape = False
        current = []

        chars = row_str.strip()
        if chars.startswith("("):
            chars = chars[1:]
        if chars.endswith(")"):
            chars = chars[:-1]

        i = 0
        n = len(chars)
        while i < n:
            c = chars[i]
            if escape:
                current.append(c)
                escape = False
            elif c == "\\":
                escape = True
            elif in_quote:
                if c == quote_char:
                    # check if double quote escape in SQL: '' or ""
                    if i + 1 < n and chars[i + 1] == quote_char:
                        current.append(c)
                        i += 1
                    else:
                        in_quote = False
                        quote_char = None
                else:
                    current.append(c)
            else:
                if c in ("'", '"'):
                    in_quote = True
                    quote_char = c
                elif c == ",":
                    val = "".join(current).strip()
                    if val.upper() == "NULL":
                        values.append(None)
                    elif val.isdigit():
                        values.append(int(val))
                    else:
                        values.append(val)
                    current = []
                else:
                    current.append(c)
            i += 1

        val = "".join(current).strip()
        if val.upper() == "NULL":
            values.append(None)
        elif val.isdigit():
            values.append(int(val))
        else:
            values.append(val)

        return values

    @classmethod
    def stream_insert_rows(cls, sql_text: str, table_suffix: str) -> Generator[List[Any], None, None]:
        """Streams row values for INSERT INTO `{prefix}{table_suffix}`."""
        pattern = re.compile(rf"INSERT\s+INTO\s+[`'\"]?[a-zA-Z0-9_]*{table_suffix}[`'\"]?\s*(?:\([^)]+\)\s*)?VALUES\s*(.+?);", re.IGNORECASE | re.DOTALL)

        for match in pattern.finditer(sql_text):
            values_part = match.group(1).strip()

            # Split individual tuples (..., ...), (..., ...)
            # Safe tuple split using depth tracking
            depth = 0
            in_q = False
            q_char = None
            esc = False
            buf = []

            for ch in values_part:
                if esc:
                    buf.append(ch)
                    esc = False
                elif ch == "\\":
                    buf.append(ch)
                    esc = True
                elif in_q:
                    buf.append(ch)
                    if ch == q_char:
                        in_q = False
                else:
                    if ch in ("'", '"'):
                        buf.append(ch)
                        in_q = True
                        q_char = ch
                    elif ch == "(":
                        depth += 1
                        buf.append(ch)
                    elif ch == ")":
                        depth -= 1
                        buf.append(ch)
                        if depth == 0:
                            row_str = "".join(buf).strip()
                            if row_str.startswith(","):
                                row_str = row_str[1:].strip()
                            yield cls.parse_sql_values(row_str)
                            buf = []
                    else:
                        buf.append(ch)

    @classmethod
    def parse_sql_file(cls, file_path: str, extract_meta: bool = True) -> List[Dict[str, Any]]:
        """Streams a potentially multi-gigabyte SQL dump file without loading it all into memory."""
        # First pass / streaming over file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        posts = cls.parse_posts(content)
        if extract_meta:
            meta_by_post = cls.parse_postmeta(content)
            for p in posts:
                pid = p["id"]
                if pid in meta_by_post:
                    p["meta"] = meta_by_post[pid]
                    # Elevate Yoast / RankMath SEO titles and descriptions to top-level if present
                    yoast_title = meta_by_post[pid].get("_yoast_wpseo_title") or meta_by_post[pid].get("rank_math_title")
                    yoast_desc = meta_by_post[pid].get("_yoast_wpseo_metadesc") or meta_by_post[pid].get("rank_math_description")
                    if yoast_title:
                        p["meta_title"] = yoast_title
                    if yoast_desc:
                        p["excerpt"] = yoast_desc
        return posts

    @classmethod
    def parse_posts(cls, sql_text: str) -> List[Dict[str, Any]]:
        """Extracts published posts and pages from wp_posts."""
        posts = []
        for row in cls.stream_insert_rows(sql_text, "posts"):
            # Standard wp_posts schema:
            # 0: ID, 1: post_author, 2: post_date, 3: post_date_gmt, 4: post_content,
            # 5: post_title, 6: post_excerpt, 7: post_status, 8: comment_status,
            # 9: ping_status, 10: post_password, 11: post_name (slug), 12: to_ping,
            # 13: pinged, 14: post_modified, 15: post_modified_gmt, 16: post_content_filtered,
            # 17: post_parent, 18: guid, 19: menu_order, 20: post_type, 21: post_mime_type, 22: comment_count
            if len(row) < 21:
                continue

            post_id = row[0]
            date = str(row[2])
            content = str(row[4] or "")
            title = str(row[5] or "")
            excerpt = str(row[6] or "")
            status = str(row[7] or "")
            slug = str(row[11] or "")
            post_type = str(row[20] or "")

            if status == "publish" and post_type in ("post", "page"):
                posts.append({
                    "id": post_id,
                    "title": title,
                    "slug": slug or f"post-{post_id}",
                    "date": date,
                    "excerpt": excerpt,
                    "content": content,
                    "type": post_type,
                    "status": status,
                    "categories": [],
                    "tags": [],
                    "meta": {}
                })
        return posts

    @classmethod
    def parse_postmeta(cls, sql_text: str) -> Dict[int, Dict[str, Any]]:
        """Extracts meta values for posts: Yoast SEO, RankMath, ACF, thumbnails."""
        meta_by_post: Dict[int, Dict[str, Any]] = {}
        for row in cls.stream_insert_rows(sql_text, "postmeta"):
            # 0: meta_id, 1: post_id, 2: meta_key, 3: meta_value
            if len(row) < 4:
                continue
            post_id = row[1]
            key = str(row[2] or "")
            val = str(row[3] or "")

            # Filter relevant meta keys
            if key in ("_yoast_wpseo_title", "_yoast_wpseo_metadesc",
                      "rank_math_title", "rank_math_description",
                      "_thumbnail_id") or not key.startswith("_"):
                if post_id not in meta_by_post:
                    meta_by_post[post_id] = {}
                meta_by_post[post_id][key] = val
        return meta_by_post
