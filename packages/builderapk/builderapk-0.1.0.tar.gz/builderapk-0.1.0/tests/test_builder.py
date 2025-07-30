# tests/test_builder.py
import unittest
from builderapk import build_apk
import os

class TestBuilderApk(unittest.TestCase):
    def test_build_apk(self):
        # Ganti dengan jalur proyek Android yang valid untuk testing
        project_path = '/path/to/android/project'
        try:
            apk = build_apk(project_path, build_type='debug')
            self.assertTrue(os.path.exists(apk))
        except Exception as e:
            self.fail(f"build_apk raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
