from getopt import getopt
import os
from sys import argv
from typing import Dict, List, Tuple
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

def get_ranking_info_tbar(mode='tbar'):
    greybox_result:List[List[Tuple[int,int]]]=[[] for _ in range(MAX_EXP)]
    casino_result:List[List[Tuple[int,int]]]=[[] for _ in range(MAX_EXP)]
    orig_result:List[Tuple[int,int]]=[]

    with open(f'{mode}/difftgen.csv','r') as f:
        lines=f.readlines()
        correct=dict()
        for line in lines:
            if line[0]!='#':
                cur_line=line.split(',')
            else:
                continue
            cur_ver=cur_line[0].strip().replace('-','_')
            correct[cur_ver]=[]
            for i in range(1,len(cur_line)):
                correct[cur_ver].append(cur_line[i].strip())

    # Casino
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            try:
                simapr_result=open(f'{mode}/result/{result}-casino-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(simapr_result)
            simapr_result.close()

            cur_result=dict()
            for res in root:
                is_plausible=res['pass_result']
                time=res['time']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if is_plausible:
                    # cur_result[loc]=round(time/60)
                    cur_result[loc]=iteration

            result_file=open(f'ods-{mode}.csv','r')

            cur_rank=0
            for res in result_file:
                cur_rank+=1
                is_correct=False
                id=res.split(',')[0]
                if result in correct:
                    if id in correct[result]:
                        is_correct=True
                
                if is_correct:
                    casino_result[i].append((cur_result[id],cur_rank))
                    break

            result_file.close()

    # Greybox
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            try:
                simapr_result=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(simapr_result)
            simapr_result.close()

            cur_result=dict()
            for res in root:
                is_plausible=res['pass_result']
                time=res['time']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if is_plausible:
                    # cur_result[loc]=round(time/60)
                    cur_result[loc]=iteration

            result_file=open(f'ods-{mode}.csv','r')

            cur_rank=0
            for res in result_file:
                cur_rank+=1
                is_correct=False
                id=res.split(',')[0]
                if result in correct:
                    if id in correct[result]:
                        is_correct=True
                
                if is_correct:
                    greybox_result[i].append((cur_result[id],cur_rank))
                    break

            result_file.close()

    # original
    for result in d4j.D4J_1_2_LIST:
        if not WITH_MOCKITO and 'Mockito' in result:
            continue
        if not os.path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
        try:
            simapr_result=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
        except:
            continue
        root=json.load(simapr_result)
        simapr_result.close()

        cur_result=dict()
        for res in root:
            is_plausible=res['pass_result']
            time=res['time']
            iteration=res['iteration']
            loc=res['config'][0]['location']
            if is_plausible:
                # cur_result[loc]=round(time/60)
                cur_result[loc]=iteration

        result_file=open(f'ods-{mode}.csv','r')

        cur_rank=0
        for res in result_file:
            cur_rank+=1
            is_correct=False
            id=res.split(',')[0]
            if result in correct:
                if id in correct[result]:
                    is_correct=True
            
            if is_correct:
                orig_result.append((cur_result[id],cur_rank))
                break

        result_file.close()

    with open(f'rq2-{mode}.json','w') as f:
        json.dump({
            'orig':orig_result,
            'greybox':greybox_result,
            'casino':casino_result
        },f,indent=4)

    # Top-1
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=[]
    for time,rank in orig_result:
        if rank==1:
            results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+1)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result:
            if rank==1:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='r',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result:
            if rank==1:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='y',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-1-{mode}.pdf',bbox_inches='tight')

    # Top-5
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=[]
    for time,rank in orig_result:
        if rank<=5:
            results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+1)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result:
            if rank<=5:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='r',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result:
            if rank<=5:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='y',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-5-{mode}.pdf',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

get_ranking_info_tbar(a[0])