import d4j_kpar
import subprocess
import multiprocessing as mp
import seeds

def run(project):
   print(f'Run {project}-orig')
   result=subprocess.run(['python3','search-kpar-orig.py',project],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   with open(f'result/{project}-orig.log','w') as f:
      f.write(result.stdout.decode("utf-8"))
   print(f'Finish {project}-orig with returncode {result.returncode}')

   for i in range(10):
      print(f'Run {project}-casino-{i}')
      result=subprocess.run(['python3','search-kpar-casino.py',project,str(seeds.SEEDS[i]),str(i)],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'result/{project}-casino-{i}.log','w') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-casino-{i} with returncode {result.returncode}')

      print(f'Run {project}-greybox-{i}')
      result=subprocess.run(['python3','search-kpar-greybox.py',project,str(seeds.SEEDS[i]),str(i)],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'result/{project}-greybox-{i}.log','w') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')

      print(f'Run {project}-greybox-fieldonly-{i}')
      result=subprocess.run(['python3','search-kpar-greybox-fieldonly.py',project,str(seeds.SEEDS[i]),str(i)],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'result/{project}-greybox-fieldonly-{i}.log','w') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greybox-fieldonly-{i} with returncode {result.returncode}')

      print(f'Run {project}-greyboxfd-{i}')
      result=subprocess.run(['python3','search-kpar-greyboxfd.py',project,str(seeds.SEEDS[i]),str(i)],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'result/{project}-greyboxfd-{i}.log','w') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-greyboxfd-{i} with returncode {result.returncode}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    
pool=mp.Pool(int(argv[1]))

for i in range(1,d4j_kpar.CHART_SIZE+1):
   pool.apply_async(run,(f'Chart_{i}',))
for i in range(1,d4j_kpar.CLOSURE_SIZE+1):
   pool.apply_async(run,(f'Closure_{i}',))
for i in range(1,d4j_kpar.LANG_SIZE+1):
   pool.apply_async(run,(f'Lang_{i}',))
for i in range(1,d4j_kpar.MATH_SIZE+1):
   pool.apply_async(run,(f'Math_{i}',))
# for i in range(1,d4j_kpar.MOCKITO_SIZE+1):
#    if i in d4j_kpar.MOCKITO_SKIP: continue
#    pool.apply_async(run,(f'Mockito_{i}',))
for i in range(1,d4j_kpar.TIME_SIZE+1):
   pool.apply_async(run,(f'Time_{i}',))

pool.close()
pool.join()
