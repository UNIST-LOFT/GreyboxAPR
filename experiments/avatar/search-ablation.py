import d4j_avatar
import subprocess
import multiprocessing as mp
import seeds
import os

def run(project):
   for i in range(10):
      print(f'Run {project}-w/o-vertical-branch-{i}')
      result=subprocess.run(['python3','search-avatar-ablation-greybox.py',project,'vertical','branch',str(seeds.SEEDS[i]),str(i)],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      with open(f'result/{project}-wo-vertical-branch-{i}.log','w') as f:
         f.write(result.stdout.decode("utf-8"))
      print(f'Finish {project}-w/o-vertical-branch-{i} with returncode {result.returncode}')
      
      if os.path.exists(f'result/{project}-greybox-fieldonly-{i}.log'):
         print(f'Skip {project}-greybox-fieldonly-{i}')
      else:
         print(f'Run {project}-greybox-fieldonly-{i}')
         result=subprocess.run(['python3','search-avatar-greybox-fieldonly.py',project,str(seeds.SEEDS[i]),str(i)],
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
         with open(f'result/{project}-greybox-fieldonly-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
         print(f'Finish {project}-greybox-fieldonly-{i} with returncode {result.returncode}')
      
      if os.path.exists(f'result/{project}-wo-vertical-field-{i}.log'):
         print(f'Skip {project}-wo-vertical-field-{i}')
      else:
         print(f'Run {project}-w/o-vertical-field-{i}')
         result=subprocess.run(['python3','search-avatar-ablation-greybox.py',project,'vertical','field',str(seeds.SEEDS[i]),str(i)],
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
         with open(f'result/{project}-wo-vertical-field-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
         print(f'Finish {project}-w/o-vertical-field-{i} with returncode {result.returncode}')
      
      if os.path.exists(f'result/{project}-wo-vertical-both-{i}.log'):
         print(f'Skip {project}-wo-vertical-both-{i}')
      else:
         print(f'Run {project}-w/o-vertical-both-{i}')
         result=subprocess.run(['python3','search-avatar-ablation-greybox.py',project,'vertical','both',str(seeds.SEEDS[i]),str(i)],
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
         with open(f'result/{project}-wo-vertical-both-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
         print(f'Finish {project}-w/o-vertical-both-{i} with returncode {result.returncode}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    
pool=mp.Pool(int(argv[1]))

for i in range(1,d4j_avatar.CHART_SIZE+1):
   pool.apply_async(run,(f'Chart_{i}',))
for i in range(1,d4j_avatar.CLOSURE_SIZE+1):
   pool.apply_async(run,(f'Closure_{i}',))
for i in range(1,d4j_avatar.LANG_SIZE+1):
   pool.apply_async(run,(f'Lang_{i}',))
for i in range(1,d4j_avatar.MATH_SIZE+1):
   pool.apply_async(run,(f'Math_{i}',))
# for i in range(1,d4j_avatar.MOCKITO_SIZE+1):
#    if i in d4j_avatar.MOCKITO_SKIP: continue
#    pool.apply_async(run,(f'Mockito_{i}',))
for i in range(1,d4j_avatar.TIME_SIZE+1):
   pool.apply_async(run,(f'Time_{i}',))

pool.close()
pool.join()
