import os
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Optional

class ArchiveInspector:
    """Unpacks and automatically detects SQL database dumps and wp-content/uploads
    from cPanel (backup-*.tar.gz), WP Engine (*.zip), Plesk (*.tar), and generic archives.
    """

    @classmethod
    def extract_archive(cls, archive_path: Path, dest_dir: Path) -> Path:
        archive_path = Path(archive_path)
        dest_dir = dest_dir.resolve()

        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zf:
                for member in zf.infolist():
                    target_path = (dest_dir / member.filename).resolve()
                    if not str(target_path).startswith(str(dest_dir)):
                        raise ValueError(f"Security: Zip-Slip traversal attempt detected in {member.filename}")
                zf.extractall(dest_dir)
        elif tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as tf:
                for member in tf.getmembers():
                    target_path = (dest_dir / member.name).resolve()
                    if not str(target_path).startswith(str(dest_dir)):
                        raise ValueError(f"Security: Tar traversal attempt detected in {member.name}")
                tf.extractall(dest_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.name}")

        return dest_dir

    @classmethod
    def find_sql_dump(cls, search_dir: Path) -> Optional[Path]:
        """Finds the primary SQL database dump (choosing the largest if multiple exist)."""
        sql_files = []
        for root, _, files in os.walk(search_dir):
            for f in files:
                if f.lower().endswith(".sql"):
                    p = Path(root) / f
                    sql_files.append((p.stat().st_size, p))

        if not sql_files:
            return None

        # Sort by size descending (largest SQL dump is the main database)
        sql_files.sort(key=lambda item: item[0], reverse=True)
        return sql_files[0][1]

    @classmethod
    def find_uploads_dir(cls, search_dir: Path) -> Optional[Path]:
        """Locates the media uploads folder (e.g. wp-content/uploads or sites/default/files)."""
        for root, dirs, _ in os.walk(search_dir):
            for d in dirs:
                full_path = Path(root) / d
                # Check for standard WordPress uploads path
                if str(full_path).endswith("wp-content/uploads") or d == "uploads":
                    return full_path
                # Check for Drupal public files path
                if str(full_path).endswith("sites/default/files"):
                    return full_path
        return None

    @classmethod
    def inspect(cls, archive_path: Path, work_dir: Path) -> Dict[str, Optional[Path]]:
        """Unpacks archive and returns detected paths for 'sql' and 'uploads'."""
        extracted_root = cls.extract_archive(archive_path, work_dir)
        sql_path = cls.find_sql_dump(extracted_root)
        uploads_path = cls.find_uploads_dir(extracted_root)

        return {
            "root": extracted_root,
            "sql": sql_path,
            "uploads": uploads_path
        }
