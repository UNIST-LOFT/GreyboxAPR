import subprocess
import multiprocessing as mp

def run(project):
   file_number_per_mode = 10
   
   #run greybox 10 times
   for i in range(1, file_number_per_mode+1):
      print(f'Run {project}-greybox-{i}')
      seed=i
      result=subprocess.run(["python", "SimAPR/simapr.py", "-o", f"experiments/yechan/alphaRepair/result/{project}-greybox-{seed}-out", "--cycle-limit", "3000", "-m", "greybox", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/yechan/alphaRepair/result/branch/{project}", "-w", f"/root/project/SimAPR/AlphaRepair/d4j/{project}", "-t", "420000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/yechan/alphaRepair/result/cache/{project}-cache.json", "-k", "learning", "--skip-valid", "--weight-critical-branch", "--", "python", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/AlphaRepair/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-greybox-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')
   
   #run greybox 10 times
   for i in range(1, file_number_per_mode+1):
      print(f'Run {project}-greybox-{i}')
      seed=i
      result=subprocess.run(["python", "SimAPR/simapr.py", "-o", f"experiments/yechan/alphaRepair/result/{project}-greybox-{seed}-out", "--cycle-limit", "3000", "-m", "greybox", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/yechan/alphaRepair/result/branch/{project}", "-w", f"/root/project/SimAPR/AlphaRepair/d4j/{project}", "-t", "420000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/yechan/alphaRepair/result/cache/{project}-cache.json", "-k", "learning", "--skip-valid", "--weight-critical-branch", "--", "python", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/AlphaRepair/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-greybox-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')
   
   
   

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    

target = ["Chart_" + str(i) for i in range(1, 27)] + ["Closure_" + str(i) for i in range(1, 134)] + ["Math_" + str(i) for i in range(1, 107)] + ["Lang_" + str(i) for i in range(1, 66)] + ["Time_" + str(i) for i in range(1, 28)]
"""
pool=mp.Pool(int(argv[1]))
for i in target:
   print("I'm running", i)
   pool.apply_async(run,(target))"""
   
with mp.Pool(int(argv[1])) as p:
   p.map(run,target)

