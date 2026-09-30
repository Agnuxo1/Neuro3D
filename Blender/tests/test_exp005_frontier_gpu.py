"""Frozen CPU gates/decoder tests; no GPU dispatch or Blender imports."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_gpu import decode,limits,dispatch,SHADER
from frontier_inputs import pack_frontier
from exp005_escape_fixture import escape_fixture
from exp005_triangle_oracle import trace_scene


class FrontierGates(unittest.TestCase):
    def test_final_readback_and_source_owned_ledger(self):
        batch=pack_frontier(escape_fixture()); fields=[0.]*12; stats=[0.]*12; ledger=[0.]*1536
        fields[:4]=[1.,0.,1.,0.]; stats[:4]=[5.,1.,4.,0.]; ledger[:4]=[1.,0.,10.,0.]
        result=decode(batch,fields,stats,ledger)
        self.assertTrue(result['valid']); self.assertEqual(result['ports']['a.Y']['ledger'][0]['source_id'],'a.row')
        bad=ledger.copy(); bad[3]=3.
        with self.assertRaises(ValueError): decode(batch,fields,stats,bad)

    def test_invalid_partial_fields_and_error_flags(self):
        batch=pack_frontier(escape_fixture())
        for flag in (1,2,3,4,5,6,7,8):
            fields=[0.]*12; stats=[0.]*12; fields[3]=flag; stats[3]=flag
            result=decode(batch,fields,stats,[0.]*1536)
            self.assertFalse(result['valid']); self.assertIn('a.Y',result['errors'])
            fields[0]=.1
            with self.assertRaises(ValueError): decode(batch,fields,stats,[0.]*1536)

    def test_limits_before_gpu_access(self):
        for steps,depth in ((True,32),(0,32),(4097,32),(4096,33),(1,0),(1,1.)):
            with self.subTest(steps=steps,depth=depth),self.assertRaises(ValueError): limits(steps,depth)
        limits(4096,32)
        with self.assertRaises(ValueError): dispatch(None,None,escape_fixture(),max_steps=0)

    def test_decoder_rejects_invalid_stats_or_intensity(self):
        batch=pack_frontier(escape_fixture())
        for case in ('flag','fractional','paths','nonfinite','power'):
            fields=[0.]*12; stats=[0.]*12
            if case=='flag': fields[3]=1.
            if case=='fractional': stats[1]=.1
            if case=='paths': stats[1]=129.
            if case=='nonfinite': fields[0]=float('nan')
            if case=='power': fields[2]=1.
            with self.subTest(case=case),self.assertRaises(ValueError): decode(batch,fields,stats,[0.]*1536)

    def test_cpu_fixture_controls_before_gpu(self):
        base=escape_fixture(); ref=trace_scene(base); targets=[]
        phase=copy.deepcopy(base); phase['objects']['a.r1']['phase_rad']+=.1; targets.append(phase)
        wave=copy.deepcopy(base); wave['lambda_BU']=.126; targets.append(wave)
        shift=copy.deepcopy(base)
        for name in ('a.r1','a.r2'):
            obj=shift['objects'][name]; obj['vertices_world_BU']=[(x+.03125,y,z) for x,y,z in obj['vertices_world_BU']]
        targets.append(shift)
        for tau in (.2,1.):
            scene=copy.deepcopy(base); scene['schema']='exp005-readback-v2'
            for obj in scene['objects'].values():
                if obj['kind']=='bs': obj['power_transmittance']=.5
            scene['objects']['b.bs2']['power_transmittance']=tau; targets.append(scene)
        for scene in targets:
            result=trace_scene(scene)
            self.assertGreater(max(abs(result['powers'][p]-ref['powers'][p]) for p in ref['powers']),1e-3)
            self.assertLess(abs(result['input_power']-result['output_power']),2e-4)
        for label in ('missing','overlap','direction'):
            scene=copy.deepcopy(base)
            if label=='missing': del scene['objects']['a.r1']
            if label=='overlap': scene['objects']['alias']=copy.deepcopy(scene['objects']['a.r1'])
            if label=='direction': scene['objects']['a.Y']['mode_direction']=[0,-1,0]
            with self.subTest(case=label),self.assertRaises(ValueError): trace_scene(scene)

    def test_kernel_has_no_path_input_and_no_cpu_frontier_readback(self):
        code=SHADER.read_text()
        for token in ('Ray stack[33]','nearest(ray.o','sqrt(props.y)','reflected','sum_field+=field','ledger_out','status=5','status=6'):
            self.assertIn(token,code)
        self.assertNotIn('paths_hi',code)
        self.assertNotIn('hits_hi',code)

    def test_runtime_comparison_checks_each_path_not_only_power(self):
        from exp005_frontier_runtime import parity
        scene=escape_fixture(); oracle=trace_scene(scene); native={'valid':True,'errors':{},'ports':{}}
        for port,field in oracle['fields'].items():
            paths=[p for p in oracle['paths'] if p['terminal']==port]
            native['ports'][port]={'field_reim':[field.real,field.imag],'power':abs(field)**2,
                'casts':oracle['rays'],'paths':len(paths),'max_depth':max((len(p['hits']) for p in paths),default=0),
                'ledger':[{'source_id':p['source_id'],'field_reim':[p['field'].real,p['field'].imag],
                           'effective_length_BU':p['length_BU']+p['reference_offset_BU']} for p in paths]}
        metrics,_=parity(scene,native)
        self.assertLess(metrics['complex_error'],1e-12)
        native['ports']['a.Y']['ledger'][0]['field_reim'][0]+=.01
        with self.assertRaises(ValueError): parity(scene,native)

    def test_runtime_gpu_call_has_no_oracle_or_path_arguments(self):
        import ast
        code=Path(__file__).with_name('exp005_frontier_runtime.py').read_text(); tree=ast.parse(code)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dispatch']
        self.assertEqual(len(calls),2)
        for call in calls:
            self.assertEqual([n.id for n in call.args],['gpu','shader','snapshot'])
        self.assertNotIn('save_as_mainfile',code)


if __name__=='__main__': unittest.main()
