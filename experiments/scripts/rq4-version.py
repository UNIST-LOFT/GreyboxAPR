from getopt import getopt
from os import path
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

def plot_patches_ci_java(project:str,mode='tbar'):
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[[] for _ in range(MAX_EXP)]
    greybox_result:List[List[int]]=[[] for _ in range(MAX_EXP)]

    # Casino
    for i in range(MAX_EXP):
        if not path.exists(f'{mode}/result/{project}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
            # Skip if experiment not end
            return
        if not WITH_MOCKITO and 'Mockito' in project:
            return
        try:
            result_file=open(f'{mode}/result/{project}-casino-{i}/simapr-result.json','r')
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
        if not path.exists(f'{mode}/result/{project}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
            # Skip if experiment not end
            return
        if not WITH_MOCKITO and 'Mockito' in project:
            return
        try:
            result_file=open(f'{mode}/result/{project}-greybox-{i}/simapr-result.json','r')
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
    if not path.exists(f'{mode}/result/{project}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
        # Skip if experiment not end
        return
    if not WITH_MOCKITO and 'Mockito' in project:
        return
    try:
        result_file=open(f'{mode}/result/{project}-orig/simapr-result.json','r')
    except:
        return
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

    is_available=False
    for l in greybox_result:
        if len(l)>0:
            is_available=True
            break
    if not is_available:
        for l in casino_result:
            if len(l)>0:
                is_available=True
                break
    if not is_available:
        if len(orig_result)>0:
            is_available=True
    
    if not is_available: return
    print(f'{project} Greybox: {np.mean([len(l) for l in greybox_result])}')
    print(f'{project} Casino: {np.mean([len(l) for l in casino_result])}')
    print(f'{project} Original: {len(orig_result)}')
        
    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original tool
    if mode=='tbar': name='TBar'
    elif mode=='fixminer': name='Fixminer'
    elif mode=='kpar': name='kPar'
    elif mode=='avatar': name='Avatar'
    elif mode=='recoder': name='Recoder'
    elif mode=='alpharepair': name='AlphaRepair'
    elif mode=='srepair': name='SRepair'
    elif mode=='selfapr': name='SelfAPR'

    # Original
    results=sorted(orig_result)
    other_list=[0]
    for i in range(0,MAX_ITERATION+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+2)),other_list,'-.b',label=name)

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
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greybox_result[j])
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
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    # plt.locator_params(axis='x',nbins=6)
    plt.yticks(fontsize=15)

    if WITH_MOCKITO:
        plt.savefig(f'{mode}/result/rq4-iter-{mode}-{project}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'{mode}/result/rq4-iter-{mode}-{project}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'{mode}/result/rq4-iter-{mode}-{project}.pdf',bbox_inches='tight')
        plt.savefig(f'{mode}/result/rq4-iter-{mode}-{project}.jpg',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

for result in d4j.D4J_2_LIST:
    plot_patches_ci_java(result,a[0])