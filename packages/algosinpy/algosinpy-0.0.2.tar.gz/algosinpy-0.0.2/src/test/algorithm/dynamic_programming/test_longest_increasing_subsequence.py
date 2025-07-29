import unittest
from ....algosinpy.algorithm.dynamic_programming import longest_increasing_subsequence


class LISTestCase(unittest.TestCase):
    def test_lis(self):
        self.assertEqual(longest_increasing_subsequence.lis([3, -2, 3, 1, 2, 5, 2, 4]), [-2, 1, 2, 4])


if __name__ == "__main__":
    unittest.main()
