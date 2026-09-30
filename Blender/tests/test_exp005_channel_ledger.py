"""Synthetic mode-channel tests; no orthogonality/raycast runtime validation."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp005_scene_properties import decode_scene, field_for_path, sum_declared_channels


def optics():
    return decode_scene({'lambda_BU':.1,'objects':{
        's':{'kind':'bs'}, 'd':{'kind':'det'}, 'e':{'kind':'escape'}}})


def route(terminal='e', field=1):
    return {'initial_field':field,'hits':[
        {'object_id':'s','event':'t','distance_BU':.1},
        {'object_id':terminal,'event':'escape' if terminal=='e' else 'detect',
         'distance_BU':.13}]}


class ChannelLedgerTests(unittest.TestCase):
    def test_declared_unvisited_ports_are_explicit_zero_not_missing(self):
        result=sum_declared_channels(optics(),[route('e')])
        self.assertEqual(set(result['fields']),{'d','e'})
        self.assertEqual(result['fields']['d'],0j)
        self.assertEqual(result['powers']['d'],0.)
        self.assertEqual(result['path_counts']['d'],0)
        self.assertEqual(result['path_counts']['e'],1)

    def test_escape_cancels_coherently_not_pathwise(self):
        result = sum_declared_channels(optics(),[route(field=1),route(field=-1)])
        self.assertEqual(result['escape_power'],0)
        self.assertEqual(result['path_counts']['e'],2)
        # A pathwise intensity sum would incorrectly report 1 instead of 0.
        separate = sum(abs(field_for_path(optics(),r['hits'],r['initial_field'])['field'])**2
                       for r in [route(field=1),route(field=-1)])
        self.assertAlmostEqual(separate,1)

    def test_reinforcement_is_not_renormalized(self):
        result = sum_declared_channels(optics(),[route(),route()])
        self.assertAlmostEqual(result['escape_power'],2)

    def test_detectors_and_escape_never_share_a_bucket(self):
        result = sum_declared_channels(optics(),[route('d'),route('e',-1)])
        self.assertAlmostEqual(result['detected_power'],.5)
        self.assertAlmostEqual(result['escape_power'],.5)

    def test_escape_boundary_distance_affects_phase(self):
        before = route(); after = copy.deepcopy(before)
        after['hits'][-1]['distance_BU'] += .025
        a = field_for_path(optics(),before['hits'])['field']
        b = field_for_path(optics(),after['hits'])['field']
        self.assertLess(abs(b/a-1j),1e-13)

    def test_missing_initial_field_and_empty_set_fail(self):
        with self.assertRaises(ValueError): sum_declared_channels(optics(),[])
        bad = route(); del bad['initial_field']
        with self.assertRaises(KeyError): sum_declared_channels(optics(),[bad])

    def test_unknown_escape_and_wrong_terminal_event_fail(self):
        bad = route(); bad['hits'][-1]['object_id'] = 'arbitrary-channel'
        with self.assertRaises(KeyError): sum_declared_channels(optics(),[bad])
        bad = route(); bad['hits'][-1]['event'] = 'detect'
        with self.assertRaises(ValueError): sum_declared_channels(optics(),[bad])

    def test_nonterminal_escape_is_not_discarded(self):
        bad = route(); bad['hits'].append({'object_id':'d','event':'detect','distance_BU':1})
        with self.assertRaises(ValueError): sum_declared_channels(optics(),[bad])


if __name__ == '__main__':
    unittest.main(verbosity=2)
