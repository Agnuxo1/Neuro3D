"""Shutdown wrapper CPU mocks, not Blender/GPU evidence."""
from types import SimpleNamespace
import unittest
from exp005_resident_v2 import configure_private_exit


class ExitTests(unittest.TestCase):
    def test_private_exit_never_persists_preferences(self):
        events=[]
        class Setting:
            def __setattr__(self,key,value):
                events.append((key,value));object.__setattr__(self,key,value)
        prefs=Setting();prefs.view=Setting();prefs.filepaths=Setting();events.clear()
        bpy=SimpleNamespace(context=SimpleNamespace(preferences=prefs))
        settings=configure_private_exit(bpy)
        self.assertEqual(events,[('use_preferences_save',False),('use_save_prompt',False),('use_auto_save_temporary_files',False)])
        self.assertFalse(settings['save_user_preferences'])


if __name__=='__main__':unittest.main()
