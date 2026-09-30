"""CPU-only batch ABI and temporal interpolation adversary; not GPU measurements."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_batch_inputs import pack_batch
from frontier_inputs import pack_frontier
from exp005_chain_fixture import chain_fixture,set_fields,analytic_fields


class BatchTests(unittest.TestCase):
    def test_one_eight_thirtytwo_are_raw_inputs_with_shared_scene(self):
        base=chain_fixture(4)
        for count in (1,8,32):
            snapshots=[]
            for i in range(count):
                state=copy.deepcopy(base);set_fields(state,[complex(i+1,j-i) for j in range(5)])
                snapshots.append(state)
            batch=pack_batch(snapshots,mode_cap=5)
            self.assertEqual(batch.input_count,count)
            self.assertEqual(batch.sources,tuple(x for s in snapshots for x in pack_frontier(s,mode_cap=5).sources))
            self.assertEqual(batch.geometry,pack_frontier(base,mode_cap=5).geometry)
            self.assertLess(batch.estimated_texture_bytes(),1024*1024)

    def test_one_invalid_or_changed_input_rejects_entire_batch(self):
        base=chain_fixture(3)
        for changed in (chain_fixture(3,treatment='phase'),chain_fixture(3,treatment='lambda')):
            with self.assertRaises(ValueError):pack_batch([base,changed],mode_cap=5)
        bad=copy.deepcopy(base);bad['sources'][0]['field_reim']=[float('nan'),0]
        with self.assertRaises(ValueError):pack_batch([base,bad],mode_cap=5)
        for items in ([],[base]*33,{}):
            with self.assertRaises(ValueError):pack_batch(items,mode_cap=5)

    def test_interpolating_equal_endpoint_intensities_misses_phase_change(self):
        # Actual independent chain oracle, not a rendered animation. Same
        # intensity endpoints with phase0/2pi do NOT imply their midpoint.
        import math
        values=[1+0j,0j,0j]
        a=analytic_fields(2,values,phase_shift=0.)
        b=analytic_fields(2,values,phase_shift=2*math.pi)
        middle=analytic_fields(2,values,phase_shift=math.pi)
        self.assertLess(max(abs(abs(a[p])**2-abs(b[p])**2) for p in a),1e-12)
        error=max(abs((abs(a[p])**2+abs(b[p])**2)/2-abs(middle[p])**2) for p in a)
        self.assertGreater(error,.1)


if __name__=='__main__':unittest.main()
