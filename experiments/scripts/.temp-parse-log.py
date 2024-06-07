import json
from os import path
from sys import argv
from typing import Dict, Set
import d4j
import random

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000
random.seed(0)

def parse(mode:str):
    casino_result:Dict[str,int]={
        '1st':0,
        'hor':0
    }
    greybox_result:Dict[str,int]={
        '1st':0,
        '2nd':0,
        'hor':0
    }

    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_log=open(f'{mode}/result/{result}-greybox-{i}/simapr-search.log','r')
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            intr_patches:Set[str]=set()
            valid_patches:Set[str]=set()
            for res in root:
                if res['result']:
                    intr_patches.add(res['config'][0]['location'])
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

    print(mode)
    print(f'Greybox: {greybox_result}')
    print(f'Casino: {casino_result}')

parse(argv[1])