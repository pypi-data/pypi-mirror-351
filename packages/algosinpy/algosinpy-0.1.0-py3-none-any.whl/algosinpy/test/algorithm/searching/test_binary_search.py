import unittest
from algosinpy.algorithm.searching.binary_search import binary_search_index

class BinarySearchTestCase(unittest.TestCase):
    def test_binary_search_index(self):
        self.assertEqual(binary_search_index([1, 2, 3, 6, 12], 6), 3)


if __name__ == "__main__":
    unittest.main()
