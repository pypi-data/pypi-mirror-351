# tests/test_core.py
import unittest
from geocleaner import clean_location

class TestGeoCleaner(unittest.TestCase):
    def test_clean_location(self):
        self.assertEqual(clean_location("  new york  "), "New York")

if __name__ == '__main__':
    unittest.main()
