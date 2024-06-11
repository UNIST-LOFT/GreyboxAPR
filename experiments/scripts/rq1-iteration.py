from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd
from os import path
from sys import argv

from getopt import getopt

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

def plot_patches_ci_java(mode='tbar'):
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]

    valid_patch_set:Dict[str,set]=dict()

    # Casino
    for i in range(MAX_EXP):
        casino_result.append([])
        for result in d4j.D4J_1_2_LIST:
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

            if result not in valid_patch_set:
                valid_patch_set[result]=set()
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    valid_patch_set[result].add(loc)
                    casino_result[-1].append(iteration)

                if iteration>MAX_ITERATION:
                    break

    print(np.mean([len(l) for l in casino_result]))
                    
    # Greybox
    for i in range(MAX_EXP):
        greybox_result.append([])
        for result in d4j.D4J_1_2_LIST:
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

            if result not in valid_patch_set:
                valid_patch_set[result]=set()
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    valid_patch_set[result].add(loc)
                    greybox_result[-1].append(iteration)

                if iteration>MAX_ITERATION:
                    break

    print(np.mean([len(l) for l in greybox_result]))

    # Original
    for result in d4j.D4J_1_2_LIST:
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

        if result not in valid_patch_set:
            valid_patch_set[result]=set()
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                valid_patch_set[result].add(loc)
                orig_result.append(iteration)

            if iteration>MAX_ITERATION:
                break

    print(len(orig_result))

    # Store valid patch set to csv file
    if WITH_MOCKITO:
        f=open(f'rq1-iter-valid-patch-count-{mode}-w-mockito.csv','w')
    else:
        f=open(f'rq1-iter-valid-patch-count-{mode}.csv','w')
    f.write('project,# of valid patch\n')
    for k,v in valid_patch_set.items():
        f.write(f'{k},{len(v)}\n')

    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(5,3))
    print(mode)

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
    temp_=[[],[],[],[],[],[]]
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
    guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[],[]]
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
    guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    # plt.locator_params(axis='x',nbins=6)
    plt.yticks(fontsize=15)

    if WITH_MOCKITO:
        plt.savefig(f'rq1-iter-{mode}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'rq1-iter-{mode}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'rq1-iter-{mode}.pdf',bbox_inches='tight')
        plt.savefig(f'rq1-iter-{mode}.jpg',bbox_inches='tight')

if __name__=='__main__':
    o,a=getopt(argv[1:],'',['with-mockito'])
    for opt,arg in o:
        if o=='--with-mockito':
            WITH_MOCKITO=True

    plot_patches_ci_java(a[0])