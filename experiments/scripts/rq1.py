from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd

import d4j

def plot_patches_ci_java(mode='tbar'):
    orig_result:List[int]=[]
    seapr_result:List[int]=[]
    genprog_result:List[List[int]]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]
    dl = mode in {'recoder', 'alpharepair'}
    #d4j.D4J_1_2_LIST
    list1 = ['Chart_3', 'Chart_12', 'Chart_15', 'Chart_7', 'Closure_2', 'Closure_46', 'Closure_62', 'Closure_63', 'Closure_93', 'Closure_126', 'Closure_133', 'Closure_21', 'Closure_22', 'Lang_7', 'Lang_44', 'Lang_51', 'Lang_56', 'Lang_58', 'Lang_63', 'Math_2', 'Math_5', 'Math_7', 'Math_8', 'Math_15', 'Math_20', 'Math_24', 'Math_28', 'Math_40', 'Mockito_38' ]
    # Casino
    print('Casino')
    for i in range(10):
        casino_result.append([])
        for result in list1:
            if dl:
                result = result.replace('_', '-')
            try:
                result_file=open(f'{mode}/result/{result}-casino-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            has_plau=False
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    #time
                    #casino_result[-1].append(round((time)/60))
                    
                    #iteration
                    casino_result[-1].append(iteration)
                    has_plau=True

                # if time>3600:
                #     break
            if has_plau and i==0:
                print(result)

    # Greybox
    print('Greybox')
    for i in range(10):
        greybox_result.append([])
        for result in list1:
            if dl:
                result = result.replace('_', '-')
            try:
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            has_plau=False
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    #time
                    #greybox_result[-1].append(round((time)/60))
                    
                    #iteration
                    greybox_result[-1].append(iteration)
                    has_plau=True

                # if time>3600:
                #     break
            if has_plau and i==0:
                print(result)


    # # GenProg
    # for i in range(50):
    #     genprog_result.append([])
    #     for result in d4j.D4J_1_2_LIST:
    #         if dl:
    #             result = result.replace('_', '-')
    #         try:
    #             result_file=open(f'{mode}/result/{result}-genprog-{i}/simapr-result.json','r')
    #         except:
    #             continue
    #         root=json.load(result_file)
    #         result_file.close()

    #         prev_time=0.
    #         for res in root:
    #             is_hq=res['result']
    #             is_plausible=res['pass_result']
    #             iteration=res['iteration']
    #             time=res['time']
    #             loc=res['config'][0]['location']

    #             if is_plausible:
    #                 genprog_result[-1].append(round((time)/60))

    #             if time>3600:
    #                 break

    # # SeAPR
    # for result in d4j.D4J_1_2_LIST:
    #     if dl:
    #         result = result.replace('_', '-')
    #     try:
    #         result_file=open(f'{mode}/result/{result}-seapr/simapr-result.json','r')
    #     except:
    #         continue
    #     root=json.load(result_file)
    #     result_file.close()

    #     prev_time=0.
    #     for res in root:
    #         is_hq=res['result']
    #         is_plausible=res['pass_result']
    #         iteration=res['iteration']
    #         time=res['time']
    #         loc=res['config'][0]['location']

    #         if is_plausible:
    #             seapr_result.append(round((time)/60))

    #         if time>3600:
    #             break

    # Original
    print('Original')
    for result in list1:
        if dl:
            result = result.replace('_', '-')
        try:
            result_file=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
        except:
            continue
        root=json.load(result_file)
        result_file.close()

        prev_time=0.
        has_plau=False
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                #time
                #orig_result.append(round((time)/60))
                
                #iteration
                orig_result.append(iteration)
                has_plau=True

            # if time>3600:
            #     break
        if has_plau:
            print(result)

    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(4,3))
    print(mode)

    # Original tool
    if mode=='tbar': name='TBar'
    elif mode=='fixminer': name='Fixminer'
    elif mode=='kpar': name='kPar'
    elif mode=='avatar': name='Avatar'
    elif mode=='recoder': name='Recoder'
    elif mode=='alpharepair': name='AlphaRepair'

    # Original
    results=sorted(orig_result)
    other_list=[0]
    
        #time 
    # for i in range(0,300):
    #     if i in results:
    #         other_list.append(other_list[-1]+results.count(i))
    #     else:
    #         other_list.append(other_list[-1])
    # plt.plot(list(range(0,301)),other_list,'-.b',label=name)
    
        #iteration
    # for i in range(0,500):
    #     if i in results:
    #         other_list.append(other_list[-1]+results.count(i))
    #     else:
    #         other_list.append(other_list[-1])
    # plt.plot(list(range(0,501)),other_list,'-.b',label=name)

    # Casino
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    
        #time
    # for j in range(10):
    #     cur_result=sorted(casino_result[j])
    #     guided_list.append([0])
    #     for i in range(0,300):
    #         if i in cur_result:
    #             guided_list[-1].append((10*guided_list[-1][-1]+cur_result.count(i))/10)
    #             guided_x.append(i)
    #             guided_y.append((10*guided_list[-1][-1]+cur_result.count(i))/10)
    #         else:
    #             guided_list[-1].append(guided_list[-1][-1])
    #             guided_x.append(i)
    #             guided_y.append(guided_list[-1][-1])
    #         if i%60==0:
    #             temp_[i//60].append(guided_list[-1][-1])
    # guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    # seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='r',label='Casino')
    
        #iteration
    for j in range(10):
        cur_result=sorted(casino_result[j])
        guided_list.append([0])
        for i in range(0,500):
            if i in cur_result:
                guided_list[-1].append((10*guided_list[-1][-1]+cur_result.count(i))/10)
                guided_x.append(i)
                guided_y.append((10*guided_list[-1][-1]+cur_result.count(i))/10)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])

    guided_y_temp=[]
    guided_y=[0]
    for i in range(10):
        guided_y_temp+=casino_result[i]
    for i in range(0,500):
        if i in guided_y_temp:
            guided_y.append((10*guided_y[-1]+guided_y_temp.count(i))/10)
        else:
            guided_y.append(guided_y[-1])
    plt.plot(list(range(0,501)),guided_y,'r',label='Casino')

    # for i in range(5):
    #     print(f'{i*60}: {np.std(temp_[i])}')

    # Greybox
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    
        #time
    # for j in range(10):
    #     cur_result=sorted(greybox_result[j])
    #     guided_list.append([0])
    #     for i in range(0,300):
    #         if i in cur_result:
    #             guided_list[-1].append((10*guided_list[-1][-1]+cur_result.count(i))/10)
    #             guided_x.append(i)
    #             guided_y.append((10*guided_list[-1][-1]+cur_result.count(i))/10)
    #         else:
    #             guided_list[-1].append(guided_list[-1][-1])
    #             guided_x.append(i)
    #             guided_y.append(guided_list[-1][-1])
    # guided_df=pd.DataFrame({'Time':guided_x,'Number of valid patches':guided_y})
    # seaborn.lineplot(data=guided_df,x='Time',y='Number of valid patches',color='g',label='Greybox')
    
        #iteration
    for j in range(10):
        cur_result=sorted(greybox_result[j])
        guided_list.append([0])
        for i in range(0,500):
            if i in cur_result:
                guided_list[-1].append((10*guided_list[-1][-1]+cur_result.count(i))/10)
                guided_x.append(i)
                guided_y.append((10*guided_list[-1][-1]+cur_result.count(i))/10)
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])

    guided_y_temp=[]
    guided_y=[0]
    for i in range(10):
        guided_y_temp+=greybox_result[i]
    for i in range(0,500):
        if i in guided_y_temp:
            guided_y.append((10*guided_y[-1]+guided_y_temp.count(i))/10)
        else:
            guided_y.append(guided_y[-1])
    plt.plot(list(range(0,501)),guided_y,'g',label='Greybox', alpha=0.5)

    # # SeAPR
    # results=sorted(seapr_result)
    # other_list=[0]
    # for i in range(0,300):
    #     if i in results:
    #         other_list.append(other_list[-1]+results.count(i))
    #     else:
    #         other_list.append(other_list[-1])
    # plt.plot(list(range(0,301)),other_list,':g',label='SeAPR')

    # # GenProg
    # other_list:List[List[int]]=[]
    # other_x=[]
    # other_y=[]
    # for j in range(50):
    #     cur_result=sorted(genprog_result[j])
    #     other_list.append([0])
    #     for i in range(0,300):
    #         if i in cur_result:
    #             other_list[-1].append((50*other_list[-1][-1]+cur_result.count(i))/50)
    #             other_x.append(i)
    #             other_y.append((50*other_list[-1][-1]+cur_result.count(i))/50)
    #         else:
    #             other_list[-1].append(other_list[-1][-1])
    #             other_x.append(i)
    #             other_y.append(other_list[-1][-1])
    # other_df=pd.DataFrame({'Time':other_x,'Number of valid patches':other_y})
    # seaborn.lineplot(data=other_df,x='Time',y='Number of valid patches',color='y',label='GenProg',linestyle='dashed')
    plt.legend(fontsize=12)
    
    #time
    # plt.xlabel('Time (min)',fontsize=15)
    
    #iteration
    plt.xlabel('Iteration',fontsize=15)
    
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f'rq1-{mode}.pdf',bbox_inches='tight')

from sys import argv

plot_patches_ci_java(argv[1])