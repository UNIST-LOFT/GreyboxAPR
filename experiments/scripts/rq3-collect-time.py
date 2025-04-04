import os
from statistics import mean
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
MAX_TIME=300

def plot_patches_ci_java(mode='tbar'):
    global MAX_TIME,MAX_EXP,WITH_MOCKITO
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]
    greybox_field_only_result:List[List[int]]=[]
    greyboxfd_result:List[List[int]]=[]

    valid_patch_set:Dict[str,set]=dict()

    # Casino
    for i in range(MAX_EXP):
        casino_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-fieldonly-{MAX_EXP-1}/simapr-finished.txt'):
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

            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            if result not in valid_patch_set:
                valid_patch_set[result]=set()

            total_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                # time=res['time']
                loc=res['config'][0]['location']
                if loc in cache:
                    total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
                else:
                    if res['time']-total_time>0:
                        total_time+=(res['time']-total_time)

                if is_plausible:
                    if MAX_TIME<round((total_time)/60):
                        MAX_TIME=round((total_time)/60)
                    valid_patch_set[result].add(loc)
                    casino_result[-1].append(round((total_time)/60))

    print(np.mean([len(l) for l in casino_result]))

    # Original
    for result in d4j.D4J_1_2_LIST:
        if not path.exists(f'{mode}/result/{result}-greybox-fieldonly-{MAX_EXP-1}/simapr-finished.txt'):
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

        # Read cache to get baseline time
        try:
            cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
        except:
            continue
        cache=json.load(cache_file)
        cache_file.close()

        if result not in valid_patch_set:
            valid_patch_set[result]=set()

        total_time=0.
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            # time=res['time']
            if loc in cache:
                total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
            else:
                if res['time']-total_time>0:
                    total_time+=(res['time']-total_time)
            loc=res['config'][0]['location']

            if is_plausible:
                if MAX_TIME<round((total_time)/60):
                    MAX_TIME=round((total_time)/60)
                valid_patch_set[result].add(loc)
                orig_result.append(round((total_time)/60))

    print(len(orig_result))

    # Greybox
    for i in range(MAX_EXP):
        greybox_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-fieldonly-{MAX_EXP-1}/simapr-finished.txt'):
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

            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            file_instrument_time:Dict[str,float]=dict()
            with open(f'scripts/file-instrument-time/{result}.txt','r') as f:
                for line in f:
                    file,time=line.strip().split(',')
                    file_instrument_time[file]=float(time)

            total_time=0.
            fail_time_list=[]
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if loc not in cache:
                    total_time+=mean(fail_time_list)
                elif 'fail_time' in cache[loc]:
                    total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
                    fail_time_list.append(cache[loc]['fail_time'])
                else:
                    total_time+=mean(fail_time_list)+cache[loc]['pass_time']
                if is_hq:
                    # Instrumentation time
                    total_time+=file_instrument_time[loc.split('/')[-1]]

                if is_plausible:
                    if MAX_TIME<round((total_time)/60):
                        MAX_TIME=round((total_time)/60)
                    valid_patch_set[result].add(loc)
                    greybox_result[-1].append(round((total_time)/60))

    print(np.mean([len(l) for l in greybox_result]))
    
    # Greybox with critical field
    for i in range(MAX_EXP):
        greyboxfd_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-fieldonly-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_file=open(f'{mode}/result/{result}-greyboxfd-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            if result not in valid_patch_set:
                valid_patch_set[result]=set()

            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            file_instrument_time:Dict[str,float]=dict()
            with open(f'scripts/file-instrument-time/{result}.txt','r') as f:
                for line in f:
                    file,time=line.strip().split(',')
                    file_instrument_time[file]=float(time)

            total_time=0.
            fail_time_list=[]
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if loc not in cache:
                    total_time+=mean(fail_time_list)
                elif 'fail_time' in cache[loc]:
                    total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
                    fail_time_list.append(cache[loc]['fail_time'])
                else:
                    total_time+=mean(fail_time_list)+cache[loc]['pass_time']
                if is_hq:
                    # Instrumentation time
                    total_time+=file_instrument_time[loc.split('/')[-1]]

                if is_plausible:
                    if MAX_TIME<round((total_time)/60):
                        MAX_TIME=round((total_time)/60)
                    valid_patch_set[result].add(loc)
                    greyboxfd_result[-1].append(round((total_time)/60))

    print(np.mean([len(l) for l in greyboxfd_result]))

    # Greybox with only critical field
    for i in range(MAX_EXP):
        greybox_field_only_result.append([])
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-fieldonly-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_file=open(f'{mode}/result/{result}-greybox-fieldonly-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            if result not in valid_patch_set:
                valid_patch_set[result]=set()

            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            file_instrument_time:Dict[str,float]=dict()
            with open(f'scripts/file-instrument-time/{result}.txt','r') as f:
                for line in f:
                    file,time=line.strip().split(',')
                    file_instrument_time[file]=float(time)

            total_time=0.
            fail_time_list=[]
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                loc=res['config'][0]['location']
                if loc not in cache:
                    total_time+=mean(fail_time_list)
                elif 'fail_time' in cache[loc]:
                    total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
                    fail_time_list.append(cache[loc]['fail_time'])
                else:
                    total_time+=mean(fail_time_list)+cache[loc]['pass_time']
                if is_hq:
                    # Instrumentation time
                    total_time+=file_instrument_time[loc.split('/')[-1]]

                if is_plausible:
                    if MAX_TIME<round((total_time)/60):
                        MAX_TIME=round((total_time)/60)
                    valid_patch_set[result].add(loc)
                    greybox_field_only_result[-1].append(round((total_time)/60))

    print(np.mean([len(l) for l in greybox_field_only_result]))

    # Store valid patch set to csv file
    if WITH_MOCKITO:
        f=open(f'rq3-time-valid-patch-count-{mode}-w-mockito.csv','w')
    else:
        f=open(f'rq3-time-valid-patch-count-{mode}.csv','w')
    f.write('project,# of valid patch\n')
    for k,v in valid_patch_set.items():
        f.write(f'{k},{len(v)}\n')

    # Store result for overall plots
    if not os.path.exists('scripts/rq3-time'):
        os.makedirs('scripts/rq3-time')
    with open(f'scripts/rq3-time/{mode}.json','w') as f:
        json.dump({
            'orig':orig_result,
            'casino':casino_result,
            'greybox':greybox_result,
            'greybox_field_only':greybox_field_only_result,
            'greyboxfd':greyboxfd_result},f)

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
    for i in range(0,MAX_TIME+1):
        if i in results:
            other_list.append(other_list[-1]+results.count(i))
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label=name)

    # Casino
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_result[j])
        guided_list.append([0])
        for i in range(0,MAX_TIME+1):
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
    other_list:List[List[int]]=[]
    other_x=[]
    other_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greybox_result[j])
        other_list.append([0])
        for i in range(0,MAX_TIME+1):
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
    other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
    seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino_B',linestyle=':')

    # Greybox with only critical field
    other_list:List[List[int]]=[]
    other_x=[]
    other_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greybox_field_only_result[j])
        other_list.append([0])
        for i in range(0,MAX_TIME+1):
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
    other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
    seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='y',label='Gresino_F',linestyle='-.')
    
    # Greybox with critical field
    other_list:List[List[int]]=[]
    other_x=[]
    other_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(greyboxfd_result[j])
        other_list.append([0])
        for i in range(0,MAX_TIME+1):
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
    other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
    seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='k',label='Gresino_BF',linestyle='--')

    plt.legend(fontsize=11)
    plt.xlabel('Time (min)',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.locator_params(axis='x',nbins=8)
    plt.yticks(fontsize=15)
    if WITH_MOCKITO:
        plt.savefig(f'rq3-time-{mode}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-time-{mode}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'rq3-time-{mode}.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-time-{mode}.jpg',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])