"""CPU-only synthetic multicell correctness and safe preflight, no Blender."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from exp005_chain_fixture import chain_fixture,inputs,set_fields,analytic_fields,summarize
from exp005_triangle_oracle import trace_scene
from exp005_mode_gate import mode_geometry
from frontier_inputs import pack_frontier


class ChainTests(unittest.TestCase):
    def test_three_four_cell_geometry_and_analytic_parity(self):
        for cells in (3,4):
            scene=chain_fixture(cells); mode_geometry(scene)
            for name,amps in inputs(cells+1):
                set_fields(scene,amps); trace=trace_scene(scene); reference=analytic_fields(cells,amps)
                with self.subTest(cells=cells,probe=name):
                    self.assertEqual(set(trace['fields']),set(reference))
                    self.assertLess(max(abs(trace['fields'][p]-reference[p]) for p in reference),1e-11)
                    self.assertLess(abs(trace['input_power']-trace['output_power']),1e-11)

    def test_exact_geometry_and_all_source_path_bounds(self):
        for cells,triangles,paths in ((3,44,58),(4,58,128)):
            scene=chain_fixture(cells); set_fields(scene,[1+0j]*(cells+1))
            counts=summarize(scene,trace_scene(scene))
            self.assertEqual((counts['triangles'],counts['terminal_paths']),(triangles,paths))
            self.assertEqual((counts['sources'],counts['ports']),(cells+1,cells+1))
            self.assertLess(counts['rays'],4096)
            self.assertLessEqual(counts['depth'],32)
            self.assertLessEqual(max(counts['paths_by_port'].values()),128)

    def test_legacy_gpu_payload_rejects_more_sources_without_new_contract(self):
        for cells in (3,4):
            with self.subTest(cells=cells),self.assertRaises(ValueError): pack_frontier(chain_fixture(cells))

    def test_opt_in_transport_profile_five_not_implicit_legacy_expansion(self):
        for cells in (3,4):
            payload=pack_frontier(chain_fixture(cells),mode_cap=5)
            self.assertEqual(payload.geometry.query_count,cells+1)
            self.assertEqual((len(payload.source_ids),len(payload.ports)),(cells+1,cells+1))
            self.assertEqual(payload.geometry.triangle_count,14*cells+2)
        for cap in (True,2,4,6,5.):
            with self.assertRaises(ValueError): pack_frontier(chain_fixture(3),mode_cap=cap)

    def test_causal_controls_and_negative_mirror(self):
        for cells in (3,4):
            baseline=trace_scene(chain_fixture(cells))
            for case in ('phase','shift','T','lambda'):
                trace=trace_scene(chain_fixture(cells,treatment=case))
                with self.subTest(cells=cells,case=case):
                    self.assertGreater(max(abs(trace['powers'][p]-baseline['powers'][p]) for p in trace['powers']),1e-3)
                    self.assertLess(abs(trace['input_power']-trace['output_power']),1e-11)
            sham=trace_scene(chain_fixture(cells,treatment='sham'))
            self.assertEqual(sham['fields'],baseline['fields'])
            scene=chain_fixture(cells); del scene['objects'][f'c{cells-1}.r1']
            with self.assertRaises(ValueError): trace_scene(scene)

    def test_small_phase_oracle_and_fixture_bounds(self):
        for cells in (3,4):
            amps=[1+0j]+[0j]*cells
            trace=trace_scene(chain_fixture(cells,treatment='phase'))
            reference=analytic_fields(cells,amps,phase_shift=.1)
            self.assertLess(max(abs(trace['fields'][p]-reference[p]) for p in reference),1e-11)
        for cells in (True,1,5,3.):
            with self.assertRaises(ValueError): chain_fixture(cells)


if __name__=='__main__': unittest.main()
