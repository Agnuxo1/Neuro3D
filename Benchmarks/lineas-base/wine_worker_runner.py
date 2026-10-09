"""Ejecuta Tools/train_wine_comparison_v1.py sin modificarlo y escribe el tiempo de CPU del proceso.

Uso: python wine_worker_runner.py <cpu_json> <worker_py> --profile P --out O
"""
import json, runpy, sys, time

cpu_json, worker = sys.argv[1], sys.argv[2]
sys.argv = [worker] + sys.argv[3:]
code = 0
t_wall = time.perf_counter()
try:
    runpy.run_path(worker, run_name="__main__")
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
json.dump({"exit_code": code, "process_cpu_seconds": time.process_time(), "wall_seconds": time.perf_counter() - t_wall},
          open(cpu_json, "w"))
sys.exit(code)
