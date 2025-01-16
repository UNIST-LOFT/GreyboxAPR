import os
import sys
import subprocess


def run(project,mode,target,seed,trial):
    cur_dir=os.getcwd()
    if not cur_dir.endswith('experiments/alpharepair'):
        print('Please run this script in experiments/alpharepair',file=sys.stderr)
        sys.exit(1)

    cur_dirs=cur_dir.split('/')
    new_cur_dir=''
    for dir in cur_dirs[:-2]:
        new_cur_dir+=dir+'/'

    mode_args = None
    if mode == 'vertical':
        mode_args = ['--not-use-guide']
    elif mode == 'horizontal':
        mode_args = ['--not-use-epsilon']

    target_args = None
    if target == 'branch':
        target_args = ['--use-branch']
    elif target == 'field':
        target_args = ['--use-field']
    elif target == 'both':
        target_args = ['--use-branch', '--use-field']
        
    common_args = [*mode_args, *target_args]
    
    if mode_args is not None and target_args is not None:
        print(f"Run {project}-w/o-{mode}-{target}-{trial}")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-wo-{mode}-{target}-{trial}',
                            '-m','greybox','--seed',f'{seed}','-k','learning','-w',f'{new_cur_dir}/AlphaRepair/d4j/{project}',
                            '-t','180000','--use-simulation-mode',f'result/cache/{project}-cache.json','--instr-cp','../../../JPatchInst',
                            '--branch-output',f'result/branch/{project}','--field-output',f'result/field/{project}',
                            '-E','3000','--skip-valid','--optimized-instrumentation',*common_args,
                            '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/AlphaRepair/buggy'])
    
    print(f'{project} ablation-wo-{mode}-{target}-{trial} finish with return code {result.returncode}')
    exit(result.returncode)

if __name__ == '__main__':
    args=sys.argv
    if len(args)!=6:
        print('Usage: python3 search-alpharepair-ablation-greybox.py <project> <vertical|horizontal> <branch|field|both> <seed> <trial>')
        sys.exit(1)
    
    run(args[1],args[2],args[3],args[4],args[5])