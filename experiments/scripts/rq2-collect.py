from getopt import getopt
import os
from statistics import mean
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

    with open(f'ods-{mode}.csv','r') as f:
        ranks:Dict[str,List[Tuple[str,float]]]=dict()
        for line in f:
            if line.startswith(','): continue
            _,patch,score=line.split(',')
            bug_id,patch_id=patch.split('#')
            patch_id=(patch_id[:-2]+'.java').replace('-','/').replace('_','/')

            if bug_id not in ranks:
                ranks[bug_id]=[]
            ranks[bug_id].append((patch_id,float(score),))

    patch_ranks:Dict[str,List[str]]=dict()
    for bug_id in ranks:
        ranks[bug_id].sort(reverse=True,key=lambda patch: patch[1])
        patch_ranks[bug_id]=[]
        for patch in ranks[bug_id]:
            patch_ranks[bug_id].append(patch[0])

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
            min_rank=500
            cur_patch=None
            for res in root:
                is_plausible=res['pass_result']
                time=res['time']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if is_plausible:
                    # cur_result[loc]=round(time/60)
                    cur_result[loc]=iteration

                    if result in patch_ranks:
                        if loc in patch_ranks[result]:
                            if patch_ranks[result].index(loc)+1<min_rank:
                                min_rank=patch_ranks[result].index(loc)+1
                                cur_patch=loc

            if cur_patch is not None:
                casino_result[i].append((cur_result[cur_patch],min_rank))
    
    print(mean([len(l) for l in casino_result]))

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
            min_rank=500
            cur_patch=None
            for res in root:
                is_plausible=res['pass_result']
                time=res['time']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if is_plausible:
                    # cur_result[loc]=round(time/60)
                    cur_result[loc]=iteration

                    if result in patch_ranks:
                        if loc in patch_ranks[result]:
                            if patch_ranks[result].index(loc)+1<min_rank:
                                min_rank=patch_ranks[result].index(loc)+1
                                cur_patch=loc

            if cur_patch is not None:
                greybox_result[i].append((cur_result[cur_patch],min_rank))

    print(mean([len(l) for l in greybox_result]))

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
        min_rank=500
        cur_patch=None
        for res in root:
            is_plausible=res['pass_result']
            time=res['time']
            iteration=res['iteration']
            loc=res['config'][0]['location']
            if is_plausible:
                # cur_result[loc]=round(time/60)
                cur_result[loc]=iteration

                if result in patch_ranks:
                    if loc in patch_ranks[result]:
                        if patch_ranks[result].index(loc)+1<min_rank:
                            min_rank=patch_ranks[result].index(loc)+1
                            cur_patch=loc

        if cur_patch is not None:
            orig_result.append((cur_result[cur_patch],min_rank))
    
    print(len(orig_result))

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
        for time,rank in casino_result[i]:
            if rank==1:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result[i]:
            if rank==1:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-1-{mode}.jpg',bbox_inches='tight')
    plt.savefig(f'rq2-top-1-{mode}.pdf',bbox_inches='tight')

    # Top-3
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=[]
    for time,rank in orig_result:
        if rank<=3:
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
        for time,rank in casino_result[i]:
            if rank<=3:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result[i]:
            if rank<=3:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-3-{mode}.jpg',bbox_inches='tight')
    plt.savefig(f'rq2-top-3-{mode}.pdf',bbox_inches='tight')

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
        for time,rank in casino_result[i]:
            if rank<=5:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result[i]:
            if rank<=5:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-5-{mode}.jpg',bbox_inches='tight')
    plt.savefig(f'rq2-top-5-{mode}.pdf',bbox_inches='tight')

    # Top-10
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=[]
    for time,rank in orig_result:
        if rank<=10:
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
        for time,rank in casino_result[i]:
            if rank<=10:
                cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino')

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result[i]:
            if rank<=10:
                cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[0]
    guided_y=[0]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
        guided_list.append([0])
        for i in range(0,MAX_ITERATION):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                guided_y.append(guided_y[-1]+cur_result.count(i)/MAX_EXP)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_y[-1])
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-10-{mode}.jpg',bbox_inches='tight')
    plt.savefig(f'rq2-top-10-{mode}.pdf',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

get_ranking_info_tbar(a[0])