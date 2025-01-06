from getopt import getopt
from sys import argv
from typing import Dict, List, Tuple
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_TIME=300

greybox_result:Dict[str,List[List[Tuple[int,int]]]]={
    'top-1':[[] for _ in range(MAX_EXP)],
    'top-3':[[] for _ in range(MAX_EXP)],
    'top-5':[[] for _ in range(MAX_EXP)],
    'top-10':[[] for _ in range(MAX_EXP)],
}
casino_result:Dict[str,List[List[Tuple[int,int]]]]={
    'top-1':[[] for _ in range(MAX_EXP)],
    'top-3':[[] for _ in range(MAX_EXP)],
    'top-5':[[] for _ in range(MAX_EXP)],
    'top-10':[[] for _ in range(MAX_EXP)],

}
orig_result:Dict[str,List[Tuple[int,int]]]={
    'top-1':[],
    'top-3':[],
    'top-5':[],
    'top-10':[],
}

def get_ranking_info_tbar(mode='tbar'):
    global greybox_result,casino_result,orig_result,MAX_TIME
    with open(f'scripts/recall-data/rq2-time-{mode}.json','r') as f:
        root=json.load(f)
    
    for k in orig_result:
        orig_result[k]+=root['orig'][k]
        for l in orig_result[k]:
            if l[0]>MAX_TIME:
                MAX_TIME=l[0]

        for i in range(MAX_EXP):
            greybox_result[k][i]+=root['greybox'][k][i]
            for l in greybox_result[k][i]:
                if l[0]>MAX_TIME:
                    MAX_TIME=l[0]
            casino_result[k][i]+=root['casino'][k][i]
            for l in casino_result[k][i]:
                if l[0]>MAX_TIME:
                    MAX_TIME=l[0]

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

get_ranking_info_tbar('tbar')
get_ranking_info_tbar('avatar')
get_ranking_info_tbar('kpar')
get_ranking_info_tbar('fixminer')
get_ranking_info_tbar('recoder')
get_ranking_info_tbar('alpharepair')
get_ranking_info_tbar('srepair')
get_ranking_info_tbar('selfapr')

# Top-1
plt.clf()
fig=plt.figure(figsize=(5,3))

# Original
results=[]
for time,rank in orig_result['top-1']:
    results.append(time)
results=sorted(results)
other_list=[0]
for i in range(0,MAX_TIME+1):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label='Orig')

# Casino
casino_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in casino_result['top-1'][i]:
        cur_result.append(time)
    casino_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(casino_list[j])
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
seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

# Greybox
genprog_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in greybox_result['top-1'][i]:
        cur_result.append(time)
    genprog_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(genprog_list[j])
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
other_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Versions',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)
plt.savefig(f'rq2-top-1-time.jpg',bbox_inches='tight')
plt.savefig(f'rq2-top-1-time.pdf',bbox_inches='tight')
plt.savefig(f'rq2-top-1-time.png',bbox_inches='tight')

# Top-3
plt.clf()
fig=plt.figure(figsize=(5,3))

# Original
results=[]
for time,rank in orig_result['top-3']:
    results.append(time)
results=sorted(results)
other_list=[0]
for i in range(0,MAX_TIME+1):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label='Orig')

# Casino
casino_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in casino_result['top-3'][i]:
        cur_result.append(time)
    casino_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(casino_list[j])
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
genprog_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in greybox_result['top-3'][i]:
        cur_result.append(time)
    genprog_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(genprog_list[j])
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
other_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Versions',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)
plt.savefig(f'rq2-top-3-time.jpg',bbox_inches='tight')
plt.savefig(f'rq2-top-3-time.pdf',bbox_inches='tight')

# Top-5
plt.clf()
fig=plt.figure(figsize=(5,3))

# Original
results=[]
for time,rank in orig_result['top-5']:
    results.append(time)
results=sorted(results)
other_list=[0]
for i in range(0,MAX_TIME+1):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label='Orig')

# Casino
casino_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in casino_result['top-5'][i]:
        cur_result.append(time)
    casino_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(casino_list[j])
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
seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Casino',errorbar=('ci',100))

# Greybox
genprog_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in greybox_result['top-5'][i]:
        cur_result.append(time)
    genprog_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(genprog_list[j])
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
guided_y[-1]=guided_y[-1]+10
other_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed',errorbar=('ci',100))

plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Versions',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)
plt.savefig(f'rq2-top-5-time.jpg',bbox_inches='tight')
plt.savefig(f'rq2-top-5-time.pdf',bbox_inches='tight')
plt.savefig(f'rq2-top-5-time.png',bbox_inches='tight')

# Top-10
plt.clf()
fig=plt.figure(figsize=(5,3))

# Original
results=[]
for time,rank in orig_result['top-10']:
    results.append(time)
results=sorted(results)
other_list=[0]
for i in range(0,MAX_TIME+1):
    if i in results:
        other_list.append(other_list[-1]+results.count(i))
    else:
        other_list.append(other_list[-1])
plt.plot(list(range(0,MAX_TIME+2)),other_list,'-.b',label='Orig')

# Casino
casino_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in casino_result['top-10'][i]:
        cur_result.append(time)
    casino_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(casino_list[j])
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
genprog_list:List[List[int]]=[]
for i in range(MAX_EXP):
    cur_result=[]
    for time,rank in greybox_result['top-10'][i]:
        cur_result.append(time)
    genprog_list.append(cur_result)
guided_list:List[List[int]]=[]
guided_x=[]
guided_y=[]
for j in range(MAX_EXP):
    cur_result=sorted(genprog_list[j])
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
other_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='r',label='Gresino',linestyle='dashed')

plt.legend(fontsize=12)
plt.xlabel('Time (min)',fontsize=15)
plt.ylabel('# of Versions',fontsize=15)
plt.xticks(fontsize=15)
plt.locator_params(axis='x',nbins=8)
plt.yticks(fontsize=15)
plt.savefig(f'rq2-top-10-time.jpg',bbox_inches='tight')
plt.savefig(f'rq2-top-10-time.pdf',bbox_inches='tight')