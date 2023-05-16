import json
import os
import sys
from typing import Dict, List

from benchmarks import *

MAX_EXECUTION=10

def get_result_time(output_file:str):
    try:
        result_file=open(output_file,'r')
    except:
        print(f'Error: {output_file} does not exist')
        sys.exit(1)
        
    root=json.load(result_file)
    result_file.close()

    prev_time=0.
    hq_result:List[int]=[]
    valid_result:List[int]=[]
    for res in root:
        is_hq=res['result']
        is_plausible=res['pass_result']
        iteration=res['iteration']
        time=res['time']
        loc=res['config'][0]['location']

        if is_hq:
            hq_result.append(round(time/60))
        if is_plausible:
            valid_result.append(round(time/60))

    return hq_result,valid_result

def valid_patch_each_project(result_dir:str,max_exp:int,use_casino:bool=True,use_greybox:bool=True,
                             use_orig:bool=True,use_seapr:bool=True):
    casino_result:Dict[str,List[int]]=dict()  # {project: [valid_patches...]}
    if use_casino:
        for project in D4J_1_2_0_LIST:
            for i in range(max_exp):
                result_path=f'{result_dir}/{project}-casino-{i}/simapr-result.json'
                if os.path.exists(result_path):
                    hq_result,valid_result=get_result_time(result_path)
                    
                    if project not in casino_result:
                        casino_result[project]=[]
                    casino_result[project]+=valid_result

    greybox_result:Dict[str,List[int]]=dict()  # {project: [valid_patches...]}
    if use_greybox:
        for project in D4J_1_2_0_LIST:
            for i in range(max_exp):
                result_path=f'{result_dir}/{project}-greybox-{i}/simapr-result.json'
                if os.path.exists(result_path):
                    hq_result,valid_result=get_result_time(result_path)
                    
                    if project not in greybox_result:
                        greybox_result[project]=[]
                    greybox_result[project]+=valid_result

    original_result:Dict[str,List[int]]=dict()  # {project: [valid_patches...]}
    if use_orig:
        for project in D4J_1_2_0_LIST:
            result_path=f'{result_dir}/{project}-orig/simapr-result.json'
            if os.path.exists(result_path):
                hq_result,valid_result=get_result_time(result_path)
                
                if project not in original_result:
                    original_result[project]=[]
                original_result[project]+=valid_result

    seapr_result:Dict[str,List[int]]=dict()  # {project: [valid_patches...]}
    if use_seapr:
        for project in D4J_1_2_0_LIST:
            result_path=f'{result_dir}/{project}-seapr/simapr-result.json'
            if os.path.exists(result_path):
                hq_result,valid_result=get_result_time(result_path)
                
                if project not in seapr_result:
                    seapr_result[project]=[]
                seapr_result[project]+=valid_result

    final_result:Dict[str,Dict[str,List[int]]]=dict()  # {algorithm: {project: [valid_patches...]}}
    if use_casino:
        final_result['casino']=casino_result
    if use_greybox:
        final_result['greybox']=greybox_result
    if use_orig:
        final_result['orig']=original_result
    if use_seapr:
        final_result['seapr']=seapr_result
    
    return final_result

def valid_patch_combine(result_dir:str,max_exp:int,use_casino:bool=True,use_greybox:bool=True,
                             use_orig:bool=True,use_seapr:bool=True):
    casino_result:List[int]=[]  # [valid_patches...]
    if use_casino:
        for project in D4J_1_2_0_LIST:
            for i in range(max_exp):
                result_path=f'{result_dir}/{project}-casino-{i}/simapr-result.json'
                if os.path.exists(result_path):
                    hq_result,valid_result=get_result_time(result_path)
                    
                    casino_result+=valid_result

    greybox_result:List[int]=[]  # [valid_patches...]
    if use_greybox:
        for project in D4J_1_2_0_LIST:
            for i in range(max_exp):
                result_path=f'{result_dir}/{project}-greybox-{i}/simapr-result.json'
                if os.path.exists(result_path):
                    hq_result,valid_result=get_result_time(result_path)
                    
                    greybox_result+=valid_result

    original_result:List[int]=[]  # [valid_patches...]
    if use_orig:
        for project in D4J_1_2_0_LIST:
            result_path=f'{result_dir}/{project}-orig/simapr-result.json'
            if os.path.exists(result_path):
                hq_result,valid_result=get_result_time(result_path)
                
                original_result+=valid_result

    seapr_result:List[int]=[]  # [valid_patches...]
    if use_seapr:
        for project in D4J_1_2_0_LIST:
            result_path=f'{result_dir}/{project}-seapr/simapr-result.json'
            if os.path.exists(result_path):
                hq_result,valid_result=get_result_time(result_path)
                
                seapr_result+=valid_result

    final_result:Dict[str,List[int]]=dict()  # {algorithm: [valid_patches...]}
    if use_casino:
        final_result['casino']=casino_result
    if use_greybox:
        final_result['greybox']=greybox_result
    if use_orig:
        final_result['orig']=original_result
    if use_seapr:
        final_result['seapr']=seapr_result
    
    return final_result