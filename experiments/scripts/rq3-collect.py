from getopt import getopt
import os
from sys import argv
from typing import Dict, List
import json

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

orig_result:List[int]=[]
wo_vertical:List[List[int]]=[[] for _ in range(MAX_EXP)]
greybox_result:List[List[int]]=[[] for _ in range(MAX_EXP)]
casino_result:List[List[int]]=[[] for _ in range(MAX_EXP)]

def plot_patches_ci_java(mode='tbar'):
    global orig_result,wo_vertical,greybox_result,casino_result
    # Casino
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            try:
                result_file=open(f'{mode}/result/{result}-casino-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    # casino_result[i].append(round((time)/60))
                    casino_result[i].append(iteration)

                # if time>3600:
                #     break

    # w/o vertical
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            try:
                result_file=open(f'{mode}/result/{result}-wo-vertical-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    # wo_vertical[i].append(round((time)/60))
                    wo_vertical[i].append(iteration)

                # if time>3600:
                #     break

    # greybox
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            try:
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    # greybox_result[i].append(round((time)/60))
                    greybox_result[i].append(iteration)

                # if time>3600:
                #     break

    # Original
    for result in d4j.D4J_1_2_LIST:
        try:
            result_file=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
        except:
            continue
        root=json.load(result_file)
        result_file.close()

        prev_time=0.
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                # orig_result.append(round((time)/60))
                orig_result.append(iteration)

            # if time>3600:
            #     break

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])

with open(f'rq3-{a[0]}.json','w') as f:
    json.dump({
        'orig':orig_result,
        'wo_vertical':wo_vertical,
        'greybox':greybox_result,
        'casino':casino_result
    },f,indent=4)