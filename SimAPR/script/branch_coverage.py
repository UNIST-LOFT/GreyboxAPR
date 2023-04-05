import json
import os
import sys
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import sklearn.manifold


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

def parse_simapr_result(output_file:str):
    valid_patches=[]
    invalid_patches=[]
    with open(f'{output_file}/simapr-result.json','r') as f:
        root=json.load(f)

    for patch in root:
        patch_id=patch['config'][0]['location']
        if patch['pass_result']:
            valid_patches.append(patch_id)
        elif patch['compilable']:
            invalid_patches.append(patch_id)
    
    return valid_patches,invalid_patches

def get_all_cov_info(branch_dir:str):
    all_cov:Dict[str,Dict[int,int]]=dict()
    original_cov:Dict[int,int]=dict()

    for file in os.listdir(branch_dir):
        if file.startswith('original'):
            original_cov=parse_cov(f'{branch_dir}/{file}')[1]
        else:
            all_cov[file.removesuffix('.txt')]=parse_cov(f'{branch_dir}/{file}')[1]

    return all_cov,original_cov

def tsne(cov:Dict[str,Dict[str,Dict[int,int]]],valid:List[str],invalid:List[str]):
    x=[]
    for test,info in cov.items():
        for patch in valid:
            vector=info[patch]
            cur_x=[]
            for branch,coverage in vector.items():
                cur_x.append([branch,coverage])
            x.append(cur_x)

        for patch in invalid:
            vector=info[patch]
            cur_x=[]
            for branch,coverage in vector.items():
                cur_x.append([branch,coverage])
            x.append(cur_x)

        tsne_plot=sklearn.manifold.TSNE()
        x_2d=tsne_plot.fit_transform(np.array(x))
        print(x_2d)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print('Usage: python3 plot_norm.py <output_dir> <branch_dir>')
        exit(1)
    output_dir=sys.argv[1]
    branch_dir=sys.argv[2]

    valid_patches,invalid_patches=parse_simapr_result(output_dir)
    all_cov,original_cov=get_all_cov_info(branch_dir)

    all_cov_test=dict()
    for patch, vector in all_cov.items():
        patch_id,test=patch.split('.java_')
        patch_id+='java'
        patch_id=patch_id.replace('#','/')
        if test not in all_cov_test.keys():
            all_cov_test[test]=dict()
        all_cov_test[test][patch_id]=vector

    tsne(all_cov_test['test1'],valid_patches,invalid_patches)