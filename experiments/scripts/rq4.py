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
MAX_ITERATION=3000

orig_result:List[int]=[]
casino_result:List[List[int]]=[[] for _ in range(MAX_EXP)]
greybox_result:List[List[int]]=[[] for _ in range(MAX_EXP)]

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

def get_tool_data(tool:str):
    global orig_result,greybox_result,casino_result
    with open(f'rq4-{tool}.json','r') as f:
        root=json.load(f)
    
    orig_result+=root['orig']

    for i in range(MAX_EXP):
        greybox_result[i]+=root['greybox'][i]
        casino_result[i]+=root['casino'][i]

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
for i in range(0,MAX_ITERATION):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_ITERATION+1)),other_list,'-.b',label='Orig')

# Casino
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(casino_result[j])
    guided_list.append([0])
    for i in range(0,MAX_ITERATION):
        if i in cur_result:
            guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            guided_x.append(i)
            guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
        else:
            guided_list[-1].append(guided_list[-1][-1])
            guided_x.append(i)
            guided_y.append(guided_list[-1][-1])
guided_df=pd.DataFrame({'Iteration':guided_x,'# of valid patches':guided_y})
seaborn.lineplot(data=guided_df,x='Iteration',y='# of valid patches',color='g',label='Casino')

# Greybox
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(greybox_result[j])
    guided_list.append([0])
    for i in range(0,MAX_ITERATION):
        if i in cur_result:
            guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            guided_x.append(i)
            guided_y.append(guided_list[-1][-1]+cur_result.count(i)/MAX_EXP)
        else:
            guided_list[-1].append(guided_list[-1][-1])
            guided_x.append(i)
            guided_y.append(guided_list[-1][-1])
guided_df=pd.DataFrame({'Iteration':guided_x,'# of valid patches':guided_y})
seaborn.lineplot(data=guided_df,x='Iteration',y='# of valid patches',color='r',label='Gresino',linestyle='dashed')

plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Valid Patches',fontsize=15)
plt.xticks(fontsize=15)
# plt.locator_params(axis='x',nbins=6)
plt.yticks(fontsize=15)
plt.savefig(f'rq4.pdf',bbox_inches='tight')