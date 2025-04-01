import d4j_fixminer
import subprocess
import multiprocessing as mp

def run(project):
   for i in range(10):
      result_path=f'/root/project/GreyboxAPR/experiments/fixminer/result/{project}-greybox-fieldonly-{i}'
      field_path=f'/root/project/GreyboxAPR/experiments/fixminer/result/field/{project}'
      print(f'Running {project}-greybox-fieldonly-{i}')
      result=subprocess.run(['python3','/root/project/GreyboxAPR/SimAPR/simulate-greybox.py',result_path,field_path],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
      with open(f'result/{project}-greybox-fieldonly-{i}/simulate.log','w') as f:
         f.write(result.stdout)
      print(f'Finish {project}-greybox-fieldonly-{i} with returncode {result.returncode}')

      result_path=f'/root/project/GreyboxAPR/experiments/fixminer/result/{project}-greyboxfd-{i}'
      print(f'Running {project}-greyboxfd-{i}')
      result=subprocess.run(['python3','/root/project/GreyboxAPR/SimAPR/simulate-greybox.py',result_path,field_path],
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
      with open(f'result/{project}-greyboxfd-{i}/simulate.log','w') as f:
         f.write(result.stdout)
      print(f'Finish {project}-greyboxfd-{i} with returncode {result.returncode}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    
pool=mp.Pool(int(argv[1]))

for i in range(1,d4j_fixminer.CHART_SIZE+1):
   pool.apply_async(run,(f'Chart_{i}',))
for i in range(1,d4j_fixminer.CLOSURE_SIZE+1):
   pool.apply_async(run,(f'Closure_{i}',))
for i in range(1,d4j_fixminer.LANG_SIZE+1):
   pool.apply_async(run,(f'Lang_{i}',))
for i in range(1,d4j_fixminer.MATH_SIZE+1):
   pool.apply_async(run,(f'Math_{i}',))
# for i in range(1,d4j_fixminer.MOCKITO_SIZE+1):
#    if i in d4j_fixminer.MOCKITO_SKIP: continue
#    pool.apply_async(run,(f'Mockito_{i}',))
for i in range(1,d4j_fixminer.TIME_SIZE+1):
   pool.apply_async(run,(f'Time_{i}',))

pool.close()
pool.join()
