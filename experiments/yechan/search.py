import subprocess
import multiprocessing as mp
import os

def run(project):
   file_number_per_mode = 10

   #run greybox 10 times
   if  os.path.exists(f"experiments/yechan/alphaRepair/result/{project}-greybox-10-out/simapr-finished.txt"):
      for i in range(1, file_number_per_mode+1):
         print(f'Run {project}-greybox-{i}')
         seed=i
         result=subprocess.run(["python", "SimAPR/simapr.py", "-o", f"experiments/yechan/alphaRepair/result/{project}-greybox-{seed}-out", "--cycle-limit", "3000", "-m", "greybox", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/yechan/alphaRepair/result/branch/{project}", "-w", f"/root/project/SimAPR/AlphaRepair/d4j/{project}", "-t", "420000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/alphaRepair/result/cache/{project}-cache.json", "-k", "learning", "--skip-valid", "--", "python", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/AlphaRepair/buggy"],
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
         with open(f'experiments/yechan/result/{project}-greybox-{i}.log','w+') as f:
            f.write(result.stdout.decode("utf-8"))
         print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')
   else:
      print(f'{project}-greybox-10 already exists')
   """
   #run casino 10 times
   for i in range(1, file_number_per_mode+1):
      print(f'Run {project}-casino-{i}')
      seed=i
      result=subprocess.run(["python", "SimAPR/simapr.py", "-o", f"experiments/yechan/alphaRepair/result/{project}-casino-{seed}-out", "--cycle-limit", "3000", "-m", "casino", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/yechan/alphaRepair/result/branch/{project}", "-w", f"/root/project/SimAPR/AlphaRepair/d4j/{project}", "-t", "420000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/alphaRepair/result/cache/{project}-cache.json", "-k", "learning", "--skip-valid", "--", "python", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/AlphaRepair/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-casino-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-casino-{i} with returncode {result.returncode}')
   
   # run original once
   print(f'Run {project}-orig')
   result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/alphaRepair/result/{project}-orig-out", "-m", "orig", "-w", f"/root/project/SimAPR/AlphaRepair/d4j/{project}", "-t", "420000", "--cycle-limit", "3000", "--seed", f"{1}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/yechan/alphaRepair/result/cache/{project}-cache.json", "-k", "learning", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/AlphaRepair/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   with open(f'experiments/yechan/result/{project}-orig.log','w+') as f:
      f.write(result.stdout.decode("utf-8"))
   print(f'Finish {project}-orig with returncode {result.returncode}')"""
   

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    

target = ['Chart_13', 'Closure_59', 'Chart_1', 'Chart_7', 'Chart_19', 'Closure_23', 'Closure_35']#["Chart_" + str(i) for i in range(1, 27)] + ["Closure_" + str(i) for i in range(1, 134)] + ["Math_" + str(i) for i in range(1, 107)] + ["Lang_" + str(i) for i in range(1, 66)] + ["Time_" + str(i) for i in range(1, 28)]
"""
pool=mp.Pool(int(argv[1]))
for i in target:
   print("I'm running", i)
   pool.apply_async(run,(target))"""
   
with mp.Pool(int(argv[1])) as p:
   p.map(run,target)

