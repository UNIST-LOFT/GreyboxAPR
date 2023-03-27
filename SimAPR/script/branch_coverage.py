"""
1. 각 패치별로 branch coverage 계산해서 vector로 파싱
2. 벡터의 N1 norm과 N2 norm 계산
3. pairwise comparison 수행
4. 각 비교 결과를 이용해 plot으로: valid/invalid 패치를 따로 해서 locality 있는지 표시
"""

import json
import os
import sys
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt


def parse_cov(cov_file: str):
    """
    :param cov_file: branch coverage file
    :return: branch coverage vector
    """
    cov=dict()
    covered_branches=[]
    with open(cov_file, 'r') as f:
        for line in f:
            branch=int(line.strip())
            if branch in cov.keys():
                cov[branch]+=1
            else:
                cov[branch]=1
            covered_branches.append(branch)

    return np.array(covered_branches),cov

def get_l1_norm(cov: np.ndarray):
    return np.linalg.norm(cov, ord=1)

def get_l2_norm(cov: np.ndarray):
    return np.linalg.norm(cov, ord=2)

def parse_simapr_result(output_file:str):
    valid_patches=[]
    invalid_patches=[]
    with open(f'{output_file}/simapr-result.json','r') as f:
        root=json.load(f)

    for patch in root:
        patch_id=patch['config'][0]['location']
        if patch['pass_result']:
            valid_patches.append(patch_id)
        else:
            invalid_patches.append(patch_id)
    
    return valid_patches,invalid_patches

def compute_norms(output_file:str,branch_dir:str) -> Tuple[Dict[str,Dict[float,int]],Dict[str,Dict[float,int]],Dict[str,Dict[float,int]],Dict[str,Dict[float,int]]]:
    valid_pathces,invalid_patches=parse_simapr_result(output_file)
    valid_l1_norms,valid_l2_norms,invalid_l1_norms,invalid_l2_norms=dict(),dict(),dict(),dict()
    valid_l1_set,valid_l2_set=set(),set()

    for file in os.listdir(branch_dir):
        patch_id,test_name=file.split('.java_')
        patch_id+='.java'
        patch_id=patch_id.replace('#','/')
        covered_branches,coverage=parse_cov(f'{branch_dir}/{file}')

        l1_norm=get_l1_norm(covered_branches)
        l2_norm=get_l2_norm(covered_branches)

        if patch_id in valid_pathces:
            print(f'{patch_id}: L1: {l1_norm}, L2: {l2_norm}')
            if test_name not in valid_l1_norms.keys():
                valid_l1_norms[test_name]=dict()
            if test_name not in valid_l2_norms.keys():
                valid_l2_norms[test_name]=dict()
            if l1_norm not in valid_l1_norms[test_name].keys():
                valid_l1_norms[test_name][l1_norm]=0
            if l2_norm not in valid_l2_norms[test_name].keys():
                valid_l2_norms[test_name][l2_norm]=0
            valid_l1_norms[test_name][l1_norm]+=1
            valid_l2_norms[test_name][l2_norm]+=1
        elif patch_id in invalid_patches:
            if test_name not in invalid_l1_norms.keys():
                invalid_l1_norms[test_name]=dict()
            if test_name not in invalid_l2_norms.keys():
                invalid_l2_norms[test_name]=dict()
            if l1_norm not in invalid_l1_norms[test_name].keys():
                invalid_l1_norms[test_name][l1_norm]=0
            if l2_norm not in invalid_l2_norms[test_name].keys():
                invalid_l2_norms[test_name][l2_norm]=0
            invalid_l1_norms[test_name][l1_norm]+=1
            invalid_l2_norms[test_name][l2_norm]+=1

    return valid_l1_norms,valid_l2_norms,invalid_l1_norms,invalid_l2_norms

def plot(output_dir:str,valid_l1_norms:Dict[str,Dict[float,int]],valid_l2_norms:Dict[str,Dict[float,int]],invalid_l1_norms:Dict[str,Dict[float,int]],invalid_l2_norms:Dict[str,Dict[float,int]]):
    for test_name in invalid_l1_norms.keys():
        plt.clf()
        if test_name in valid_l1_norms.keys():
            valid_l1=valid_l1_norms[test_name]
            valid_l2=valid_l2_norms[test_name]
        else:
            valid_l1=dict()
            valid_l2=dict()
        invalid_l1=invalid_l1_norms[test_name]
        invalid_l2=invalid_l2_norms[test_name]

        valid_l1_x=[]
        valid_l1_y=[]
        valid_l2_x=[]
        valid_l2_y=[]
        invalid_l1_x=[]
        invalid_l1_y=[]
        invalid_l2_x=[]
        invalid_l2_y=[]

        valid_l1_keys=sorted(list(valid_l1.keys()))
        print('------------------\nvalid L1')
        for norm in valid_l1_keys:
            valid_l1_x.append(norm)
            valid_l1_y.append(valid_l1[norm])
            print(f'{norm}: {valid_l1[norm]}')
        print('------------------\nvalid L2')
        valid_l2_keys=sorted(list(valid_l2.keys()))
        for norm in valid_l2_keys:
            valid_l2_x.append(norm)
            valid_l2_y.append(valid_l2[norm])
            print(f'{norm}: {valid_l2[norm]}')
        print('------------------\ninvalid L1')
        invalid_l1_keys=sorted(list(invalid_l1.keys()))
        for norm in invalid_l1_keys:
            invalid_l1_x.append(norm)
            invalid_l1_y.append(invalid_l1[norm])
            print(f'{norm}: {invalid_l1[norm]}')
        print('------------------\ninvalid L2')
        invalid_l2_keys=sorted(list(invalid_l2.keys()))
        for norm in invalid_l2_keys:
            invalid_l2_x.append(norm)
            invalid_l2_y.append(invalid_l2[norm])
            print(f'{norm}: {invalid_l2[norm]}')

        plt.plot(valid_l1_x,valid_l1_y,'r-',label='valid patch l1')
        plt.plot(valid_l2_x,valid_l2_y,'r--',label='valid patch l2')
        plt.plot(invalid_l1_x,invalid_l1_y,'b-',label='invalid patch l1')
        plt.plot(invalid_l2_x,invalid_l2_y,'b--',label='invalid patch l2')
        plt.legend()
        plt.savefig(f'{output_dir}/{test_name}.jpg')

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print('Usage: python3 plot_norm.py <output_dir> <branch_dir>')
        exit(1)
    output_dir=sys.argv[1]
    branch_dir=sys.argv[2]
    valid_l1_norms,valid_l2_norms,invalid_l1_norms,invalid_l2_norms=compute_norms(output_dir,branch_dir)
    plot(output_dir,valid_l1_norms,valid_l2_norms,invalid_l1_norms,invalid_l2_norms)