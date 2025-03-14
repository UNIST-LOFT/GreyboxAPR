import os
import sys
import subprocess


def run(project,mode,seed,trial):
    cur_dir=os.getcwd()
    if not cur_dir.endswith('experiments/alpharepair'):
        print('Please run this script in experiments/alpharepair',file=sys.stderr)
        sys.exit(1)

    cur_dirs=cur_dir.split('/')
    new_cur_dir=''
    for dir in cur_dirs[:-2]:
        new_cur_dir+=dir+'/'

    if mode=='vertical':
        print(f"Run {project}-w/o-vertical-{trial}")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-wo-vertical-{trial}',
                               '-m','casino','--seed',f'{seed}','-k','learning','--skip-valid',
                               '-w',f'{new_cur_dir}/AlphaRepair/d4j/{project}','-t','180000',
                               '--use-simulation-mode',f'result/cache/{project}-cache.json','-E','3000','--not-use-guide',
                               '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/AlphaRepair/buggy'])
    elif mode=='horizontal':
        print(f"Run {project}-w/o-horizontal-{trial}")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-wo-horizontal-{trial}',
                               '-m','casino','--seed',f'{seed}','-k','learning','--skip-valid',
                               '-w',f'{new_cur_dir}/AlphaRepair/d4j/{project}','-t','180000',
                               '--use-simulation-mode',f'result/cache/{project}-cache.json','-E','3000','--not-use-epsilon',
                               '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/AlphaRepair/buggy'])
    elif mode=='field':
        print(f"Run {project}-fieldonly-{trial}")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-fieldonly-{trial}',
                               '-m','greybox','--seed',f'{seed}','-k','learning','--skip-valid','--use-field',
                               '-w',f'{new_cur_dir}/AlphaRepair/d4j/{project}','-t','180000','--not-use-guide',
                               '--use-simulation-mode',f'result/cache/{project}-cache.json','-E','3000','--not-use-epsilon',
                               '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/AlphaRepair/buggy'])
    
    print(f'{project} ablation-{trial} finish with return code {result.returncode}')
    exit(result.returncode)

if __name__ == '__main__':
    args=sys.argv
    if len(args)!=5:
        print('Usage: python3 search-alpharepair-ablation.py <project> <vertical|horizontal|field> <seed> <trial>')
        sys.exit(1)
    
    run(args[1],args[2],args[3],args[4])