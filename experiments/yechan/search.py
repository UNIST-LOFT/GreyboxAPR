import subprocess
import multiprocessing as mp

def run(project):
   with open(f'experiments/yechan/result/{project}-casino-0.log','w+') as f:
         f.write("is anything happening?")
   #run greybox 10 times
   for i in range(10):
      print(f'Run {project}-casino-{i}')
      seed=i+1
      result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result/{project}-greybox-{seed}-out", "-m", "greybox", "--instr-cp", "/root/project/JPatchInst", "--branch-output", f"experiments/tbar/result/branch/{project}t", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "36000", "-T", "18000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-greybox-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-{seed} with returncode {result.returncode}')

   #run casino 10 times
   for i in range(10):
      print(f'Run {project}-casino-{i}')
      seed=i+1
      result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result/{project}-casino-{i+1}-out", "-m", "casino", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "36000", "-T", "18000", "--seed", f"{seed}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'experiments/yechan/result/{project}-casino-{i}.log','w+') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-casino-{seed} with returncode {result.returncode}')
      
   # run original once
   result=subprocess.run(["python3", "SimAPR/simapr.py", "-o", f"experiments/yechan/tbar/result/{project}-orig-out", "-m", "orig", "-w", f"/root/project/SimAPR/TBar/d4j/{project}", "-t", "36000", "-T", "18000", "--seed", f"{1}", "--use-simulation-mode", f"/root/project/SimAPR/experiments/tbar/result/cache/{project}-cache.json", "-k", "template", "--skip-valid", "--", "python3", "/root/project/SimAPR/SimAPR/script/d4j_run_test.py", "/root/project/SimAPR/TBar/buggy"],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   with open(f'experiments/yechan/result/{project}-orig.log','w+') as f:
      f.write(result.stdout.decode("utf-8"))
   print(f'Finish {project}-orig with returncode {result.returncode}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    

target = ["Closure_115", "Closure_129", "Math_49", "Lang_53", "Mockito_38", "Time_11"]
"""
pool=mp.Pool(int(argv[1]))
for i in target:
   print("I'm running", i)
   pool.apply_async(run,(target))"""
   
with mp.Pool(int(argv[1])) as p:
   p.map(run,target)

