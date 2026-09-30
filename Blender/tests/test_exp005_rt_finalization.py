import ast
import copy
import unittest
from exp005_rt_finalization_review import audit,pinned,function,isolated_case,PEER


class FinalizationReview(unittest.TestCase):
    def test_eight_finalization_cases(self):
        r=audit();self.assertEqual(len(r['cases']),8)
        self.assertEqual(r['cases'][2]['code'],7)
        self.assertFalse(r['peer_writers_imports_core_and_tests_executed'])

    def test_probe_blocks_before_core(self):
        r=audit();self.assertEqual(r['cases'][1]['events'],['probe','fallback_double'])

    def test_original_watchdog_and_kill_ast_unchanged(self):
        self.assertTrue(all(audit()['preserved_ast'].values()))

    def test_unreviewed_writer_call_rejected_without_running(self):
        sources,_=pinned();node=copy.deepcopy(function(ast.parse(sources[PEER/'guard_v4.py']),'run'))
        node.body.insert(0,ast.Expr(value=ast.Call(func=ast.Name(id='open',ctx=ast.Load()),args=[ast.Constant('never')],keywords=[])))
        with self.assertRaisesRegex(ValueError,'unreviewed call'):isolated_case(node,'not executed')


if __name__=='__main__':unittest.main()
