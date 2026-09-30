"""CPU-only escape reference-plane and coherent-power regressions."""
import copy
from pathlib import Path
import unittest

from exp005_cascade_runtime import probes
from exp005_escape_fixture import escape_fixture,ESCAPE
from exp005_gpu_pack import pack_paths
from exp005_scene_properties import decode_scene,sum_declared_channels
from exp005_triangle_oracle import trace_scene


def with_inputs(scene,amps):
    scene=copy.deepcopy(scene)
    for source,amp in zip(scene['sources'],amps): source['field_reim']=[amp.real,amp.imag]
    return scene


class EscapeTests(unittest.TestCase):
    def test_coherent_escape_and_detected_power_balance_all_inputs(self):
        for _,amps in probes():
            scene=with_inputs(escape_fixture(),amps); oracle=trace_scene(scene)
            inputs={s['id']:complex(*s['field_reim']) for s in scene['sources']}
            paths=[dict(p,initial_field=inputs[p['source_id']]) for p in oracle['paths']]
            ledger=sum_declared_channels(decode_scene(scene),paths)
            self.assertEqual(ledger['escape_power'],ledger['powers'][ESCAPE])
            self.assertLess(abs(ledger['escape_power']+ledger['detected_power']-sum(abs(a)**2 for a in amps)),1e-11)
            self.assertLess(max(abs(ledger['fields'][p]-oracle['fields'][p]) for p in ledger['fields']),1e-11)
            self.assertIn(ESCAPE,pack_paths(scene,paths).ports)

    def test_escape_pathwise_intensity_is_a_wrong_control(self):
        oracle=trace_scene(escape_fixture())
        incoherent=sum(abs(p['field'])**2 for p in oracle['paths'] if p['terminal']==ESCAPE)
        self.assertGreater(abs(incoherent-abs(oracle['fields'][ESCAPE])**2),.1)

    def test_boundary_translation_and_reference_translation_are_distinct(self):
        for _,amps in probes():
            base=trace_scene(with_inputs(escape_fixture(),amps))['fields']
            boundary=trace_scene(with_inputs(escape_fixture('boundary_shift'),amps))['fields']
            reference=trace_scene(with_inputs(escape_fixture('reference_shift'),amps))['fields']
            for port in base:
                self.assertLess(abs(boundary[port]-base[port]),1e-11)
                self.assertLess(abs(reference[port]-base[port]*(1j if port==ESCAPE else 1)),1e-11)

    def test_missing_boundary_or_wrong_mode_fails_closed(self):
        absent=escape_fixture(); del absent['objects'][ESCAPE]
        wrong=escape_fixture(); wrong['objects'][ESCAPE]['mode_direction']=(0,1,0)
        reference=escape_fixture(); reference['objects'][ESCAPE]['mode_origin_BU']=(6.03125,4,0)
        for scene in (absent,wrong,reference):
            with self.assertRaises(ValueError): trace_scene(scene)

    def test_phase_is_causal_and_sham_has_no_effect(self):
        base=trace_scene(escape_fixture())['fields']
        phase=trace_scene(escape_fixture('phase'))['fields']
        self.assertGreater(abs(abs(phase[ESCAPE])**2-abs(base[ESCAPE])**2),.001)
        self.assertEqual(base,trace_scene(escape_fixture('sham'))['fields'])


if __name__=='__main__': unittest.main()
