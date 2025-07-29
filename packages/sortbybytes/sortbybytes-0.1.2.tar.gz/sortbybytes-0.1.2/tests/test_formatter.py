import unittest
from sortbybytes import get_size

class TestFormatter(unittest.TestCase):
    def test_bytes_to_human_readable(self):
        self.assertEqual(get_size(1253656), "1.20 MB")
        self.assertEqual(get_size(1024), "1.00 KB")
        self.assertEqual(get_size(1024**2), "1.00 MB")
        self.assertEqual(get_size(1024**3), "1.00 GB")
        self.assertEqual(get_size(123), "123.00 B")

    def test_suffix_customization(self):
        self.assertEqual(get_size(2048, suffix="Bytes"), "2.00 KBytes")

if __name__ == '__main__':
    unittest.main()
