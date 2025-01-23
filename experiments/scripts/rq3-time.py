from getopt import getopt
import os
from sys import argv
from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn

import d4j

from ablation import *

MAX_EXP=10
WITH_MOCKITO=False
MAX_TIME=300

orig_result:List[int]=[]
ablation_results = get_ablation_result_variables(MAX_EXP)

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

def get_tool_data(tool:str):
    global MAX_TIME,MAX_EXP,ablation_results
    with open(f'scripts/ablation-data/rq3-{tool}.json','r') as f:
        root=json.load(f)
    
    orig_result+=root['orig']
    for l in orig_result:
        if l>MAX_TIME:
            MAX_TIME=l
            
    for i in range(MAX_EXP):
        for k, v in root.items():
            try:
                result = next(filter(lambda x: x.name == k))
                result.result_list[i] += v[i]
                for l in v[i]:
                    if l>MAX_TIME:
                        MAX_TIME=l
            except:
                pass

get_tool_data('tbar')
get_tool_data('alpharepair')
get_tool_data('avatar')
get_tool_data('kpar')
get_tool_data('fixminer')
get_tool_data('recoder')
get_tool_data('srepair')
get_tool_data('selfapr')

# Plausible patch plot
plt.clf()
fig=plt.figure(figsize=(5,3))

# Original
results=sorted(orig_result)
other_list=[0]
for i in range(0,MAX_TIME+1):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label='Orig')

# Draw plots
for result in ablation_results:
    draw_plot(result, MAX_TIME, 'Time (min)')

plt.legend(fontsize='small', framealpha=0.5)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Valid Patches',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)
if WITH_MOCKITO:
    plt.savefig(f'rq3-time-w-mockito.pdf',bbox_inches='tight')
    plt.savefig(f'rq3-time-w-mockito.jpg',bbox_inches='tight')
else:
    plt.savefig(f'rq3-time.pdf',bbox_inches='tight')
    plt.savefig(f'rq3-time.jpg',bbox_inches='tight')
