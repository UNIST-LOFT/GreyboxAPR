import d4j_selfapr
import subprocess
import multiprocessing as mp
import os

EXP_DIR = os.path.dirname(os.path.abspath(__file__))

def run(project_queue,core):
    while not project_queue.empty():
        project=project_queue.get()
        print(f'Run {project}')
        result=subprocess.run(['python3','selfapr.py', project, str(core)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT, cwd=EXP_DIR)
        os.makedirs('result', exist_ok=True)
        with open(f'result/{project}-selfapr-post.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
        print(f'Finish {project} with returncode {result.returncode}')

queue=mp.Manager().Queue()

def add_to_queue(queue, bug_id):
    if not os.path.exists(f'/root/GreyboxAPR/SelfAPR/d4j/{bug_id}/switch-info.json'):
        queue.put(bug_id)

for i in range(1,d4j_selfapr.CHART_SIZE+1):
    add_to_queue(queue, f'Chart_{i}')
for i in range(1,d4j_selfapr.CLOSURE_SIZE+1):
    add_to_queue(queue, f'Closure_{i}')
for i in range(1,d4j_selfapr.LANG_SIZE+1):
    add_to_queue(queue, f'Lang_{i}')
for i in range(1,d4j_selfapr.MATH_SIZE+1):
    add_to_queue(queue, f'Math_{i}')
for i in range(1,d4j_selfapr.MOCKITO_SIZE+1):
    if i in d4j_selfapr.MOCKITO_SKIP: continue
    add_to_queue(queue, f'Mockito_{i}')
for i in range(1,d4j_selfapr.TIME_SIZE+1):
    add_to_queue(queue, f'Time_{i}')

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