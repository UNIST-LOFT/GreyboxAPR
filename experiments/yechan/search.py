import subprocess
import multiprocessing as mp

def run(project):
   file_number_per_mode = 10
   
   with open(f'experiments/yechan/result/{project}-casino-0.log','w+') as f:
         f.write("is anything happening?")
   #run greybox 10 times
   for i in range(1, file_number_per_mode+1):
      print(f'Run {project}-greybox-{i}')
      seed=i
      result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result_with_weight/{project}-greybox-{seed}-out", "--cycle-limit", "3000", "-m", "greybox", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/tbar/result/branch/{project}t", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "420000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--weight-critical-branch", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-greybox-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')
   """
   #run casino 10 times
   for i in range(1, file_number_per_mode+1):
      print(f'Run {project}-casino-{i}')
      seed=i
      result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result/{project}-casino-{i+1}-out", "-m", "casino", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "420000", "--cycle-limit", "3000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-casino-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-casino-{i} with returncode {result.returncode}')
      
   # run original once
   result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result/{project}-orig-out", "-m", "orig", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "420000", "--cycle-limit", "3000", "--seed", f"{1}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   with open(f'experiments/yechan/result/{project}-orig.log','w+') as f:
      f.write(result.stdout.decode("utf-8"))
   print(f'Finish {project}-orig with returncode {result.returncode}')
   """
   

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    

target = ["Chart_1", "Chart_15", "Closure_115", "Math_49", "Lang_53", "Time_11"] + ["Math_" + str(i) for i in range(1, 31)]
"""
pool=mp.Pool(int(argv[1]))
for i in target:
   print("I'm running", i)
   pool.apply_async(run,(target))"""
   
with mp.Pool(int(argv[1])) as p:
   p.map(run,target)

