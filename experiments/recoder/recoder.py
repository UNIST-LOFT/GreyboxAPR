import subprocess
import getopt
import sys
import os

def is_d4j2(bug_id):
    subject, bug = bug_id.split("_")
    if subject in ['Chart','Lang','Math','Mockito','Time']:
        return False
    elif subject=='Closure' and 133<=int(bug)<175:
        return True
    else:
        return True
    
def main(argv):
    if len(argv) < 2:
        print("Usage: python3 recoder.py <project> [gpu-core]")
        exit(1)
    
    bugid = argv[1]
    print(f"Run recoder: {bugid}")

    new_env=os.environ.copy()
    if len(argv) > 2:
        new_env["CUDA_VISIBLE_DEVICES"]=argv[2]
    os.chdir("../../Recoder")
    
    if is_d4j2(bugid):
        cmd = f"conda run -n recoder python3 testDefect4j-d4j2.py {bugid}"
    else:
        cmd = f"conda run -n recoder python3 testDefect4j.py {bugid}"
    os.makedirs("d4j", exist_ok=True)
    result=subprocess.run(cmd, env=new_env, executable='/bin/bash', shell=True)
    if result.returncode != 0:
        print(f"Recoder failed to run recoder {bugid}")
        exit(result.returncode)

    result2=subprocess.run(f"conda run -n recoder python3 repair.py {bugid}",env=new_env, shell=True, executable='/bin/bash')
    if result2.returncode != 0:
        print(f"Recoder failed to generate actual patches {bugid}")
        exit(result2.returncode)
    print(f"Recoder finished bug {bugid} with return code {result.returncode}")
    exit(result.returncode)
    
if __name__ == "__main__":
    main(sys.argv)