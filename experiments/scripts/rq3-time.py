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

MAX_EXP=10
WITH_MOCKITO=False
MAX_TIME=300

orig_result:List[int]=[]
casino_result:List[List[int]]=[]
greybox_result:List[List[int]]=[]
greybox_field_only_result:List[List[int]]=[]
greyboxfd_result:List[List[int]]=[]

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

def get_tool_data(tool:str):
    global MAX_EXP
    with open(f'scripts/rq3-time/{tool}.json','r') as f:
        root=json.load(f)
    
    orig_result+=root['orig']
    for i in range(MAX_EXP):
        casino_result[i]+=root['casino'][i]
        greybox_result[i]+=root['greybox'][i]
        greybox_field_only_result[i]+=root['greybox_field_only'][i]
        greyboxfd_result[i]+=root['greyboxfd'][i]

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

# Casino
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
temp_=[[],[],[],[],[]]
for j in range(MAX_EXP):
    cur_result=sorted(casino_result[j])
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
seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Casino')

# Greybox
other_list:List[List[int]]=[]
other_x=[]
other_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(greybox_result[j])
    other_list.append([0])
    for i in range(0,MAX_TIME+1):
        if i in cur_result:
            other_list[-1].append(other_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1]+cur_result.count(i))
        else:
            other_list[-1].append(other_list[-1][-1])
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1])
other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino_B',linestyle=':')

# Greybox with only critical field
other_list:List[List[int]]=[]
other_x=[]
other_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(greybox_field_only_result[j])
    other_list.append([0])
    for i in range(0,MAX_TIME+1):
        if i in cur_result:
            other_list[-1].append(other_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1]+cur_result.count(i))
        else:
            other_list[-1].append(other_list[-1][-1])
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1])
other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='y',label='Gresino_F',linestyle='-.')

# Greybox with critical field
other_list:List[List[int]]=[]
other_x=[]
other_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(greyboxfd_result[j])
    other_list.append([0])
    for i in range(0,MAX_TIME+1):
        if i in cur_result:
            other_list[-1].append(other_list[-1][-1]+cur_result.count(i)/MAX_EXP)
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1]+cur_result.count(i))
        else:
            other_list[-1].append(other_list[-1][-1])
            other_x.append(i)
            if i==0:
                other_y.append(0)
            else:
                other_y.append(other_y[-1])
other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='k',label='Gresino_BF',linestyle='--')

plt.legend(fontsize=11)
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
