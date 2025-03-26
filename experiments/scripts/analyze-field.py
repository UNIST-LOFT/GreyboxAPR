import json
import os
import shutil
import sys
import subprocess
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
import d4j

tool=sys.argv[1]

if os.path.exists('scripts/critical-field'):
    shutil.rmtree('scripts/critical-field')
os.mkdir('scripts/critical-field')

freq_data:Dict[str,Dict[str,Dict[str,float]]]=dict()

for result in d4j.D4J_1_2_LIST:
    plau_freq_list:Dict[str,int]=dict()
    unplau_freq_list:Dict[str,int]=dict()
    plau_diffs:Dict[str,List[float]]=dict()
    unplau_diffs:Dict[str,List[float]]=dict()
    print(result)
    for i in range(10):
        field_path=f'{tool}/result/field/{result}'
        result_path=f'{tool}/result/{result}-greybox-fieldonly-{i}'
        if not os.path.exists(f'{result_path}/simapr-finished.txt'):
            continue
        res=subprocess.run(['python3','/root/project/GreyboxAPR/SimAPR/simulate-greybox.py',result_path,field_path],stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,text=True)
        
        if res.returncode!=0:
            print(f"Error in {result}-{i}")
            print(res.stdout)
            continue
        
        if not os.path.exists(f'{result_path}/critical-field.json'):
            continue
        with open(f'{result_path}/critical-field.json','r') as f:
            fields=json.load(f)

        if len(fields['interesting_freq'])==0:
            continue
        
        # Analyze field values
        plau_diff=fields['plausible_diff']
        unplau_diff=fields['unplausible_diff']
        
        for test in plau_diff:
            for field in plau_diff[test]:
                if f'{test}#{field}' not in plau_diffs:
                    plau_diffs[f'{test}#{field}']=[]
                plau_diffs[f'{test}#{field}']+=plau_diff[test][field]
        for test in unplau_diff:
            for field in unplau_diff[test]:
                if f'{test}#{field}' not in unplau_diffs:
                    unplau_diffs[f'{test}#{field}']=[]
                unplau_diffs[f'{test}#{field}']+=unplau_diff[test][field]

        # Analyze field frequency
        plau_freq=fields['plausible_freq']
        unplau_freq=fields['unplausible_freq']
        for test in plau_freq:
            for field in plau_freq[test]:
                if f'{test}#{field}' not in plau_freq_list:
                    plau_freq_list[f'{test}#{field}']=0
                plau_freq_list[f'{test}#{field}']+=plau_freq[test][field]
        for test in unplau_freq:
            for field in unplau_freq[test]:
                if f'{test}#{field}' not in unplau_freq_list:
                    unplau_freq_list[f'{test}#{field}']=0
                unplau_freq_list[f'{test}#{field}']+=unplau_freq[test][field]

    if len(plau_diffs)==0:
        continue
    _plau_diff_list=[]
    _unplau_diff_list=[]
    for key in plau_diffs:
        _plau_diff_list+=plau_diffs[key]
        if key in unplau_diffs:
            _unplau_diff_list+=unplau_diffs[key]
    for key in unplau_diffs:
        if key not in plau_diffs:
            _unplau_diff_list+=unplau_diffs[key]

    plau_diff_list=[]
    unplau_diff_list=[]
    for v in _plau_diff_list:
        if str(v)!='nan':
            plau_diff_list.append(v)
    for v in _unplau_diff_list:
        if str(v)!='nan':
            unplau_diff_list.append(v)
    if len(plau_diff_list)>0:
        print(f'Plausible patch: len: {len(plau_diff_list)} mean: {np.mean(plau_diff_list)}, median: {np.median(plau_diff_list)}, std: {np.std(plau_diff_list)}')
        freq_data[result]={'plausible':{
            'length':len(plau_diff_list),
            'mean': np.mean(plau_diff_list),
            'median': np.median(plau_diff_list),
            'std': np.std(plau_diff_list)
        }}
    if len(unplau_diff_list)>0:
        print(f'Unplausible patch: len: {len(unplau_diff_list)} mean: {np.mean(unplau_diff_list)}, median: {np.median(unplau_diff_list)}, std: {np.std(unplau_diff_list)}')
        freq_data[result]={'unplausible':{
            'length':len(unplau_diff_list),
            'mean': np.mean(unplau_diff_list),
            'median': np.median(unplau_diff_list),
            'std': np.std(unplau_diff_list)
        }}

    plau_list=[]
    unplau_list=[]
    for key in plau_freq_list:
        plau_list.append(plau_freq_list[key])
        if key not in unplau_freq_list:
            unplau_list.append(0)
        else:
            unplau_list.append(unplau_freq_list[key])
    for key in unplau_freq_list:
        if key not in plau_freq_list:
            plau_list.append(0)
            unplau_list.append(unplau_freq_list[key])
    
    x=list(range(len(plau_list)))
    plt.clf()
    plt.plot(x,plau_list,'r',label='Plausible')
    plt.plot(x,unplau_list,'-.b',label='Unplausible')
    plt.legend()
    plt.xlabel('Critical field')
    plt.ylabel('Frequency')
    plt.grid()
    plt.savefig(f'scripts/critical-field/{result}.pdf',bbox_inches='tight')
    plt.savefig(f'scripts/critical-field/{result}.jpg',bbox_inches='tight')

with open('experiments/scripts/critical-field/freq.json','w') as f:
    json.dump(freq_data,f)