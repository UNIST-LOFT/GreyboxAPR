import json
from os import path,listdir
from sys import argv
from typing import Dict, List, Set
import d4j
import random

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000
random.seed(0)

def parse_branch(file_path:str):
    result:Dict[int,int]=dict()
    with open(file_path,'r') as file:
        for line in file:
            if ':' in line and line.count(':')==1:
                id,count=line.split(':')
                try:
                    result[int(id)]=int(count)
                except:
                    pass
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

    casino_result:Dict[str,int]={
        '1st':0,
        'hor':0
    }
    greybox_result:Dict[str,int]={
        '1st':0,
        '2nd':0,
        'hor':0
    }

    casino_update_result=0
    greybox_update_result={
        'blackbox':0,
        'greybox':0
    }

    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/{res_dir}/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_log=open(f'{mode}/{res_dir}/{result}-greybox-{i}/simapr-search.log','r')
                result_file=open(f'{mode}/{res_dir}/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            # Parse original branch coverage
            orig_coverage:Dict[str,Dict[int,int]]=dict()
            for file in listdir(f'{mode}/{res_dir}/branch/{result}'):
                if file.startswith('original_'):
                    test=file.split('original_')[1][:-4]
                    orig_coverage[test]=parse_branch(f'{mode}/{res_dir}/branch/{result}/{file}')

            intr_patches:Set[str]=set()
            valid_patches:Set[str]=set()
            for res in root:
                if res['result']:
                    intr_patches.add(res['config'][0]['location'])
                    greybox_update_result['blackbox']+=4

                    for file in listdir(f'{mode}/{res_dir}/branch/{result}'):
                        if file.startswith(res['config'][0]['location'].replace('/','#')):
                            test=file.split('.java_')[1][:-4]
                            if test not in orig_coverage: continue
                            patch_coverage=parse_branch(f'{mode}/{res_dir}/branch/{result}/{file}')
                            diff=branch_diff(orig_coverage[test],patch_coverage)
                            greybox_update_result['greybox']+=len(diff)*4
                            continue

                if res['pass_result']:
                    valid_patches.add(res['config'][0]['location'])

            if len(valid_patches)==0:
                continue

            for line in result_log:
                if 'Mode of 1st' in line:
                    greybox_result['1st']+=1
                    casino_result['1st']+=1
                elif 'Mode of 2nd' in line:
                    greybox_result['2nd']+=1
                    if random.randint(1,10)<=3:
                        casino_result['1st']+=1
                    else:
                        casino_result['hor']+=1
                elif 'Use original order' in line or 'Use epsilon greedy method' in line:
                    greybox_result['hor']+=1
                    casino_result['hor']+=1

            result_log.close()

            try:
                r_file=open(f'{mode}/{res_dir}/{result}-casino-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(r_file)
            r_file.close()
            for res in root:
                if res['result']:
                    casino_update_result+=1

    print(mode)
    print(f'Greybox: {greybox_result}')
    print(f'Casino: {casino_result}')
    print(f'Greybox: {greybox_update_result}')
    print(f'Casino: {casino_update_result}')

parse(argv[1])