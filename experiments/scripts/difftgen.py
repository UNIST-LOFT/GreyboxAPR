import subprocess
import shutil
import os
import sys

def run(tool:str, procs: int):
    root_dir = os.path.abspath("..")
    difftgen_dir = os.path.abspath(f"{root_dir}/DiffTGen")
    result=subprocess.run(['python3','script/extract-candidates.py',tool.lower(), root_dir, f'patches/{tool.lower()}'],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    result=subprocess.run(['python3','script/driver.py', root_dir, tool.lower(), f'patches/{tool.lower()}', str(procs)],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    result=subprocess.run(['python3','script/check-results.py', root_dir, tool.lower(),f'patches/{tool.lower()}'],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    
    shutil.copytree(f'{difftgen_dir}/out/{tool.lower()}/{tool.lower()}.csv',f'{tool.lower()}/difftgen.csv',dirs_exist_ok=True)
    
procs = 96
if len(sys.argv) > 1:
    procs = int(sys.argv[1])
run('TBar', procs)
run('Fixminer', procs)
run('kPar', procs)
run('Avatar', procs)
run('Recoder', procs)
run('AlphaRepair', procs)