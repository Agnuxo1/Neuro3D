"""CPU invalidation/resource lifecycle contract; fake GPU is NOT evidence of GPU execution."""
import ast
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from exp005_chain_fixture import chain_fixture,set_fields
from resident_frontier_gpu import SceneBinding,ResidentSession,static_key
from exp005_resident_runtime import resident_order,summary


class ResidentTests(unittest.TestCase):
    def test_fields_change_only_raw_inputs_not_static_binding(self):
        scene=chain_fixture(4); binding=SceneBinding(scene,mode_cap=5)
        changed=copy.deepcopy(scene); set_fields(changed,[1j,-1+2j,0j,3j,1+1j])
        result=binding.inputs(changed)
        self.assertEqual(result.geometry,binding.batch.geometry)
        self.assertEqual(result.optics,binding.batch.optics)
        self.assertEqual(result.sources[3::8],(0.,-1.,0.,0.,1.))
        self.assertEqual(result.sources[7::8],(1.,2.,0.,3.,1.))
        self.assertEqual(binding.batch.sources[3::8],(1.,0.,0.,0.,0.))

    def test_every_static_edit_requires_explicit_rebuild(self):
        original=chain_fixture(3); binding=SceneBinding(original,mode_cap=5)
        def phase(s): s['objects']['c0.r1']['phase_rad']+=.1
        def splitter(s): s['objects']['c0.bs1']['power_transmittance']=.2
        def wavelength(s): s['lambda_BU']+=.001
        def mesh(s): s['objects']['c0.r1']['vertices_world_BU'][0]=(99,0,0)
        def mode(s): next(o for o in s['objects'].values() if o['kind']=='det')['mode_direction']=[0,0,1]
        def source(s): s['sources'][0]['direction']=[0,1,0]
        def order(s): s['objects']=dict(reversed(list(s['objects'].items())))
        def missing(s): del s['objects']['c0.r1']
        def extra(s): s['undeclared_meshes']=['hidden geometry']
        for edit in (phase,splitter,wavelength,mesh,mode,source,order,missing,extra):
            changed=copy.deepcopy(original); edit(changed)
            with self.subTest(edit=edit.__name__),self.assertRaises(ValueError): binding.inputs(changed)

    def test_nonfinite_or_malformed_fields_rejected(self):
        for pair in ([float('nan'),0],[float('inf'),0],[True,0],[1],[1,2,3]):
            scene=chain_fixture(3); scene['sources'][0]['field_reim']=pair
            with self.assertRaises(ValueError): static_key(scene)

    def test_closed_session_never_dispatches_and_releases_owned_refs(self):
        session=object.__new__(ResidentSession);session.closed=False
        session.static=[object()];session.outputs=[object()]
        session.close();session.close()
        self.assertEqual((session.static,session.outputs),([],[]))
        with self.assertRaises(ValueError):session.run(chain_fixture(3))

    def test_stale_scene_poisoned_before_texture_transfer(self):
        session=object.__new__(ResidentSession);session.closed=False
        session.static=[];session.outputs=[]
        session.binding=SceneBinding(chain_fixture(3),mode_cap=5)
        changed=chain_fixture(3,treatment='phase')
        with patch.object(session,'_textures',side_effect=AssertionError('no transfer')):
            with self.assertRaisesRegex(ValueError,'scene changed'):session.run(changed)
        self.assertTrue(session.closed)

    def test_no_result_cache_or_cpu_paths_and_dispatch_every_valid_call(self):
        path=Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'resident_frontier_gpu.py'
        code=path.read_text();tree=ast.parse(code)
        run=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='run')
        text=ast.get_source_segment(code,run)
        self.assertIn('compute.dispatch',text)
        self.assertNotIn('trace_scene',code);self.assertNotIn('ray_cast',code)
        self.assertNotIn('self.result',text)

    def fake_gpu(self):
        texture=Mock();texture.read.return_value.to_list.return_value=[0.,0.,0.,0.]
        gpu=SimpleNamespace(types=SimpleNamespace(GPUTexture=Mock(return_value=texture),
            Buffer=lambda kind,count,values:values),compute=SimpleNamespace(dispatch=Mock()))
        return gpu

    def test_residency_allocations_and_fresh_dispatches_fake_gpu_only(self):
        gpu=self.fake_gpu();scene=chain_fixture(3)
        session=ResidentSession(gpu,Mock(),scene,mode_cap=5)
        self.assertEqual(gpu.types.GPUTexture.call_count,8)
        with patch('resident_frontier_gpu.decode',return_value={'valid':True}) as decoder:
            for amps in ([1,0,0,0],[0,1j,0,0],[0,0,0,0]):
                set_fields(scene,amps);session.run(scene)
            self.assertEqual((gpu.compute.dispatch.call_count,decoder.call_count,session.calls),(3,3,3))
        self.assertEqual((session.allocations,gpu.types.GPUTexture.call_count),(14,14))
        session.close()

    def test_partial_gpu_result_poisoned_fake_gpu_only(self):
        gpu=self.fake_gpu();scene=chain_fixture(3);session=ResidentSession(gpu,Mock(),scene,mode_cap=5)
        with patch('resident_frontier_gpu.decode',return_value={'valid':False}):
            with self.assertRaisesRegex(ValueError,'aborted'):session.run(scene)
        self.assertTrue(session.closed);self.assertEqual(session.calls,0)
        with self.assertRaises(ValueError):session.run(scene)
        self.assertEqual(gpu.compute.dispatch.call_count,1)

    def test_resident_pair_statistics_no_selection(self):
        rows=[{'backend':name,'pair':i,'hot_ms':1. if name=='fresh' else 2.}
              for i in range(20) for name in resident_order(i)]
        self.assertEqual(summary(rows)['paired_fresh_over_resident']['median'],.5)
        for bad in (rows[:-1],list(reversed(rows))):
            with self.assertRaises(ValueError):summary(bad)


if __name__=='__main__':unittest.main()
