import os
import d4j
import sys

def parse_time(path:str):
    with open(path,'r') as f:
        for line in f:
            if line.startswith('Test time:'):
                return float(line.split()[-1])

MAX_EXP=10

def calculate(project:str,tool:str):
    global MAX_EXP
    if not os.path.exists(f'{tool}/result/{project}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                return

    orig_time=parse_time(f'{tool}/result/{project}-orig/simapr-finished.txt')
    for i in range(MAX_EXP):
        greybox_time=parse_time(f'{tool}/result/{project}-greybox-{i}/simapr-finished.txt')
        print(f'{greybox_time},{orig_time},{greybox_time-orig_time},{(greybox_time-orig_time)/orig_time},{(greybox_time-orig_time)/greybox_time}',file=sys.stdout)

tool=sys.argv[1]

for project in d4j.D4J_1_2_LIST:
    calculate(project,tool)