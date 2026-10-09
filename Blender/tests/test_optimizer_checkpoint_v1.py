import json,tempfile,unittest
from pathlib import Path
from Blender.blender_lab.optimizer_checkpoint_v1 import atomic_write,load,replay,canonical

def advance(d,m,v,step):
    row={'step':step,'deltas_BU':list(d),'train_loss':sum(x*x for x in d),'gradient_max_abs':max(abs(2*x) for x in d)}
    return [x*.5 for x in d],[2*x for x in d],[4*x*x for x in d],row

class CheckpointControls(unittest.TestCase):
    def test_atomic_roundtrip_and_replayed_state(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as folder:
            path=Path(folder)/'checkpoint.json';d=[1.,-2.];m=v=[0.,0.];history=[]
            for step in range(3):d,m,v,row=advance(d,m,v,step);history.append(row)
            atomic_write(path,{'profile':'known'},3,d,m,v,history)
            payload=load(path,{'profile':'known'},60,2);a,b,c,rows=replay(payload,[1.,-2.],advance)
            self.assertEqual((a,b,c),(d,m,v));self.assertEqual(len(rows),3)
            self.assertFalse(list(Path(folder).glob('*.pending-*')))

    def test_tamper_stale_and_truncated_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as folder:
            path=Path(folder)/'checkpoint.json';d,m,v,row=advance([1.],[0.],[0.],0);atomic_write(path,{'profile':'known'},1,d,m,v,[row]);original=path.read_bytes()
            with self.assertRaises(ValueError):load(path,{'profile':'other'},60,1)
            document=json.loads(original);document['payload']['m_hex'][0]=float(3).hex();path.write_bytes(canonical(document))
            with self.assertRaises(ValueError):load(path,{'profile':'known'},60,1)
            path.write_bytes(original[:len(original)//2])
            with self.assertRaises(ValueError):load(path,{'profile':'known'},60,1)

    def test_self_consistent_hash_does_not_bypass_prefix_replay(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as folder:
            path=Path(folder)/'checkpoint.json';d,m,v,row=advance([1.],[0.],[0.],0)
            atomic_write(path,{'profile':'known'},1,d,[999.],v,[row]);payload=load(path,{'profile':'known'},60,1)
            with self.assertRaises(ValueError):replay(payload,[1.],advance)

if __name__=='__main__':unittest.main()
