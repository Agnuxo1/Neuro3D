"""Native integration tests without launching Blender, render or GPU."""
import ast
from pathlib import Path
import unittest

import exp005_blender_gpu as native


class NativeTests(unittest.TestCase):
    def test_double_split_preserves_scene_lengths_and_phases(self):
        for value in (0.,.1,.101,6.0125,1e-7,-.0125,.37,1.234567891234):
            hi,lo=native.split_double(value)
            self.assertLessEqual(abs((hi+lo)-value),1e-14)
        height,hi,lo=native.texture_data(tuple(range(260)))
        self.assertEqual((height,len(hi),len(lo)),(2,512,512))

    def test_native_dispatch_and_real_reopen_no_render_or_external_context(self):
        code=Path(native.__file__).read_text()
        calls=[ast.unparse(n.func) for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Call)]
        for name in ('gpu.compute.dispatch','gpu.shader.create_from_info','bpy.ops.wm.open_mainfile','raycast_paths'):
            self.assertIn(name,calls)
        self.assertFalse(any('moderngl' in c or c.startswith('bpy.ops.render.') or 'sum_declared_channels' in c for c in calls))
        self.assertEqual((native.FIELD_TOL,native.POWER_TOL),(1e-4,2e-4))

    def test_hidden_launcher_and_shader_readback(self):
        import exp005_hidden_blender as launcher
        self.assertIn('subprocess.SW_HIDE',Path(launcher.__file__).read_text())
        shader=native.SHADER.read_text()
        self.assertIn('imageStore(fields_out',shader)
        self.assertIn('sum_field+=value',shader)
        self.assertIn('double(wavelength_hi)+double(wavelength_lo)',shader)

    def test_shader_owner_released_before_blender_context_shutdown(self):
        code=Path(native.__file__).read_text()
        self.assertLess(code.index('del shader'),code.rindex('schedule_exit(bpy)'))
        self.assertIn('gc.collect()',code)
        self.assertIn('bpy.app.timers.register(close',code)
        self.assertIn('bpy.context.temp_override(window=windows[0])',code)


if __name__=='__main__': unittest.main()
