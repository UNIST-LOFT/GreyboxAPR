import os
from typing import List
import json

import numpy as np
import pandas as pd
import seaborn

import d4j

deps = ['greyboxfd', 'greybox-fieldonly', 'wo-vertical-both']

class AblationResult:
    def __init__(self, name: str, dirname: str, color: str):
        self.name = name
        self.dirname = dirname
        self.color = color
        self.result_list: List[List[int]] = [[] for _ in range(AblationResult.MAX_EXP)]
        
    @staticmethod
    def setGlobalState(mode: str, MAX_EXP: int, MAX_ITERATION: int, WITH_MOCKITO: bool):
        AblationResult.mode = mode
        AblationResult.MAX_EXP = MAX_EXP
        AblationResult.MAX_ITERATION = MAX_ITERATION
        AblationResult.WITH_MOCKITO = WITH_MOCKITO
        
    def check_deps(self, result):
        for dep in deps:
            if not os.path.exists(f'{AblationResult.mode}/result/{result}-{dep}-{AblationResult.MAX_EXP-1}/simapr-finished.txt'):
                return False
        return True
        
    def save_result(self):
        for i in range(AblationResult.MAX_EXP):
            for result in d4j.D4J_1_2_LIST:
                if not self.check_deps(result):
                    # Skip if experiment not end
                    continue
                if not AblationResult.WITH_MOCKITO and 'Mockito' in result:
                    continue

                try:
                    result_file=open(f'{AblationResult.mode}/result/{self.result}-{self.dirname}-{i}/simapr-result.json','r')
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
        for j in range(AblationResult.MAX_EXP):
            cur_result=sorted(self.result_list[j])
            guided_list.append([0])
            for i in range(0,AblationResult.MAX_ITERATION+1):
                if i in cur_result:
                    guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/AblationResult.MAX_EXP)
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