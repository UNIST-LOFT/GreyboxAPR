import subprocess
import getopt
import sys
import os

def main(argv):
    if len(argv) < 2:
        print("Usage: python3 srepair.py <project> [gpu-core]")
        exit(1)

    bugid = argv[1]
    print(f"Run SRepair: {bugid}")
    cmd = f"python3 run.py {bugid}"
    new_env=os.environ.copy()
    if len(argv) > 2:
        new_env["CUDA_VISIBLE_DEVICES"]=argv[2]
    
    # cmd+=' -skip-extract'
    # cmd+=' -skip-solution'
    # cmd+=' -skip-gen'
    # cmd+=' -skip-postprocess'
    
    os.chdir('../../SRepair')
    result=subprocess.run(cmd, env=new_env, shell=True)
    print(f"SRepair finished bug {bugid} with return code {result.returncode}")
    exit(result.returncode)

if __name__ == "__main__":
    main(sys.argv)