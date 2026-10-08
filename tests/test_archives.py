import unittest
import tempfile
import zipfile
from pathlib import Path
from cms_zombie.adapters.archives import ArchiveInspector

class TestArchives(unittest.TestCase):

    def test_inspect_zip_archive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            zip_file = tmp_path / "cpanel_backup.zip"

            # Create synthetic archive with nested structure
            with zipfile.ZipFile(zip_file, "w") as zf:
                zf.writestr("homedir/public_html/wp-content/uploads/2023/01/photo.jpg", "binary")
                zf.writestr("mysql/my_database.sql", "INSERT INTO wp_posts VALUES (1);")
                zf.writestr("other.sql", "short")

            work_dir = tmp_path / "unpacked"
            detected = ArchiveInspector.inspect(zip_file, work_dir)

            self.assertIsNotNone(detected["sql"])
            self.assertEqual(detected["sql"].name, "my_database.sql")
            self.assertIsNotNone(detected["uploads"])
            self.assertTrue(str(detected["uploads"]).endswith("wp-content/uploads"))

if __name__ == "__main__":
    unittest.main()
