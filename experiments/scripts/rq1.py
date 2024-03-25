from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd
from os import path
from sys import argv

import d4j

MAX_EXP=50

def plot_patches_ci_java(mode='tbar'):
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]

    # Casino
    for i in range(MAX_EXP):
        casino_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
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
                    casino_result[-1].append(round((time)/60))

                # if time>3600:
                #     break
    print(np.mean([len(l) for l in casino_result]))
                    
    # Greybox
    for i in range(MAX_EXP):
        greybox_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            try:
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            total_time=0.
            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                if res['config'][0]['location'] not in cache:
                    # If Casino mode did not try this pacth
                    total_time+=prev_time
                else:
                    prev_time=cache[res['config'][0]['location']]['fail_time']+cache[res['config'][0]['location']]['pass_time']
                    total_time+=prev_time
                loc=res['config'][0]['location']

                if is_plausible:
                    greybox_result[-1].append(round((total_time)/60))

                # if time>3600:
                #     break
    print(np.mean([len(l) for l in greybox_result]))

    # Original
    for result in d4j.D4J_1_2_LIST:
        if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
            # Skip if experiment not end
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
                orig_result.append(round((time)/60))

            # if time>3600:
            #     break
    print(len(orig_result))

    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(4,3))
    print(mode)

    # Original tool
    if mode=='tbar': name='TBar'
    elif mode=='fixminer': name='Fixminer'
    elif mode=='kpar': name='kPar'
    elif mode=='avatar': name='Avatar'
    elif mode=='recoder': name='Recoder'
    elif mode=='alpharepair': name='AlphaRepair'

    # Original
    results=sorted(orig_result)
    other_list=[0]
    for i in range(0,301):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,302)),other_list,'-.b',label=name)

    # Casino
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_result[j])
        guided_list.append([0])
        for i in range(0,301):
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
            # if i%60==0:
            #     temp_[i//60].append(guided_list[-1][-1])
    guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Casino')
    # for i in range(5):
    #     print(f'{i*60}: {np.std(temp_[i])}')

    # Greybox
    other_list:List[List[int]]=[]
    other_x=[]
    other_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greybox_result[j])
        other_list.append([0])
        for i in range(0,301):
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
            # if i%500==0:
            #     temp_[i//500].append(other_list[-1][-1])
    other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
    seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Greybox',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Time (min)',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq1-{mode}.pdf',bbox_inches='tight')

if __name__=='__main__':
    plot_patches_ci_java(argv[1])