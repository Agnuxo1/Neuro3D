import copy
import unittest

from audit import audit_record,audit_linear_arrays


def point():
    return {'status':'ok','N':64,'M':64,'params':4096,'rel_error':1e-7,
            'mode':'cells','geometry':'geometry','spp':1,'render_s':.7,'total_s':2.,
            'vram_peak_mb':2494}


class AuditTests(unittest.TestCase):
    def test_execution_ok_does_not_hide_accuracy_failure(self):
        p=point(); p['rel_error']=1
        a=audit_record(p)
        self.assertTrue(a['execution_ok']); self.assertFalse(a['producer_accuracy_within_v1_limit'])
        self.assertFalse(a['candidate_incoherent_case_for_review'])

    def test_cells_is_partial_even_if_accurate(self):
        a=audit_record(point())
        self.assertTrue(a['producer_accuracy_within_v1_limit'])
        self.assertFalse(a['full_gpu_verified']); self.assertFalse(a['eligible_coherent_rt_capacity'])

    def test_integrate_requires_backend_readback_and_safety_proof(self):
        p=point(); p['mode']='integrate'; p['gpu_reduction_verified']=True
        p.update(backend='OPTIX',device='NVIDIA GeForce RTX 3090',blender_version='4.5.14',
                 backend_log_sha256='a',input_artifact_sha256='b',readback_artifact_sha256='c',
                 code_sha256='d',ram_free_min_gib=5.,gpu_temp_max_c=70.)
        a=audit_record(p); self.assertTrue(a['candidate_incoherent_case_for_review'])
        self.assertFalse(a['verified_incoherent_capacity'])
        self.assertFalse(a['full_gpu_verified']); self.assertFalse(a['rt_backend_verified'])
        self.assertFalse(a['eligible_coherent_rt_capacity'])
        p['vram_peak_mb']=19*1024
        self.assertFalse(audit_record(p)['candidate_incoherent_case_for_review'])

    def test_invalid_finite_dimensions_and_timing(self):
        for change in ({'rel_error':float('nan')},{'N':True},{'params':1},
                       {'render_s':0},{'total_s':.1},{'vram_peak_mb':0}):
            p=point(); p.update(change)
            self.assertFalse(audit_record(p)['candidate_incoherent_case_for_review'])
            self.assertTrue(audit_record(p)['reasons'])

    def test_record_not_mutated(self):
        p=point(); old=copy.deepcopy(p); audit_record(p); self.assertEqual(p,old)

    def test_independent_signed_matvec_and_zero_reference(self):
        a=audit_linear_arrays([1,2],[[1,-1],[3,4]],[7,7])
        self.assertEqual(a['max_abs_error'],0); self.assertEqual(a['relative_error'],0)
        z=audit_linear_arrays([0,0],[[1,-1],[3,4]],[0,0])
        self.assertIsNone(z['relative_error']); self.assertTrue(z['zero_reference_exact'])
        bad=audit_linear_arrays([0,0],[[1,-1],[3,4]],[1,0])
        self.assertFalse(bad['zero_reference_exact'])

    def test_shape_and_finiteness_fail_closed(self):
        with self.assertRaises(ValueError): audit_linear_arrays([1,2],[[1,2]],[1,2])
        with self.assertRaises(ValueError): audit_linear_arrays([1],[[float('inf')]],[1])


if __name__=='__main__': unittest.main()
