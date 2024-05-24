from getopt import getopt
from os import path
from sys import argv
from typing import Dict, List
import json

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

orig_result:List[int]=[]
casino_result:List[List[int]]=[[] for _ in range(MAX_EXP)]
greybox_result:List[List[int]]=[[] for _ in range(MAX_EXP)]

def plot_patches_ci_java(mode='tbar'):
    global orig_result,casino_result,greybox_result
    # Casino
    for i in range(MAX_EXP):
        for result in d4j.D4J_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_file=open(f'{mode}/result/{result}-casino-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    casino_result[i].append(iteration)

    # Greybox
    for i in range(MAX_EXP):
        for result in d4j.D4J_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    greybox_result[i].append(iteration)

    # Original
    for result in d4j.D4J_2_LIST:
        if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
            # Skip if experiment not end
            continue
        if not WITH_MOCKITO and 'Mockito' in result:
            continue
        try:
            result_file=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
        except:
            continue
        root=json.load(result_file)
        result_file.close()

        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                orig_result.append(iteration)

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])

with open(f'rq4-{a[0]}.json','w') as f:
    json.dump({
        'orig':orig_result,
        'greybox':greybox_result,
        'casino':casino_result
    },f,indent=4)