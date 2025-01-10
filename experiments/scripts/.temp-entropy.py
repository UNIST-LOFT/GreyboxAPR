import json
from os import path,listdir
from sys import argv
from typing import Dict, List, Set

from matplotlib import pyplot as plt
import d4j
import random
from scipy.stats import entropy,skew
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

    level_result:Dict[str,Dict[str,List[float]]]={
        'file':{'1st':[],'2nd':[]},
        'func':{'1st':[],'2nd':[]},
        'line':{'1st':[],'2nd':[]},
        'type':{'1st':[],'2nd':[]}
    }

    with open('temp-entropy.json','r') as f:
        _temp=json.load(f)
        greybox_result=_temp['greybox_result']
        level_result=_temp['level_result']

    print(mode)
    print(f'1st: {np.mean(greybox_result["1st"])}, 2nd: {np.mean(greybox_result["2nd"])}')
    print(f'Median 1st: {np.median(greybox_result["1st"])}, 2nd: {np.median(greybox_result["2nd"])}')
    print(f'Skew: {skew(greybox_result["1st"])}, {skew(greybox_result["2nd"])}')

    plt.clf()
    _=plt.figure(figsize=(3,4))
    plt.ylabel('Entropy')
    plt.boxplot([np.array(greybox_result["1st"]),np.array(greybox_result["2nd"])],positions=[0.15,0.75],
                labels=['1st vert.','2nd vert.'],showmeans=True,meanline=True,widths=0.5)
    plt.savefig(f'entropy-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-{mode}.jpg',bbox_inches='tight')

    # file
    plt.clf()
    _=plt.figure(figsize=(3,4))
    plt.ylabel('Entropy')
    plt.boxplot([np.array(level_result['file']["1st"]),np.array(level_result['file']["2nd"])],positions=[0.15,0.75],
                labels=['1st vert.','2nd vert.'],showmeans=True,meanline=True,widths=0.5)
    plt.savefig(f'entropy-file-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-file-{mode}.jpg',bbox_inches='tight')

    # func
    plt.clf()
    _=plt.figure(figsize=(3,4))
    plt.ylabel('Entropy')
    plt.boxplot([np.array(level_result['func']["1st"]),np.array(level_result['func']["2nd"])],positions=[0.15,0.75],
                labels=['1st vert.','2nd vert.'],showmeans=True,meanline=True,widths=0.5)
    plt.savefig(f'entropy-func-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-func-{mode}.jpg',bbox_inches='tight')
    # line
    plt.clf()
    _=plt.figure(figsize=(3,4))
    plt.ylabel('Entropy')
    plt.boxplot([np.array(level_result['line']["1st"]),np.array(level_result['line']["2nd"])],positions=[0.15,0.75],
                labels=['1st vert.','2nd vert.'],showmeans=True,meanline=True,widths=0.5)
    plt.savefig(f'entropy-line-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-line-{mode}.jpg',bbox_inches='tight')
    # type
    plt.clf()
    _=plt.figure(figsize=(3,4))
    plt.ylabel('Entropy')
    plt.boxplot([np.array(level_result['type']["1st"]),np.array(level_result['type']["2nd"])],positions=[0.15,0.75],
                labels=['1st vert.','2nd vert.'],showmeans=True,meanline=True,widths=0.5)
    plt.savefig(f'entropy-type-{mode}.pdf',bbox_inches='tight')
    plt.savefig(f'entropy-type-{mode}.jpg',bbox_inches='tight')

parse(argv[1])