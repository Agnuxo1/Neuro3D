"""Run the demo headless. Usage: python run_blender.py <blender.exe> [--train] [--verify] [--render renders]"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
blender, rest = sys.argv[1], sys.argv[2:]
args = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", os.path.join(here, "neuro3d_iris_demo.py"), "--"] + rest
sys.exit(subprocess.call(args, cwd=here))
