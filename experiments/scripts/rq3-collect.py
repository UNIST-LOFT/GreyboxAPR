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
MAX_ITERATION=3000

def plot_patches_ci_java(mode='tbar'):
    global MAX_EXP,MAX_ITERATION,WITH_MOCKITO
    AblationResult.setGlobalState(mode, MAX_EXP, WITH_MOCKITO, MAX_ITERATION = MAX_ITERATION)
    
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
        result.save_result('iteration')

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

        prev_time=0.
        for res in root:
            is_hq=res['result']
            is_plausible=res['pass_result']
            iteration=res['iteration']
            time=res['time']
            loc=res['config'][0]['location']

            if is_plausible:
                # orig_result.append(round((time)/60))
                orig_result.append(iteration)

            # if time>3600:
            #     break

    print(f'original: {len(orig_result)}')

    dump_data = { 'orig': orig_result }
    for result in ablation_results:
        dump_data[result.name] = result.result_list
    
    with open(f'rq3-{mode}.json','w') as f:
        json.dump(dump_data,f,indent=4)

    print('\nDrawing plots\n')

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
    
    print('original Done')

    # Draw plots
    for result in ablation_results:
        result.draw_plot('iteration')
    
    plt.legend(fontsize='small', framealpha=0.5)
    plt.xlabel('Iteration',fontsize=15)
    plt.ylabel('# of Valid Patches',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    if WITH_MOCKITO:
        plt.savefig(f'rq3-{mode}-w-mockito.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-{mode}-w-mockito.jpg',bbox_inches='tight')
    else:
        plt.savefig(f'rq3-{mode}.pdf',bbox_inches='tight')
        plt.savefig(f'rq3-{mode}.jpg',bbox_inches='tight')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])