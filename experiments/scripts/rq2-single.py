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
    with open(f'scripts/recall-data/rq2-{mode}.json','r') as f:
        data=json.load(f)
        orig_result=data['orig']
        greybox_result=data['greybox']
        casino_result=data['casino']

    # Top-1
    plt.clf()
    fig=plt.figure(figsize=(5,3))

    # Original
    results=[]
    for time,rank in orig_result['top-1']:
        results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+2)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result['top-1'][i]:
            cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
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
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result['top-1'][i]:
            cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
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
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

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
    for time,rank in orig_result['top-3']:
        results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+2)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result['top-3'][i]:
            cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
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
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result['top-3'][i]:
            cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
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
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

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
    for time,rank in orig_result['top-5']:
        results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+2)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result['top-5'][i]:
            cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
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
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result['top-5'][i]:
            cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
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
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

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
    for time,rank in orig_result['top-10']:
        results.append(time)
    results=sorted(results)
    other_list=[0]
    for i in range(0,MAX_ITERATION+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_ITERATION+2)),other_list,'-.b',label='Orig')

    # Casino
    casino_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in casino_result['top-10'][i]:
            cur_result.append(time)
        casino_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_list[j])
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
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

    # Greybox
    genprog_list:List[List[int]]=[]
    for i in range(MAX_EXP):
        cur_result=[]
        for time,rank in greybox_result['top-10'][i]:
            cur_result.append(time)
        genprog_list.append(cur_result)
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(genprog_list[j])
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
    other_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=other_df,x='Iteration',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq2-top-10-{mode}.jpg',bbox_inches='tight')
    plt.savefig(f'rq2-top-10-{mode}.pdf',bbox_inches='tight')

get_ranking_info_tbar('tbar')
get_ranking_info_tbar('avatar')
get_ranking_info_tbar('fixminer')
get_ranking_info_tbar('kpar')
get_ranking_info_tbar('alpharepair')
get_ranking_info_tbar('recoder')
get_ranking_info_tbar('srepair')
get_ranking_info_tbar('selfapr')