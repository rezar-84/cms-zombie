import os
import re
import shutil
from pathlib import Path
from typing import List, Dict

class MediaAssetManager:
    """Manages wp-content/uploads extraction, filtering out auto-generated resized thumbnails."""

    # Matches WordPress thumbnail suffixes like -150x150.jpg, -300x200.png, -768x512.webp
    WP_THUMB_RE = re.compile(r"-\d+x\d+\.(jpg|jpeg|png|webp|gif|svg)$", re.IGNORECASE)

    @classmethod
    def is_original_asset(cls, filename: str) -> bool:
        """Returns True if the file is an original asset, False if it is an auto-generated thumbnail."""
        return not bool(cls.WP_THUMB_RE.search(filename))

    @classmethod
    def copy_original_assets(cls, source_uploads_dir: Path, target_assets_dir: Path) -> List[Dict[str, str]]:
        """Copies only original assets into target, preserving relative folder structure."""
        copied = []
        source_uploads_dir = Path(source_uploads_dir)
        target_assets_dir = Path(target_assets_dir)

        if not source_uploads_dir.exists():
            return copied

        for root, _, files in os.walk(source_uploads_dir):
            for file in files:
                if file.startswith("."):
                    continue
                if cls.is_original_asset(file):
                    src_path = Path(root) / file
                    rel_path = src_path.relative_to(source_uploads_dir)
                    dest_path = target_assets_dir / rel_path

                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    copied.append({
                        "original": str(rel_path),
                        "destination": str(dest_path)
                    })
        return copied
