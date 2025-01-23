from getopt import getopt
from sys import argv
from typing import List
import json
import os

from matplotlib import pyplot as plt

import d4j

from ablation import AblationResult

MAX_EXP=10
WITH_MOCKITO=False
MAX_TIME=300

def plot_patches_ci_java(mode='tbar'):
    global MAX_TIME,MAX_EXP,WITH_MOCKITO
    AblationResult.setGlobalState(mode, MAX_EXP, WITH_MOCKITO, MAX_TIME = MAX_TIME)
    
    orig_result:List[int]=[]
    ablation_results = [
        # name, dirname, color, max_exp
        AblationResult('wo_vertical_field', 'wo-vertical-field', 'r'), # blackbox x / branch x / field o
        AblationResult('wo_vertical_branch', 'wo-vertical-branch', 'g'), # blackbox x / branch o / field x
        AblationResult('wo_vertical_both', 'wo-vertical-both', 'b'), # blackbox x / branch o / field o
        AblationResult('casino', 'casino', 'c'), # blackbox o / branch x / field x
        AblationResult('greybox_field', 'greybox-fieldonly', 'm'), # blackbox o / branch x / field o
        AblationResult('greybox_branch', 'greybox', 'y'), # blackbox o / branch o / field x
        AblationResult('greybox_both', 'greyboxfd', 'k') # blackbox o / branch o / field o
    ]
    
    print('Saving results as json\n')
    
    # Save Results
    for result in ablation_results:
        result.save_result('time')

    # Original
    for result in d4j.D4J_1_2_LIST:
        if not AblationResult.check_deps(result):
            # Skip if experiment not end
            continue
        if not WITH_MOCKITO and 'Mockito' in result:
            continue
        try:
            result_file=open(f'{mode}/result/{result}-orig/simapr-result.json','r')
        except:
            continue
        root=json.load(result_file)
        result_file.close()

        # Read cache to get baseline time
        try:
            cache_file=open(f'{mode}/result/cache/{result}-cache.json','r')
        except:
            continue
        cache=json.load(cache_file)
        cache_file.close()

        total_time=0.
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']
            if loc in cache:
                total_time+=cache[loc]['fail_time']+cache[loc]['pass_time']
            else:
                if res['time']-total_time>0:
                    total_time+=(res['time']-total_time)


            if is_plausible:
                if MAX_TIME<round((total_time)/60):
                    MAX_TIME=round((total_time)/60)
                orig_result.append(round((total_time)/60))
                # orig_result.append(iteration)

            # if time>3600:
            #     break

    print(f'original: {len(orig_result)}')
    
    dump_data = { 'orig': orig_result }
    for result in ablation_results:
        dump_data[result.name] = result.result_list
    
    with open(f'rq3-{mode}-time.json','w') as f:
        json.dump(dump_data,f,indent=4)

    print('\nDrawing plots\n')

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

    print('original Done')

    # Draw plots
    for result in ablation_results:
        result.draw_plot('time')

    plt.legend(fontsize='small', framealpha=0.5)
    plt.xlabel('Time (min)',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.locator_params(axis='x',nbins=8)
    plt.yticks(fontsize=15)
    if WITH_MOCKITO:
        plt.savefig(f'rq3-time-{mode}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-time-{mode}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'rq3-time-{mode}.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-time-{mode}.jpg',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])