import os
import time
from typing import Any, Dict, List, Set, Tuple
import d4j
import subprocess
import json

each_time:Dict[str,List[Tuple[float,float]]]=[]

def run_test(project:str,tool:str,patch:str,buggy_file:str,buggy_class_name:str=None,test:str='ALL',greybox:bool=False):
    new_env=os.environ.copy()
    new_env["SIMAPR_TEST"] = test
    new_env["SIMAPR_LOCATION"] = str(patch)
    new_env["SIMAPR_WORKDIR"] = f'/root/project/GreyboxAPR/{tool}/d4j/{project}'
    new_env["SIMAPR_BUGGY_LOCATION"] = buggy_file
    new_env["SIMAPR_BUGGY_PROJECT"] = project
    new_env["SIMAPR_TIMEOUT"] = '180000'
    if buggy_class_name is not None:
        new_env["SIMAPR_CLASS_NAME"] = buggy_class_name

    if greybox:
        new_env['GREYBOX_BRANCH']='1'
        new_env['GREYBOX_RESULT']=f'/tmp/{project}-{test.replace("::","#")}.txt'
        new_env['GREYBOX_INSTR_ROOT']='/root/project/JPatchInst'
        new_env['CLASSPATH']='/root/project/JPatchInst'
    else:
        new_env['GREYBOX_BRANCH']='0'
        new_env['CLASSPATH']='/root/project/JPatchInst'

    start_time=time.time()
    res=subprocess.run(['python3','d4j_run_test.py',f'/root/project/GreyboxAPR/{tool}/buggy'],env=new_env,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    total_time=time.time()-start_time
    return total_time  # We already know this patch passes all failing tests or not

def run_original(project:str,tool:str,test:str='ALL',greybox:bool=False):
    return run_test(project,tool,'original','original',test=test,greybox=greybox)

def parse_info(project:str,tool:str):
    failing_tests:List[str]=dict()
    patch_infos:Dict[str,Dict[str,Any]]=dict()

    with open(f'/root/project/GreyboxAPR/{tool}/d4j/{project}/switch-info.json') as f:
        info=json.load(f)
    
    failing_tests[project]=info['failing_test_cases']
    patch_infos[project]=dict()
    for file in info['rules']:
        file_name=file['file_name']
        class_name=file['class_name']
        for func in file['functions']:
            for line in func['lines']:
                for patch in line['cases']:
                    patch_infos[project][patch['location']]={
                        'file_name':file_name,
                        'class_name':class_name,
                    }

    return failing_tests, patch_infos

def parse_result(project:str,tool:str):
    casino_patches:Set[str]=set()
    gresino_patches:Set[str]=set()

    for res_file in os.listdir(f'/root/project/GreyboxAPR/experiments/{tool.lower()}/result'):
        if res_file.startswith(project) and ('casino' in res_file or 'greybox' in res_file):
            with open(f'/root/project/GreyboxAPR/experiments/{tool.lower()}/result/{res_file}/simapr-result.json') as f:
                res=json.load(f)
            
            for patch in res:
                if patch['compilable']:
                    if 'casino' in res_file:
                        casino_patches.add(patch['config'][0]['location'])
                    elif 'greybox' in res_file:
                        gresino_patches.add(patch['config'][0]['location'])

    return casino_patches.intersection(gresino_patches)

def run(project:str,tool:str):
    global each_time
    failing_tests,patch_infos=parse_info(project,tool)
    patches=parse_result(project,tool)

    # without greybox
    wo_greybox_times=[]
    run_original(project,tool,greybox=False)
    for patch in patches:
        file_name=patch_infos[project][patch]['file_name']
        class_name=patch_infos[project][patch]['class_name']
        for test in failing_tests[project]:
            wo_greybox_times.append(run_test(project,tool,patch,file_name,class_name,test,greybox=False))

    # with greybox
    w_greybox_times=[]
    run_original(project,tool,greybox=True)
    for patch in patches:
        file_name=patch_infos[project][patch]['file_name']
        class_name=patch_infos[project][patch]['class_name']
        for test in failing_tests[project]:
            w_greybox_times.append(run_test(project,tool,patch,file_name,class_name,test,greybox=True))

    for wo,w in zip(wo_greybox_times,w_greybox_times):
        each_time[project].append((wo,w,))

import multiprocessing as mp
from sys import argv

if len(argv)!=3:
    print(f'Usage: {argv[0]} <tool> <num of processes>')
    exit(1)

_tool=argv[1].lower()
if _tool=='tbar':
    tool='TBar'
elif _tool=='avatar':
    tool='Avatar'
elif _tool=='fixminer':
    tool='Fixminer'
elif _tool=='kpar':
    tool='kPar'
elif _tool=='alpharepair':
    tool='AlphaRepair'
elif _tool=='recoder':
    tool='Recoder'
elif _tool=='srepair':
    tool='SRepair'
elif _tool=='selfapr':
    tool='SelfAPR'
    
pool=mp.Pool(int(argv[1]))

for proj in d4j.D4J_1_2_LIST:
    each_time[proj]=[]

for proj in d4j.D4J_1_2_LIST:
    pool.apply_async(run,args=(proj,argv[2],))

pool.close()
pool.join()

final_result:List[List[float]]=[]
for proj in each_time:
    for wo,w in each_time[proj]:
        final_result.append([wo,w,])

with open(f'/root/project/GreyboxAPR/experiments/{argv[1].lower()}/overhead.json','w') as f:
    json.dump(final_result,f)