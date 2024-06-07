import json
from os import path,listdir
from sys import argv
from typing import Dict, List, Set

from matplotlib import pyplot as plt
import d4j
import random
from scipy.stats import entropy
import numpy as np

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000
random.seed(0)

def parse_branch(file_path:str):
    result:Dict[int,int]=dict()
    with open(file_path,'r') as file:
        for line in file:
            if ':' in line:
                id,count=line.split(':')
                result[int(id)]=int(count)
    return result

def branch_diff(orig:Dict[int,int],patch:Dict[int,int]):
    result:List[int]=[]
    for key in orig:
        if key not in patch:
            result.append(key)
        elif orig[key]!=patch[key]:
            result.append(key)
    return result

def parse(mode:str):
    if mode=='avatar':
        res_dir='result-temp'
    else:
        res_dir='result'

    greybox_result:Dict[str,List[float]]={
        '1st':[],
        '2nd':[]
    }

    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/{res_dir}/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            result_log=open(f'{mode}/{res_dir}/{result}-greybox-{i}/simapr-search.log','r')

            with np.errstate(invalid='raise'):
                for line in result_log:
                    if 'Prob of 1st' in line:
                        _l=line.split(': ')[-1]
                        mode_list=[]
                        for m in _l.split(','):
                            if m!='\n':
                                if float(m)!=0.:
                                    mode_list.append(float(m))
                        if len(mode_list)>0:
                            greybox_result['1st'].append(entropy(mode_list))
                    elif 'Prob of 2nd' in line:
                        _l=line.split(': ')[-1]
                        mode_list=[]
                        for m in _l.split(','):
                            if m!='\n':
                                if float(m)!=0.:
                                    mode_list.append(float(m))
                        if len(mode_list)>0:
                            greybox_result['2nd'].append(entropy(mode_list))

            result_log.close()

    print(mode)
    print(f'1st: {np.mean(greybox_result["1st"])}, 2nd: {np.mean(greybox_result["2nd"])}')

    plt.ylabel('Entropy')
    plt.boxplot([np.array(greybox_result["1st"]),np.array(greybox_result["2nd"])],
                labels=['1st vert.','2nd vert.'],showmeans=True)
    plt.savefig(f'entropy-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-{mode}.jpg',bbox_inches='tight')

parse(argv[1])