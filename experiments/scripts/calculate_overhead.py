import os
import d4j
import sys
import numpy as np

def parse_time(path:str):
    with open(path,'r') as f:
        for line in f:
            if line.startswith('Test time:'):
                return float(line.split()[-1])

MAX_EXP=10

def calculate(project:str,tool:str):
    res=[]
    global MAX_EXP
    if not os.path.exists(f'{tool}/result/{project}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
        # Skip if experiment not end
        return

    if not os.path.exists(f'{tool}/result/{project}-orig/simapr-finished.txt'):
         return
    
    orig_time=parse_time(f'{tool}/result/{project}-orig/simapr-finished.txt')
    for i in range(MAX_EXP):
        if os.path.exists(f'{tool}/result/{project}-greybox-{i}/simapr-finished.txt'):
            greybox_time=parse_time(f'{tool}/result/{project}-greybox-{i}/simapr-finished.txt')
            try:
                print(f'{greybox_time},{orig_time},{greybox_time-orig_time},{(greybox_time-orig_time)/orig_time},{(greybox_time-orig_time)/greybox_time}',file=sys.stdout)
                res.append((greybox_time-orig_time)/orig_time)
            except ZeroDivisionError:
                pass

    return res
tool=sys.argv[1]

final_res=[]
for project in d4j.D4J_1_2_LIST:
    res=calculate(project,tool)
    if res:
        final_res+=res

print(f'{np.mean(final_res)},{np.std(final_res)}',file=sys.stderr)