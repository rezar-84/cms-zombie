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

    def test_zip_slip_prevention(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            malicious_zip = tmp_path / "evil.zip"

            # Create archive with path traversal filename
            with zipfile.ZipFile(malicious_zip, "w") as zf:
                zf.writestr("../../evil.sh", "echo hacked")

            work_dir = tmp_path / "unpacked"
            with self.assertRaises(ValueError) as ctx:
                ArchiveInspector.extract_archive(malicious_zip, work_dir)
            self.assertIn("Zip-Slip", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
