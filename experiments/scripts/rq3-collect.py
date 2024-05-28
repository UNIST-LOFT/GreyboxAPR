from getopt import getopt
import os
from sys import argv
from typing import Dict, List
import json

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

def plot_patches_ci_java(mode='tbar'):
    orig_result:List[int]=[]
    wo_vertical:List[List[int]]=[[] for _ in range(MAX_EXP)]
    greybox_result:List[List[int]]=[[] for _ in range(MAX_EXP)]
    casino_result:List[List[int]]=[[] for _ in range(MAX_EXP)]

    # Casino
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt') or \
                        not os.path.exists(f'{mode}/result/{result}-wo-vertical-{MAX_EXP-1}/simapr-finished.txt'):
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

    print(np.mean([len(l) for l in casino_result]))

    # w/o vertical
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt') or \
                        not os.path.exists(f'{mode}/result/{result}-wo-vertical-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
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

    print(np.mean([len(l) for l in wo_vertical]))

    # greybox
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt') or \
                        not os.path.exists(f'{mode}/result/{result}-wo-vertical-{MAX_EXP-1}/simapr-finished.txt'):
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
    
    print(np.mean([len(l) for l in greybox_result]))

    # Original
    for result in d4j.D4J_1_2_LIST:
        if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt') or \
                    not os.path.exists(f'{mode}/result/{result}-wo-vertical-{MAX_EXP-1}/simapr-finished.txt'):
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

    print(len(orig_result))

    with open(f'rq3-{mode}.json','w') as f:
        json.dump({
            'orig':orig_result,
            'wo_vertical':wo_vertical,
            'greybox':greybox_result,
            'casino':casino_result
        },f,indent=4)

    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=sorted(orig_result)
    other_list=[0]
    for i in range(0,MAX_ITERATION):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+1)),other_list,'-.b',label='Orig')

    # Casino
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_result[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION+1):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1]+cur_result.count(i))
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'# of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='# of valid patches',color='g',label='Casino')

    # w/o vertical
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(wo_vertical[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION+1):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1]+cur_result.count(i))
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'# of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='# of valid patches',color='y',label='w/o 1st vert.')

    # greybox
    other_list:List[List[int]]=[]
    other_x=[]
    other_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greybox_result[j])
        other_list.append([0])
        for i in range(0,MAX_ITERATION+1):
            if i in cur_result:
                other_list[-1].append(other_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                other_x.append(i)
                if i==0:
                    other_y.append(0)
                else:
                    other_y.append(other_y[-1]+cur_result.count(i))
            else:
                other_list[-1].append(other_list[-1][-1])
                other_x.append(i)
                if i==0:
                    other_y.append(0)
                else:
                    other_y.append(other_y[-1])
    other_df=pd.DataFrame({'Iteration':other_x,'# of valid patches':other_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='# of valid patches',color='r',label='Gasino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Time (min)',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    if WITH_MOCKITO:
        plt.savefig(f'rq3-{mode}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-{mode}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'rq3-{mode}.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-{mode}.jpg',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])