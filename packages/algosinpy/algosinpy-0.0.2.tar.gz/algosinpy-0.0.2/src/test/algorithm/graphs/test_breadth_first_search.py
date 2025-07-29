import unittest
from ....algosinpy.algorithm.graphs import breadth_first_search


class TestBreadthFirstSearch(unittest.TestCase):
    def test_bfs(self):
        graph = breadth_first_search.Graph(is_bidirectional=True)
        graph.add_edge(0, 1)
        graph.add_edge(0, 2)
        graph.add_edge(2, 3)
        graph.add_edge(2, 4)
        graph.add_edge(1, 2)
        self.assertEqual(graph.bfs(2), [2, 0, 3, 4, 1])


if __name__ == "__main__":
    unittest.main()
