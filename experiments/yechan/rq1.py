from typing import Dict, List
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd

import os

def get_fl_folders():
    directory_path = 'experiments/yechan/alphaRepair/result'

    # 디렉토리 내의 폴더 목록 가져오기
    folder_list = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

    # 특정 패턴으로 끝나는 폴더들만 선택 = result_with_weight에서 greybox-10 이 끝나있고, result에서 orig가 끝나있어야 함.
    pattern = '-greybox-10-out'
    filtered_folders = [folder[:-len(pattern)] for folder in folder_list if folder.endswith(pattern) and os.path.exists(os.path.join(directory_path, folder,"simapr-finished.txt")) and os.path.exists(os.path.join(directory_path, folder[:-len(pattern)]+'-orig-out',"simapr-finished.txt"))]
    
    print("modes: ", filtered_folders)
    
    return filtered_folders


D4J_1_2_LIST = get_fl_folders() #filtered_folders

def plot_patches_ci_java(mode='alphaRepair'):
    global D4J_1_2_LIST
    orig_result:List[int]=[]
    casino_result:List[List[int]]=[]
    greybox_result:List[List[int]]=[]
    greybox_with_weight_result:List[List[int]]=[]
    
    x_len = 3000
    file_number_per_mode = 10
    
    dl = mode in {'recoder', 'alpharepair'}

    # Greybox
    for i in range(1, file_number_per_mode+1):
        greybox_result.append([])
        for result in D4J_1_2_LIST:
            if dl:
                result = result.replace('_', '-')
            try:
                result_file=open(f'experiments/yechan/{mode}/result/{result}-greybox-{i}-out/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    greybox_result[-1].append(iteration)

                # if time>3600:
                #     break
    """    
    # Greybox with fl
    for i in range(1, file_number_per_mode+1):
        greybox_with_weight_result.append([])
        for result in D4J_1_2_LIST:
            if dl:
                result = result.replace('_', '-')
            try:
                result_file=open(f'experiments/yechan/{mode}/result_with_weight/{result}-greybox-{i}-out/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    greybox_with_weight_result[-1].append(iteration)

                # if time>3600:
                #     break
    """
    # Casino
    for i in range(1, file_number_per_mode+1):
        casino_result.append([])
        for result in D4J_1_2_LIST:
            if dl:
                result = result.replace('_', '-')
            try:
                result_file=open(f'experiments/yechan/{mode}/result/{result}-casino-{i}-out/simapr-result.json','r')
            except:
                continue
            root=json.load(result_file)
            result_file.close()

            prev_time=0.
            for res in root:
                is_hq=res['result']
                is_plausible=res['pass_result']
                iteration=res['iteration']
                time=res['time']
                loc=res['config'][0]['location']

                if is_plausible:
                    casino_result[-1].append(iteration)

                # if time>3600:
                #     break

    
    # Original
    for result in D4J_1_2_LIST:
        if dl:
            result = result.replace('_', '-')
        try:
            result_file=open(f'experiments/yechan/{mode}/result/{result}-orig-out/simapr-result.json','r')
        except:
            continue
        root=json.load(result_file)
        result_file.close()

        prev_time=0.
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                orig_result.append(iteration)

            # if time>3600:
            #     break

    # Plausible patch plot
    plt.clf()
    fig=plt.figure(figsize=(4,3))
    print(mode)

    # Original tool
    if mode=='alphaRepair': name='alphaRepair'
    elif mode=='fixminer': name='Fixminer'
    elif mode=='kpar': name='kPar'
    elif mode=='avatar': name='Avatar'
    elif mode=='recoder': name='Recoder'
    elif mode=='alpharepair': name='alphaRepair'

    # Original
    results=sorted(orig_result)
    other_list=[0]
    for i in range(0,x_len):
        if i in results:
            other_list.append(other_list[-1]+1)
        else:
            other_list.append(other_list[-1])
    plt.plot(list(range(0,x_len+1)),other_list,'-.b',label=name)

    # Greybox
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    for j in range(file_number_per_mode):
        print(f"print by Greybox {j}")
        cur_result=sorted(greybox_result[j])
        guided_list.append([0])
        for i in range(0,x_len):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)) #cumulative
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            
            
            if i%1000==1:
                print(i,":",guided_y[-1])
            
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='g',label='Greybox')
    #for i in range(5):
        #print(f'{i*60}: {np.std(temp_[i])}')
    """
    # Greybox with fl
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    for j in range(file_number_per_mode):
        print(f"print by Greybox fl {j}")
        cur_result=sorted(greybox_with_weight_result[j])
        guided_list.append([0])
        for i in range(0,x_len):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)) #cumulative
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            
            
            if i%1000==1:
                print(i,":",guided_y[-1])
            
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='#CC00CC',label='Greybox_wt')
    #for i in range(5):
        #print(f'{i*60}: {np.std(temp_[i])}')
    """
    # Casino
    guided_list:List[List[int]]=[]
    guided_x=[]
    guided_y=[]
    temp_=[[],[],[],[],[]]
    for j in range(file_number_per_mode):
        print(f"print by Casino {j}")
        cur_result=sorted(casino_result[j])
        guided_list.append([0])
        for i in range(0,x_len):
            if i in cur_result:
                guided_list[-1].append(guided_list[-1][-1]+cur_result.count(i)) #cumulative
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            else:
                guided_list[-1].append(guided_list[-1][-1])
                guided_x.append(i)
                guided_y.append(guided_list[-1][-1])
            
            if i%1000==1:
                print(i,":",guided_y[-1])
                
    guided_df=pd.DataFrame({'Iteration':guided_x,'Number of valid patches':guided_y})
    seaborn.lineplot(data=guided_df,x='Iteration',y='Number of valid patches',color='r',label='Casino')
    #for i in range(5):
        #print(f'{i*60}: {np.std(temp_[i])}')

    

    
    plt.legend(fontsize=12)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=15)
    plt.savefig(f'experiments/yechan/rq1-{mode}.pdf',bbox_inches='tight')



plot_patches_ci_java('alphaRepair')