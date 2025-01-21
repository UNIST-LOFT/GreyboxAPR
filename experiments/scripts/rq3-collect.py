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

deps = ['greybox', 'wo-vertical']

def save_result(mode: str, dirname: str, result_list: List[List[int]]):
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if check_deps(mode, result):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue

            try:
                result_file=open(f'{mode}/result/{result}-{dirname}-{i}/simapr-result.json','r')
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
                    result_list[i].append(iteration)

    print(name)
    print(np.mean([len(l) for l in result_list]))

class AblationResult:
    def __init__(self, mode: str, name: str, dirname: str, color: str):
        self.mode = mode
        self.name = name
        self.dirname = dirname
        self.color = color
        self.result_list: List[List[int]] = [[] for _ in range(MAX_EXP)]
        
    def check_deps(self, result):
        for dep in deps:
            if not os.path.exists(f'{self.mode}/result/{result}-{dep}-{MAX_EXP-1}/simapr-finished.txt'):
                return False
        return True
        
    def save_result(self):
        for i in range(MAX_EXP):
            for result in d4j.D4J_1_2_LIST:
                if self.check_deps(result):
                    # Skip if experiment not end
                    continue
                if not WITH_MOCKITO and 'Mockito' in result:
                    continue

                try:
                    result_file=open(f'{self.mode}/result/{self.result}-{self.dirname}-{i}/simapr-result.json','r')
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
                        self.result_list[i].append(iteration)

        print(self.name)
        print(np.mean([len(l) for l in self.result_list]))
    
    def draw_plot(self):
        guided_list:List[List[int]]=[]
        guided_x=[]
        guided_y=[]
        for j in range(MAX_EXP):
            cur_result=sorted(self.result_list[j])
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
        seaborn.lineplot(data=guided_df,x='Iteration',y='# of valid patches',color=self.color,label=self.name)

def plot_patches_ci_java(mode='tbar'):
    orig_result:List[int]=[]
    results = [
        # mode, name, dirname, color
        AblationResult(mode, 'wo_vertical_field', 'wo-vertical-field', 'r'), # blackbox x / branch x / field o
        AblationResult(mode, 'wo_vertical_branch', 'wo-vertical-branch', 'g'), # blackbox x / branch o / field x
        AblationResult(mode, 'wo_vertical_both', 'wo-vertical-both', 'b'), # blackbox x / branch o / field o
        AblationResult(mode, 'casino', 'casino', 'c'), # blackbox o / branch x / field x
        AblationResult(mode, 'greybox_field', 'greybox-fieldonly', 'm'), # blackbox o / branch x / field o
        AblationResult(mode, 'greybox_branch', 'greybox', 'y'), # blackbox o / branch o / field x
        AblationResult(mode, 'greybox_both', 'greyboxfd', 'k') # blackbox o / branch o / field o
    ]

    # Save Results
    for result in results:
        result.save_result()

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

    dump_data = { 'orig': orig_result }
    for result in results:
        dump_data[result.name] = result.result_list
    
    with open(f'rq3-{mode}.json','w') as f:
        json.dump(dump_data,f,indent=4)

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

    # Draw plots
    for result in results:
        result.draw_plot()
    
    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
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