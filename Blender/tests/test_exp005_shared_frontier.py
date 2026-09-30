"""CPU tests of shared counter ABI, isolation, and native source contract."""
import ast
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from shared_frontier_gpu import decode,dispatch,SHADER
from frontier_gpu import SHADER as PREVIOUS
from frontier_inputs import pack_frontier
from exp005_chain_fixture import chain_fixture


class SharedFrontierTests(unittest.TestCase):
    def payload(self):
        batch=pack_frontier(chain_fixture(4),mode_cap=5)
        fields=[0.]*20; stats=[0.]*20; ledger=[0.]*2560
        for i in range(5): stats[i*4:i*4+4]=[415.,0.,21.,0.]
        return batch,fields,stats,ledger,[415.,0.,1.,0.]

    def test_shared_total_not_sum_of_port_copies(self):
        args=self.payload(); result=decode(*args)
        self.assertTrue(result['valid']); self.assertEqual(result['work']['total_casts'],415)
        self.assertEqual(result['work']['traversal_invocations'],1)
        self.assertEqual(sum(p['casts'] for p in result['ports'].values()),2075)

    def test_inconsistent_work_is_not_accepted(self):
        for index,value in ((0,414.),(1,1.),(2,0.),(2,5.),(3,1.),(0,float('nan'))):
            batch,fields,stats,ledger,work=self.payload(); work[index]=value
            with self.subTest(index=index,value=value),self.assertRaises(ValueError): decode(batch,fields,stats,ledger,work)
        batch,fields,stats,ledger,work=self.payload(); stats[0]-=1
        with self.assertRaises(ValueError): decode(batch,fields,stats,ledger,work)
        with self.assertRaises(ValueError): decode(batch,fields,stats,ledger,[415.,0.,1.])

    def test_shared_abort_all_outputs_clear(self):
        batch,fields,stats,ledger,work=self.payload()
        for i in range(5): fields[i*4+3]=1.; stats[i*4+3]=1.
        work[3]=1.; result=decode(batch,fields,stats,ledger,work)
        self.assertFalse(result['valid']); self.assertEqual(len(result['errors']),5)
        fields[0]=.1
        with self.assertRaises(ValueError): decode(batch,fields,stats,ledger,work)

    def test_single_invocation_no_cpu_paths_and_old_shader_is_separate(self):
        code=SHADER.read_text(); prior=PREVIOUS.read_text()
        self.assertNotEqual(SHADER,PREVIOUS)
        self.assertIn('if(invocation!=0) return',code)
        self.assertIn('sum_fields[5]',code); self.assertIn('work_out',code)
        self.assertIn('int port=int(gl_GlobalInvocationID.x)',prior)
        for name in ('paths_hi','hits_hi','cpu_field'): self.assertNotIn(name,code)
        # Identical intersection/phase primitives; no bias/sign drift in the optimization.
        self.assertEqual(code[code.index('const double TAU'):code.index('void main()')],
                         prior[prior.index('const double TAU'):prior.index('void main()')].replace('    best+=BIAS; // Original ray origin distance, not shortened biased length.','    best+=BIAS;'))
        import shared_frontier_gpu
        tree=ast.parse(Path(shared_frontier_gpu.__file__).read_text())
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='dispatch']
        self.assertEqual(len(calls),1)
        self.assertEqual([ast.unparse(x) for x in calls[0].args],['shader','1','1','1'])

    def test_limits_before_gpu_and_default_profile_protected(self):
        with self.assertRaises(ValueError): dispatch(None,None,chain_fixture(4),max_steps=0)
        with self.assertRaises(ValueError): dispatch(None,None,chain_fixture(4))

    def test_runtime_routes_only_raw_scene_and_never_saves_frozen_blends(self):
        code=Path(__file__).with_name('exp005_shared_runtime.py').read_text(); tree=ast.parse(code)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dispatch']
        self.assertEqual(len(calls),2)
        for call in calls: self.assertEqual([arg.id for arg in call.args],['gpu','shader','snapshot'])
        self.assertNotIn('save_as_mainfile',code)
        self.assertIn('INPUT_REPORT_SHA',code); self.assertIn('phase_locality(',code)

    def test_independent_oracle_rejects_false_shared_counts(self):
        from exp005_shared_runtime import shared_parity
        from exp005_triangle_oracle import trace_scene
        scene=chain_fixture(3); oracle=trace_scene(scene); native={'valid':True,'errors':{},'ports':{}}
        for p,field in oracle['fields'].items():
            paths=[row for row in oracle['paths'] if row['terminal']==p]
            native['ports'][p]={'field_reim':[field.real,field.imag],'power':abs(field)**2,'casts':oracle['rays'],
                               'ledger':[{'source_id':row['source_id'],'field_reim':[row['field'].real,row['field'].imag],
                               'effective_length_BU':row['length_BU']+row['reference_offset_BU']} for row in paths]}
        native['work']={'total_casts':oracle['rays'],'total_terminal_paths':len(oracle['paths']),
                         'traversal_invocations':1,'status':0}
        shared_parity(scene,native)
        for key in ('total_casts','total_terminal_paths','traversal_invocations','status'):
            native['work'][key]+=1
            with self.subTest(key=key),self.assertRaises(ValueError): shared_parity(scene,native)
            native['work'][key]-=1


if __name__=='__main__': unittest.main()
