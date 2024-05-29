import subprocess
import shutil
import os
import sys

def run(tool:str, procs: int):
    root_dir = os.path.abspath("..")
    difftgen_dir = os.path.abspath(f"{root_dir}/DiffTGen")
    result=subprocess.run(['python3','script/extract-candidates.py',tool.lower(), root_dir, f'patches/{tool.lower()}'],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    if result.returncode!=0:
        print(result.stdout.decode('utf-8'))
        print("Error in extract-candidates.py")
        exit(1)
    result=subprocess.run(['python3','script/driver.py', root_dir, tool.lower(), f'patches/{tool.lower()}', str(procs)],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    if result.returncode!=0:
        print(result.stdout.decode('utf-8'))
        print("Error in driver.py")
        exit(1)
    result=subprocess.run(['python3','script/check-results.py', tool.lower(),f'patches/{tool.lower()}'],stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, cwd=difftgen_dir)
    if result.returncode!=0:
        print(result.stdout.decode('utf-8'))
        print("Error in check-results.py")
        exit(1)
    
    shutil.copy(f'{difftgen_dir}/out/{tool.lower()}.csv',f'{tool.lower()}/difftgen.csv')
    
if len(sys.argv) != 3:
    print("Usage: python3 difftgen.py <tool> <num_procs>")
    exit(1)

procs = int(sys.argv[2])
run(sys.argv[1], procs)