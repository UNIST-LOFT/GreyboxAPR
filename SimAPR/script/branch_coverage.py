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

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print('Usage: python3 plot_norm.py <output_dir> <branch_dir>')
        exit(1)
    output_dir=sys.argv[1]
    branch_dir=sys.argv[2]
    valid_l1_norms,valid_l2_norms,invalid_l1_norms,invalid_l2_norms=compute_norms(output_dir,branch_dir)
