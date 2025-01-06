from getopt import getopt
from os import path
from sys import argv
from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_TIME=300

casino_result:Dict[str,List[List[int]]]={
    'srepair': [[] for _ in range(MAX_EXP)],
    'tbar': [[] for _ in range(MAX_EXP)],
    'avatar': [[] for _ in range(MAX_EXP)],
    'kpar': [[] for _ in range(MAX_EXP)],
    'fixminer': [[] for _ in range(MAX_EXP)],
    'alpharepair': [[] for _ in range(MAX_EXP)],
    'recoder': [[] for _ in range(MAX_EXP)],
    'selfapr': [[] for _ in range(MAX_EXP)]
}

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

def get_tool_data(tool:str):
    global casino_result,MAX_TIME
    with open(f'scripts/d4j-data/rq1-{tool}-time.json','r') as f:
        root=json.load(f)
    
    for i in range(MAX_EXP):
        casino_result[tool][i]+=root['casino'][i]
        for l in casino_result[tool][i]:
            if l>MAX_TIME:
                MAX_TIME=l

get_tool_data('srepair')
get_tool_data('tbar')
get_tool_data('alpharepair')
get_tool_data('avatar')
get_tool_data('kpar')
get_tool_data('fixminer')
get_tool_data('recoder')
get_tool_data('selfapr')

TOOL_FORMATED_NAME={
    'tbar': 'TBar',
    'avatar': 'Avatar',
    'kpar': 'kPar',
    'fixminer': 'Fixminer',
    'alpharepair': 'AlphaRepair',
    'recoder': 'Recoder',
    'srepair': 'SRepair',
    'selfapr': 'SelfAPR',
}

# Plausible patch plot
plt.clf()
fig=plt.figure(figsize=(7,5))

# Casino
linestyle=['-','--','-.',':']
_index=0
for tool in casino_result:
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    for j in range(MAX_EXP):
        cur_result=sorted(casino_result[tool][j])
        guided_list.append([0])
        for i in range(0,MAX_TIME+1):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1]+cur_result.count(i))
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                if i==0:
                    guided_y.append(0)
                else:
                    guided_y.append(guided_y[-1])
    guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',label=TOOL_FORMATED_NAME[tool],linestyle=linestyle[_index%4])
    _index+=1


plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Valid Patches',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)

if WITH_MOCKITO:
    plt.savefig(f'rq1-casino-time-w-mockito.pdf',bbox_inches='tight')
    plt.savefig(f'rq1-casino-time-w-mockito.png',bbox_inches='tight')
else:
    plt.savefig(f'rq1-casino-time.pdf',bbox_inches='tight')
    plt.savefig(f'rq1-casino-time.png',bbox_inches='tight')