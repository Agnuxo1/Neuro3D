import unittest
import math
from path_counts import count_source,ledger


class CountTests(unittest.TestCase):
    def test_one_cell_and_conf1_terminal_path_count(self):
        self.assertEqual(ledger(1)['paths_all_sources_exact'],8)
        self.assertEqual(ledger(4)['paths_all_sources_exact'],17492)
        self.assertEqual(count_source(4,'row',0),6688)
    def test_independent_terminal_combinatorics(self):
        for k in range(1,9):
            for j in range(k):
                right=sum(math.comb(k+q-1,q)*2**(k+q) for q in range(k-j))
                up=sum(math.comb(k-j+p-1,p)*2**(k-j+p) for p in range(k))
                self.assertEqual(count_source(k,'row',j),right+up)
    def test_symmetry_and_upper_bound(self):
        for k in range(1,9):
            self.assertEqual([count_source(k,'row',j) for j in range(k)],
                             [count_source(k,'column',j) for j in range(k)])
            l=ledger(k)
            self.assertLessEqual(l['paths_all_sources_exact'],l['paths_all_sources_upper_bound'])
    def test_k8_source_versus_all_source_memory(self):
        l=ledger(8)
        self.assertEqual(l['paths_r0_exact'],297402880)
        self.assertAlmostEqual(l['r0_hypothetical_20byte_records_gib'],5.539560317993164)
        self.assertEqual(l['all_sources_upper_bound_20byte_records_gib'],
                         16*l['r0_hypothetical_20byte_records_gib'])
        self.assertFalse(l['capacity_limit_demonstrated'])
    def test_invalid_size_and_source(self):
        for args in ((0,'row',0),(33,'row',0),(True,'row',0),(2,'invalid',0),(2,'row',2)):
            with self.assertRaises(ValueError): count_source(*args)


if __name__=='__main__': unittest.main()
