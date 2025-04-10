import d4j_srepair
import subprocess
import multiprocessing as mp

def run(project_queue,core):
    while not project_queue.empty():
        project=project_queue.get()
        print(f'Run {project}')
        result=subprocess.run(['python3','srepair.py',project,str(core)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        with open(f'result/{project}-srepair.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
        print(f'Finish {project} with returncode {result.returncode}')

queue=mp.Manager().Queue()

for i in range(1,d4j_srepair.CHART_SIZE+1):
    queue.put(f'Chart_{i}')
for i in range(1,d4j_srepair.CLOSURE_SIZE+1):
    queue.put(f'Closure_{i}')
for i in range(1,d4j_srepair.LANG_SIZE+1):
    queue.put(f'Lang_{i}')
for i in range(1,d4j_srepair.MATH_SIZE+1):
    queue.put(f'Math_{i}')
for i in range(1,d4j_srepair.MOCKITO_SIZE+1):
    if i in d4j_srepair.MOCKITO_SKIP: continue
    queue.put(f'Mockito_{i}')
for i in range(1,d4j_srepair.TIME_SIZE+1):
    queue.put(f'Time_{i}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of GPU cores>')
    exit(1)

procs=[]
for i in range(int(argv[1])):
    proc=mp.Process(target=run,args=(queue,i))
    procs.append(proc)
for proc in procs:
    proc.start()
for proc in procs:
    proc.join()