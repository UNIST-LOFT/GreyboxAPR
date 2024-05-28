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

    valid_patch_set:Dict[str,set]=dict()

    # Casino
    casino_time_until_finish=[]
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
            casino_time_until_finish.append(round((total_time)/60))

    print(np.mean([len(l) for l in casino_result]))

    # Original
    orig_time_until_finish=[]
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
        orig_time_until_finish.append(round((total_time)/60))

    print(len(orig_result))

    # Greybox
    greybox_time_until_finish=[]
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
                if 'fail_time' in cache[loc]:
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
            greybox_time_until_finish.append(round((total_time)/60))

    print(np.mean([len(l) for l in greybox_result]))

    plt.clf()
    print(mode)

    # Original tool
    if mode=='tbar': name='TBar'
    elif mode=='fixminer': name='Fixminer'
    elif mode=='kpar': name='kPar'
    elif mode=='avatar': name='Avatar'
    elif mode=='recoder': name='Recoder'
    elif mode=='alpharepair': name='AlphaRepair'

    plt.ylabel('Time (m)')

    plt.boxplot([np.array(greybox_time_until_finish),np.array(casino_time_until_finish),np.array(orig_time_until_finish)],
                labels=['Gasino','Casino',name],showmeans=True)
    plt.savefig(f'max-time-{mode}-box.pdf',bbox_inches='tight')
    plt.savefig(f'max-time-{mode}-box.jpg',bbox_inches='tight')

if __name__=='__main__':
    o,a=getopt(argv[1:],'',['with-mockito'])
    for opt,arg in o:
        if o=='--with-mockito':
            WITH_MOCKITO=True

    plot_patches_ci_java(a[0])