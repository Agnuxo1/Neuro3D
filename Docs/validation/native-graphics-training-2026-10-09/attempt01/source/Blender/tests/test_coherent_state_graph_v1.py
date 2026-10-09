"""Graph quotient vs exhaustive paths, analytic oracle and independent hits."""
import copy
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from exp005_chain_fixture import chain_fixture,analytic_fields
from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.benchmarks.capacity_audit.robust_multipath_v1 import trace_scene
from Tools.trace_indexed_scene_v1 import wire
from Tools.audit_coherent_state_graph_v1 import audit_graph_result


def run(snapshot):
    graph=build_graph(snapshot)
    fields={s['id']:s['field_reim'] for s in snapshot['sources']}
    result={'graph':graph,'fields':None,'powers':None}
    if graph['status']=='COMPLETE':
        result.update(propagate_graph(graph,fields))
    return result


def scene_wire(value):
    if isinstance(value,float):
        return wire(F(value))
    if isinstance(value,dict):
        return {k:scene_wire(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [scene_wire(v) for v in value]
    return wire(value)


class StateGraphTests(unittest.TestCase):
    def test_chain_all_sources_against_exhaustive_and_analytic(self):
        snapshot=chain_fixture(2)
        values=[complex(.3,.2),complex(-.6,.1),complex(.1,-.2)]
        for s,value in zip(snapshot['sources'],values):
            s['field_reim']=[value.real,value.imag]
        result=run(snapshot)
        traced=trace_scene(snapshot)
        expected=analytic_fields(2,values)
        self.assertEqual(result['graph']['status'],'COMPLETE')
        for port,value in expected.items():
            self.assertLess(abs(value-result['fields'][port]),2e-14)
            self.assertLess(abs(traced['fields'][port]-result['fields'][port]),2e-13)
        self.assertEqual(result['represented_terminal_paths'],len(traced['paths']))
        audit=audit_graph_result(scene_wire(snapshot),wire(result))
        self.assertTrue(audit['nearest_hits_independently_verified'])
        self.assertFalse(audit['field_certified'])

    def test_same_state_sources_cancel_fields_before_future_operator(self):
        snapshot=scene({'out':plane_x(2)})
        other=copy.deepcopy(snapshot['sources'][0])
        other.update(id='opposed',field_reim=[-1,0])
        snapshot['sources'].append(other)
        result=run(snapshot)
        self.assertEqual(len(result['graph']['nodes']),1)
        self.assertEqual(result['powers']['out'],0)
        self.assertEqual(result['represented_terminal_paths'],2)
        self.assertEqual(audit_graph_result(wire(snapshot),wire(result))['primary_metric'],1)

    def test_cycle_is_unknown_not_pruned(self):
        snapshot=scene({'left':plane_x(0,'mirror'),'right':plane_x(1,'mirror'),'out':plane_x(2)},origin=(F(1,2),0,0))
        result=run(snapshot)
        self.assertEqual(result['graph']['status'],'INCOMPLETE')
        self.assertIn('CYCLE',{r['status'] for r in result['graph']['unresolved']})
        self.assertIsNone(result['fields'])

    def test_exact_zero_branch_and_both_nonzero_branches(self):
        for tau,count in ((0,1),(F(1,2),2),(1,1)):
            snapshot=scene({'bs':plane_x(1,'bs',power_transmittance=tau),'out':plane_x(2),
                            'escape':plane_x(-1,'escape',axis=(-1,0,0))})
            result=run(snapshot)
            self.assertEqual(result['represented_terminal_paths'],count)
            self.assertEqual(audit_graph_result(wire(snapshot),wire(result))['primary_metric'],1)

    def test_missing_branch_rejected(self):
        snapshot=scene({'bs':plane_x(1,'bs'),'out':plane_x(2),'escape':plane_x(-1,'escape',axis=(-1,0,0))})
        result=wire(run(snapshot))
        result['graph']['nodes'][0]['edges'].pop()
        with self.assertRaisesRegex(ValueError,'branch'):
            audit_graph_result(wire(snapshot),result)

    def test_forged_farther_hit_rejected(self):
        snapshot=scene({'near':plane_x(1),'far':plane_x(2)})
        result=wire(run(snapshot))
        node=result['graph']['nodes'][0]
        node.update(hit_object='far',primitive_id=1,coincident_primitives=[1],segment_parameter=2,point=[2,0,0],terminal='far')
        with self.assertRaisesRegex(ValueError,'nearest'):
            audit_graph_result(wire(snapshot),result)

    def test_state_cap_preserves_null_fields(self):
        graph=build_graph(chain_fixture(2),max_states=2)
        self.assertEqual(graph['status'],'INCOMPLETE')
        self.assertIn('STATE_LIMIT',{r['status'] for r in graph['unresolved']})
        with self.assertRaisesRegex(ValueError,'complete'):
            propagate_graph(graph,{s['id']:[1,0] for s in chain_fixture(2)['sources']})

    def test_mode_mismatch_miss_boundary_contact_remain_unresolved(self):
        snapshots=[scene({'out':plane_x(1,axis=(1,1,0))}),
                   scene({'out':plane_x(1)},direction=(-1,0,0)),
                   scene({'out':plane_x(1)},origin=(0,0,-4)),
                   scene({'out':plane_x(0)})]
        for snapshot in snapshots:
            result=run(snapshot)
            self.assertEqual(result['graph']['status'],'INCOMPLETE')
            self.assertIsNone(result['fields'])
            self.assertEqual(audit_graph_result(wire(snapshot),wire(result))['primary_metric'],0)


if __name__=='__main__':
    unittest.main()
