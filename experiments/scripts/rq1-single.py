import os
import shutil
from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd
from os import path
from sys import argv
import multiprocessing as mp

from getopt import getopt

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

excepts = []

def plot_patches_ci_java(result:str, mode='tbar'):
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]
    greyboxfd_result:List[List[int]]=[]

    # Casino
    for i in range(MAX_EXP):
        casino_result.append([])
        if result in excepts:
            continue
        if not path.exists(f'{mode}/result/{result}-greyboxfd-{MAX_EXP-1}/simapr-finished.txt'):
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
                casino_result[-1].append(iteration)

            if iteration>MAX_ITERATION:
                break

    casino_mean=np.mean([len(l) for l in casino_result])
                    
    # Greybox
    for i in range(MAX_EXP):
        greybox_result.append([])
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
                greybox_result[-1].append(iteration)

            if iteration>MAX_ITERATION:
                break

    greybox_mean=np.mean([len(l) for l in greybox_result])
    
    # Greybox with critical field only
    for i in range(MAX_EXP):
        greyboxfd_result.append([])
        try:
            result_file=open(f'{mode}/result/{result}-greybox-fieldonly-{i}/simapr-result.json','r')
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
                greyboxfd_result[-1].append(iteration)

            if iteration>MAX_ITERATION:
                break

    greyboxfd_mean=np.mean([len(l) for l in greyboxfd_result])

    # Original
    try:
        result_file=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
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

        if iteration>MAX_ITERATION:
            break

    orig_mean=len(orig_result)

    if casino_mean==0. and greybox_mean==0. and greyboxfd_mean==0. and orig_mean==0:
        return

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
    
    # Greybox with critical field only
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[],[]]
    for j in range(MAX_EXP):
        cur_result=sorted(greyboxfd_result[j])
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
    seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='y',label='Gresino+',linestyle='dotted')

    plt.legend(fontsize=11)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    # plt.locator_params(axis='x',nbins=6)
    plt.yticks(fontsize=15)

    if WITH_MOCKITO:
        plt.savefig(f'scripts/rq1-single/{mode}-{result}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'scripts/rq1-single/{mode}-{result}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'scripts/rq1-single/{mode}-{result}.pdf',bbox_inches='tight')
        plt.savefig(f'scripts/rq1-single/{mode}-{result}.jpg',bbox_inches='tight')

if __name__=='__main__':
    tool=argv[1]
    result=argv[2]
    plot_patches_ci_java(result, tool)