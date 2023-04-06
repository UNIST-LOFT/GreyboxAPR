import json
import os
import sys
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import sklearn.manifold

__max_branch_id=0
def parse_cov(cov_file: str):
    """
    :param cov_file: branch coverage file
    :return: branch coverage vector
    """
    global __max_branch_id
    cov=dict()
    covered_branches=[]
    with open(cov_file, 'r') as f:
        for line in f:
            branch=int(line.strip())
            if branch > __max_branch_id:
                __max_branch_id = branch
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

    # Padd uncovered branches with 0
    for file,cov in all_cov.items():
        for branch in range(__max_branch_id+1):
            if branch not in cov.keys():
                cov[branch]=0
    for branch in range(__max_branch_id+1):
        if branch not in original_cov.keys():
            original_cov[branch]=0

    return all_cov,original_cov

def tsne(cov:Dict[str,Dict[str,Dict[int,int]]],valid:List[str],invalid:List[str],out_dir:str):
    x=[]
    for test,info in cov.items():
        for patch in valid:
            if patch not in info.keys():
                continue
            vector=info[patch]
            branches=list(vector.keys())
            sorted_branches=sorted(branches)
            cur_x=[]
            for branch in sorted_branches:
                cur_x.append(vector[branch])
            x.append(cur_x)

        for patch in invalid:
            if patch not in info.keys():
                continue
            vector=info[patch]
            branches=list(vector.keys())
            sorted_branches=sorted(branches)
            cur_x=[]
            for branch in sorted_branches:
                cur_x.append(vector[branch])
            x.append(cur_x)

        tsne_plot=sklearn.manifold.TSNE()
        x_array=np.array(x)
        print(x_array.shape)
        x_2d=tsne_plot.fit_transform(x_array)
        # print(x_2d)
        print(x_2d.shape)

        plt.clf()
        print(len(valid))
        plt.scatter(x_2d[len(valid):,0],x_2d[len(valid):,1],c='b',label='invalid')
        plt.scatter(x_2d[:len(valid),0],x_2d[:len(valid),1],c='r',label='valid')
        plt.legend()
        plt.savefig(f'{out_dir}/{test}.jpg')

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print('Usage: python3 branch_coverage.py <output_dir> <branch_dir>')
        exit(1)
    output_dir=sys.argv[1]
    branch_dir=sys.argv[2]

    valid_patches,invalid_patches=parse_simapr_result(output_dir)
    if len(valid_patches)<=4:
        print('Too few valid patches')
        exit(0)
        
    all_cov,original_cov=get_all_cov_info(branch_dir)

    all_cov_test=dict()
    for patch, vector in all_cov.items():
        patch_id,test=patch.split('.java_')
        patch_id+='.java'
        patch_id=patch_id.replace('#','/')
        if test not in all_cov_test.keys():
            all_cov_test[test]=dict()
        all_cov_test[test][patch_id]=vector

    tsne(all_cov_test,valid_patches,invalid_patches,output_dir)