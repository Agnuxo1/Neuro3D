"""An owned grandchild must terminate when its CPU supervisor reaches deadline."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import psutil

ROOT=Path(__file__).resolve().parents[2]


class BoundedCPUDescendants(unittest.TestCase):
    def test_deadline_terminates_the_owned_tree(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TEMP")) as directory:
            folder=Path(directory)
            child=folder/"child.py"
            child.write_text("import time\ntime.sleep(120)\n",encoding="utf-8")
            owner=folder/"owner.py"
            owner.write_text("import subprocess,sys,time,pathlib\n"
                             "p=subprocess.Popen([sys.executable,sys.argv[1]])\n"
                             "pathlib.Path(sys.argv[2]).write_text(str(p.pid))\n"
                             "time.sleep(120)\n",encoding="utf-8")
            receipt=folder/"receipt.json";pidfile=folder/"child-pid.txt"
            command=[sys.executable,str(ROOT/"Tools/run_bounded_cpu_v2.py"),
                     "--receipt",str(receipt),"--stdout",str(folder/"stdout.txt"),
                     "--seconds","8","--rss-mib","256","--free-ram-mib","0","--",
                     sys.executable,str(owner),str(child),str(pidfile)]
            result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=40)
            record=json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(result.returncode,2)
            self.assertEqual(record["reason"],"DEADLINE")
            self.assertTrue(record["owned_worker_terminal"])
            self.assertIn(str(int(pidfile.read_text())),record["owned_descendant_identities"])
            self.assertFalse(psutil.pid_exists(int(pidfile.read_text())))


if __name__=="__main__":unittest.main()
