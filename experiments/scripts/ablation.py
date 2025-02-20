from typing import List

import numpy as np
import pandas as pd
import seaborn
import json
import d4j
import os

# Skip if {project}-{item}-{MAX_EXP} not done where item is an item in deps array.
# e.g. check if tbar-greyboxfd-9 is done
deps = ['greybox-fieldonly']

def get_ablation_result_variables(MAX_EXP: int):
    return [
        # name, dirname, MAX_EXP, color
        AblationResult('wo_vertical_field', 'wo-vertical-field', MAX_EXP, 'r'), # blackbox x / branch x / field o
        AblationResult('wo_vertical_branch', 'wo-vertical-branch', MAX_EXP, 'g'), # blackbox x / branch o / field x
        AblationResult('wo_vertical_both', 'wo-vertical-both', MAX_EXP, 'b'), # blackbox x / branch o / field o
        AblationResult('casino', 'casino', MAX_EXP, 'c'), # blackbox o / branch x / field x
        AblationResult('greybox_field', 'greybox-fieldonly', MAX_EXP, 'm'), # blackbox o / branch x / field o
        AblationResult('greybox_branch', 'greybox', MAX_EXP, 'y'), # blackbox o / branch o / field x
        AblationResult('greybox_both', 'greyboxfd', MAX_EXP, 'k') # blackbox o / branch o / field o
    ]

class AblationResult:
    def __init__(self, name: str, dirname: str, MAX_EXP: int, color: str):
        self.name = name
        self.dirname = dirname
        self.color = color
        self.MAX_EXP = MAX_EXP
        self.result_list: List[List[int]] = [[] for _ in range(MAX_EXP)]
        
def check_deps(result: str, mode: str, MAX_EXP: int):
        global deps
        for dep in deps:
            if not os.path.exists(f'{mode}/result/{result}-{dep}-{MAX_EXP-1}/simapr-finished.txt'):
                return False
        return True
    
def get_result_data(result: str, mode: str, dirname: str, MAX_EXP: int, index: int, WITH_MOCKITO: bool):
    if not check_deps(result, mode, MAX_EXP):
        # Skip if experiment not end
        return None
    if not WITH_MOCKITO and 'Mockito' in result:
        return None

    try:
        result_file=open(f'{mode}/result/{result}-{dirname}-{index}/simapr-result.json','r')
    except:
        return None
    root=json.load(result_file)
    result_file.close()
    
    return root

def save_result_iter(ablation_result: AblationResult, mode: str, MAX_ITERATION: int, **kwargs):
    for i in range(ablation_result.MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            root = get_result_data(result, mode, ablation_result.dirname, ablation_result.MAX_EXP, i, kwargs.get('WITH_MOCKITO', False))
            if root == None:
                continue
            
            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    ablation_result.result_list[i].append(iteration)

    print(f'{ablation_result.name}: {np.mean([len(l) for l in ablation_result.result_list])}')
        
def save_result_time(ablation_result: AblationResult, mode: str, MAX_TIME: int, **kwargs):
    for i in range(ablation_result.MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            root = get_result_data(result, mode, ablation_result.dirname, ablation_result.MAX_EXP, i, kwargs.get('WITH_MOCKITO', False))
            if root == None:
                continue
            
            # Read cache to get baseline time
            try:
                cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
            except:
                continue
            cache=json.load(cache_file)
            cache_file.close()

            total_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']
                if loc in cache:
                    total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
                else:
                    if res['time']-total_time>0:
                        total_time+=(res['time']-total_time)

                if is_plausible:
                    if MAX_TIME<round((total_time)/60):
                        MAX_TIME=round((total_time)/60)
                    ablation_result.result_list[i].append(round((total_time)/60))

    print(f'{ablation_result.name}: {np.mean([len(l) for l in ablation_result.result_list])}')
    
def draw_plot(ablation_result: AblationResult, count: int, label: str):
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(ablation_result.MAX_EXP):
        cur_result=sorted(ablation_result.result_list[j])
        guided_list.append([0])
        for i in range(0,count+1):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/ablation_result.MAX_EXP)
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

    df_obj = { '# of valid patches':guided_y }
    df_obj[label] = guided_x
    guided_df=pd.DataFrame(df_obj)
    seaborn.lineplot(data=guided_df,x=label,y='# of valid patches',color=ablation_result.color,label=ablation_result.name)
    print(f'{ablation_result.name} Done')