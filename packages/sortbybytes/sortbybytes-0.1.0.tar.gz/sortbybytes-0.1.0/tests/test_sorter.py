import unittest
from sortbybytes import sortvalue

class TestSorter(unittest.TestCase):
    def test_sort_ascending(self):
        data = ["25.6 MB", "5.6 KB", "12.5 GB"]
        expected = ["5.6 KB", "25.6 MB", "12.5 GB"]
        self.assertEqual(sortvalue(data), expected)

    def test_sort_descending(self):
        data = ["25.6 MB", "5.6 KB", "12.5 GB"]
        expected = ["12.5 GB", "25.6 MB", "5.6 KB"]
        self.assertEqual(sortvalue(data, reverse=True), expected)

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            sortvalue(["25.6MB", "invalid"])

if __name__ == '__main__':
    unittest.main()
