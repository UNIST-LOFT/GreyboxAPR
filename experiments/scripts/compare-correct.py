import os
from typing import Dict, List
import sys
import json

tool=sys.argv[1]

def parse(file:str):
    result:Dict[int,int]=dict()
    with open(file) as f:
        for line in f:
            if ':' not in line:
                continue
            branch,count=line.strip().split(':')
            try:
                result[int(branch)]=int(count)
            except ValueError:
                pass
    return result

correct_patches:Dict[str,Dict[str,Dict[int,int]]]=dict()
for file in os.listdir('scripts/correct-branch'):
    project,test=file.split('-')
    if project not in correct_patches:
        correct_patches[project]=dict()
    correct_patches[project][test]=parse(f'scripts/correct-branch/{file}')

orig_patches:Dict[str,Dict[str,Dict[int,int]]]=dict()
for project in os.listdir(f'{tool}/result/branch'):
    if project not in correct_patches: continue
    if project not in orig_patches:
        orig_patches[project]=dict()

    for file in os.listdir(f'{tool}/result/branch/{project}'):
        if file.startswith('original'):
            test='_'.join(file.split('_')[1:])
            orig_patches[project][test]=parse(f'{tool}/result/branch/{project}/original_{test}')

def get_diff(source:Dict[int,int],target:Dict[int,int]):
    result:Dict[int,str]=dict()
    for branch in target:
        if branch not in source:
            result[branch]='up'
        elif target[branch]>source[branch]:
            result[branch]='up'
        elif target[branch]<source[branch]:
            result[branch]='down'

    for branch in source:
        if branch not in target:
            result[branch]='down'

    return result

def compare_each_branch(project:str):
    global correct_patches,orig_patches,tool
    if project not in correct_patches or project not in orig_patches:
        return
    
    # diff of correct patches
    correct_diff:Dict[str,Dict[int,str]]=dict()
    for test in orig_patches[project]:
        for _test in correct_patches[project]:
            if _test.endswith(test.replace('::','#')):
                correct_diff[test]=get_diff(correct_patches[project][_test],orig_patches[project][test])
                break

    # diff of each patches
    plau_patches:List[str]=[]
    if not os.path.exists(f'{tool}/result/cache/{project}-cache.json'): return
    with open(f'{tool}/result/cache/{project}-cache.json','r') as f:
        cache=json.load(f)
        for p in cache:
            if cache[p]['plausible']: plau_patches.append(p)

    result:List[int]=[0,0]
    for patch in plau_patches:
        for test in correct_diff:
            if not os.path.exists(f'{tool}/result/branch/{project}/{patch.replace("/","#")}_{test}'): continue
            branch=parse(f'{tool}/result/branch/{project}/{patch.replace("/","#")}_{test}')
            diff=get_diff(branch,orig_patches[project][test])
            for b in diff:
                if b in correct_diff[test]:
                    if diff[b]==correct_diff[test][b]:
                        result[0]+=1
                    else:
                        result[1]+=1

    return result

res:List[int]=[0,0]
for project in correct_patches:
    result=compare_each_branch(project)
    if result:
        res[0]+=result[0]
        res[1]+=result[1]

print(f'Consistent: {res[0]}, Inconsistent: {res[1]}')