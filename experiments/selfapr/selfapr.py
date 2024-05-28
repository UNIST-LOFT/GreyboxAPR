import subprocess
import getopt
import sys
import os

def main(argv):
    if len(argv) < 2:
        print("Usage: python3 selfapr.py <project> [gpu-core]")
        exit(1)

    bugid = argv[1]
    os.chdir("../../SelfAPR")
    new_env=os.environ.copy()
    os.makedirs("d4j", exist_ok=True)
    print(f"Run SelfAPR: {bugid}")
    opt = "all" 
    if len(argv) > 3:
        opt = argv[3]
    if opt == "all" or opt == "pre":
        cmd = f"conda run -n selfapr python3 0_localize_fault.py {bugid}"
        result = subprocess.run(cmd, shell=True, executable='/bin/bash')
        cmd = f"conda run -n selfapr python3 1_bug_representation.py {bugid}"
        result = subprocess.run(cmd, shell=True, executable='/bin/bash')
    
    if opt == "all" or opt == "gpu":
        if len(argv) > 2:
            new_env["CUDA_VISIBLE_DEVICES"]=argv[2]
        cmd = f"conda run -n selfapr python3 2_test.py {bugid}"
        result=subprocess.run(cmd, env=new_env, shell=True, executable='/bin/bash')
        print(f"SelfAPR finished raw patch gen {bugid} with return code {result.returncode}")
    
    if opt == "all" or opt == "post":
        cmd = f"conda run -n selfapr python3 3_evaluate_patch.py {bugid}"
        result = subprocess.run(cmd, shell=True, executable='/bin/bash')
    
    exit(result.returncode)

if __name__ == "__main__":
    main(sys.argv)